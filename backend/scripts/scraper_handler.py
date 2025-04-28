import time
import asyncio

from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class ScraperHandler:
    """
    An engine used for scraping Medium data and handling ClickHouse transactions via Spark.

    Must be initialised with a DataHandler instance!
    """

    def __init__(
        self,
        data_handler = None,
    ):
        
        # TODO: Add database support later
        self.data_handler = data_handler
        # self.data_handler.initialiseClickHouseConnection()


    # Private Functions
    # -----------------

    @staticmethod
    def __cc_to_int(
        value
    ):
        """Convert a string with K or M suffix to an integer."""

        value = str(value)

        if value.endswith('K'):
            return int(float(value[:-1]) * 1e3)
        elif value.endswith('M'):
            return int(float(value[:-1]) * 1e6)
        else:
            return int(value)


    @staticmethod
    def __age_to_datetime(
        value
    ):

        # Cover all bases (probably a better way to do this)
        if 'd ago' in value:
            value = int(value.split('d ago')[0].strip())
            return datetime.today() - timedelta(days=value)

        elif 'h ago' in value:
            value = int(value.split('h ago')[0].strip())
            return datetime.today() - timedelta(hours=value)
        
        elif 'm ago' in value:
            value = int(value.split('m ago')[0].strip())
            return datetime.today() - timedelta(minutes=value)
        
        elif 's ago' in value:
            value = int(value.split('s ago')[0].strip())
            return datetime.today() - timedelta(seconds=value)

        else:

            if ',' in value:
                return datetime.strptime(value, '%b %d, %Y')
            else:
                new_date = datetime.strptime(value, '%b %d')
                return datetime(
                    year=datetime.today().year,
                    month=new_date.month,
                    day=new_date.day,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )


    @staticmethod
    def __htmlToJson(
        html : str,
        tag : str,
    ):
        """
        Extracts the articles from the HTML content and returns them as a list of dictionaries.
        """

        article_container = BeautifulSoup(html, "html.parser")
        articles = []

        if article_container:

            for article in article_container.find_all("article"):

                title = article.find("h2").text.strip() if article.find("h2") else "No Title"
                link = list(article.find("div", class_="bh l").children)[0]["data-href"] if article.find("div", class_="bh l") else "No Link"
                paywall = True if article.find("button", class_="l ay ap an") else False

                author_obj = article.find("div", class_="ab")
                author = " ".join([x.text.strip() for x in author_obj.find_all("p")]) if author_obj else "No Author"

                images = [img["src"] for img in article.find_all("img")]
                profile_image = images[0] if len(images) > 0 else "No Image"
                article_image = images[2] if len(images) > 2 else "No Other Image"

                objs = [x.text.strip() for x in article.find("div", class_="h k").find_all("span")]

                obj_length = len(objs[:-1])
                article_age = objs[0]

                claps = 0
                comments = 0

                # If 'ago' is in the first element, the list is at most 3 elements long
                # Else, the list is longer

                if 'ago' in objs[0]:
                    if obj_length > 2:
                        claps = objs[1]
                        comments = objs[2]
                    elif obj_length == 2:
                        claps = objs[1]

                else:
                    article_age = objs[1]
                    claps = objs[2] if obj_length >= 3 else 0
                    comments = objs[3] if obj_length >= 4 else 0

                articles.append({
                    "title" : title, 
                    "link" : link,
                    "paywall" : paywall,
                    "published_date" : str(ScraperHandler.__age_to_datetime(article_age)),
                    "claps" : ScraperHandler.__cc_to_int(claps),
                    "comments" : ScraperHandler.__cc_to_int(comments),
                    "topic_name" : tag.split("/")[0],
                    "topic_type" : tag.split("/")[1],
                    "tag" : tag,
                    "profile_image" : profile_image,
                    "article_image" : article_image,
                    "author" : author,
                    # "version" : int(time.time()), # Used for CH Database versioning
                    # "objs" : objs,
                })

        return articles


    # Entry Function
    # --------------


    async def scrape_medium(
        self,
        tag, # Example: "future/recommended" 
        scroll_depth,
        scroll_delay=1.5,
        cloudfare_delay=5,
    ):
        """
        Run Playwright headless browser to scrape Medium.
        """

        # articles = []

        print(f"Scraping tag: {tag}")

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            url = f"https://medium.com/tag/{tag}"
            await page.goto(url, timeout=60000)
            await asyncio.sleep(cloudfare_delay)  # Allow time for Cloudflare to clear

            # Simulate scrolling
            for _ in range(scroll_depth):
                
                # Scroll to the bottom of the page, and wait for it to load
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(scroll_delay)

                # Ingest into clickhouse as data become available
                html = await page.content()

                articles = ScraperHandler.__htmlToJson(html, tag)
                
                for article in articles: yield article
        
            # Close the browser on finish
            await browser.close()
        
        # TODO: Add database support later
        # self.data_handler.writeToClickhouse(articles)
        # yield articles