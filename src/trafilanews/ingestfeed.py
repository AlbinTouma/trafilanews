from operator import contains
from trafilanews.utils import decode_rss_links, parse_rss_feed, parse_article, fetch_article 
import httpx
from collections.abc import Generator, Iterator

class IngestFeed():

    def __init__(
            self,
            url: str,
            client: httpx.Client | None = None,
            browser: object | None = None
            ):

            self.rss_url = url
            self.browser = browser 
            self.client = client


    def fetch_article(self, url: str) -> str | None:
        if "news.google.com/rss" in url:
            decoded_url = decode_rss_links(url)
        else:
            decoded_url = url
        article = fetch_article(decoded_url, self.client, self.browser)
        return article

    def stream_articles(self) -> Generator[str, None, None]:
        response = self.client.get(self.rss_url)
        response.raise_for_status()
        rss_feed = parse_rss_feed(response)

        for url in rss_feed:
            if contains(self.rss_url, "news.google.com/rss"):
                url = decode_rss_links(url)

            article = fetch_article(url, self.client, self.browser)
            if not article:
                continue

            content_json = parse_article(article)
            if content_json is None:
                continue

            yield content_json

    def fetch_all(self) -> list[str]:
        return list(self.stream_articles())


if __name__ =="__main__":

    google_rss_url ="https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q=Iran"
    bbc_rss_url = "https://feeds.bbci.co.uk/news/rss.xml"

    rss = trafilanews(google_rss_url, use_playwright=True)
    feed = rss.stream_articles()
    for i in feed:
        print(i)
