from fastapi import FastAPI
from pydantic import HttpUrl

app = FastAPI()


@app.post("/")
def parse_url(url: HttpUrl):
    ...  # TODO: implement browser logic
