from collections.abc import Generator, Iterator
from xmlrpc import client
from contextlib import contextmanager
from trafilanews.ingestfeed import IngestFeed
import httpx


class TrafilaNews:
        def __init__(self, url: str | str, proxy: str | None = None, timeout: float | None = 10.0, user_agent: str | None = None, playwright: bool = False):
               self.url = url
               self.proxy = proxy
               self.timeout = timeout
               self.headers = {"User-Agent": user_agent} if user_agent else None
               self.playwright = playwright

        @contextmanager
        def _httpx_client(self):
                client = httpx.Client(proxy=self.proxy, timeout=self.timeout, headers=self.headers)
                yield client
                client.close()

        @contextmanager
        def _playwright_browser(self):
                if not self.playwright:
                        yield None

                from playwright.sync_api import sync_playwright
                p = sync_playwright().start()
                browser = p.chromium.launch()
                yield browser
                browser.close()

        def ingest_feed(self, url: str) -> Generator[str, None, None]:
              with self._playwright_browser() as browser, self._httpx_client() as client:
                    for i in IngestFeed(self.url, browser=browser, client=client).stream_articles():
                        yield i    

        def ingest_feeds(self, urls: list[str]) -> Generator[str, None, None]:
              with self._playwright_browser() as browser, self._httpx_client() as client:
                    for url in urls:
                        ingest_feed = IngestFeed(url, browser=browser, client=client)
                        for i in ingest_feed.stream_articles():
                            yield i


if __name__ == "__main__":
        google_rss_url = "https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q=Iran"
        bbc_rss_url = "https://feeds.bbci.co.uk/news/rss.xml"
        
        trafilanews = TrafilaNews(google_rss_url, playwright=True)
        ingest_feed = trafilanews.ingest_feed(google_rss_url)
        for i in ingest_feed:
            print(i)
              
                    


