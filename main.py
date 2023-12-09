from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from scrappers import NewsRBCScrapper
from scrappers import CyberScrapper
import uvicorn


app = FastAPI()

PERIOD = 6 * 60 * 60  # 3 times a day
TEST = 60


def getting_news_urls():
    news = NewsRBCScrapper()
    news.get_urls()
    news.collect()


def getting_papers():
    run = CyberScrapper()
    run.collect()


def test():
    news = NewsRBCScrapper()
    news.test_logs()


@app.get("/")
@repeat_every(seconds=TEST)
def r_task() -> None:
    print(1)
    test()
    print(3)


if __name__ == "__main__":
    uvicorn.run(app)
