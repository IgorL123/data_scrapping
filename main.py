from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from scrappers import NewsRBCScrapper
from scrappers import CyberScrapper

app = FastAPI()

PERIOD = 6 * 60 * 60  # 3 times a day


@app.get("/")
def read_root():
    return {"Hello": "World"}


def getting_news_urls():
    news = NewsRBCScrapper()
    news.get_urls()
    news.collect()


def getting_papers():
    run = CyberScrapper()
    run.collect()


@app.on_event("startup")
@repeat_every(seconds=PERIOD)
def r_task() -> None:
    print(1)
    getting_news_urls()
    print(2)
    getting_papers()
    print(3)

