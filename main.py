import asyncio
from contextlib import asynccontextmanager
from os import environ

import docker
from fastapi import Body, FastAPI, Request, HTTPException, Depends
from pydantic import HttpUrl
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Browser

BROWSER_IMAGE = "cloakhq/cloakbrowser:latest"
BROWSER_NETWORK = environ.get("BROWSER_NETWORK", "cloak_net")
CDP_PORT = 9222
CONNECT_RETRIES = 20
CONNECT_DELAY = 2


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Spawn a CloakBrowser container via the Docker SDK and connect to it over CDP.

    The app owns the container's whole lifecycle: it starts one on app boot, connects
    Playwright over CDP, stores driver+browser on app state for the request handler, and
    tears all three down on shutdown. Requires the Docker socket mounted into this
    container (see docker-compose.yml).
    """
    docker_client = docker.from_env()
    # seccomp=unconfined lets chromium use its sandbox; the container joins BROWSER_NETWORK
    # so this app can reach it by its docker-assigned name via that network's DNS.
    container = docker_client.containers.run(
        BROWSER_IMAGE,
        command="cloakserve",
        detach=True,
        security_opt=["seccomp=unconfined"],
        network=BROWSER_NETWORK,
    )
    container.reload()

    cdp_url = f"http://{container.name}:{CDP_PORT}"
    playwright_driver = await async_playwright().start()

    # The container is up but cloakserve needs a moment before CDP accepts connections;
    # poll until it does or the retry budget is exhausted.
    browser = None
    for _ in range(CONNECT_RETRIES):
        try:
            browser = await playwright_driver.chromium.connect_over_cdp(cdp_url)
            break
        except Exception:
            await asyncio.sleep(CONNECT_DELAY)

    # Never came up: don't leak the driver or the container before failing boot.
    if browser is None:
        await playwright_driver.stop()
        container.remove(force=True)
        raise RuntimeError(f"CloakBrowser at {cdp_url} not ready")

    fastapi_app.state.playwright_driver = playwright_driver
    fastapi_app.state.browser = browser

    yield

    await browser.close()
    await playwright_driver.stop()
    container.remove(force=True)


app = FastAPI(lifespan=lifespan)


def get_browser(request: Request) -> Browser:
    return request.app.state.browser


@app.post("/")
async def parse_url(
    url: HttpUrl = Body(),
    browser: Browser = Depends(get_browser)
) -> str:
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(str(url), timeout=15000)
        html = await page.content()
        return html
    except PlaywrightTimeoutError:
        raise HTTPException(status_code=504, detail="Website timeout")
    finally:
        await context.close()
