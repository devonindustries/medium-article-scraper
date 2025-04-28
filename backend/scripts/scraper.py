import asyncio

from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def cc_to_int(value):
    """Convert a string with K or M suffix to an integer."""

    value = str(value)

    if value.endswith('K'):
        return int(float(value[:-1]) * 1e3)
    elif value.endswith('M'):
        return int(float(value[:-1]) * 1e6)
    else:
        return int(value)


def age_to_datetime(value):

    if 'd ago' in value:
        value = int(value.replace('d ago', '').strip())
        return datetime.today() - timedelta(days=value)
    
    else:

        # Check for something of the form
        # - MMM DD
        # - MMM DD, YYYY

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



async def scrape(tag, scroll_depth):
    """Run Playwright headless browser to scrape Medium."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = f"https://medium.com/tag/{tag}"
        await page.goto(url, timeout=60000)
        await asyncio.sleep(5)  # Allow time for Cloudflare to clear

        # Simulate scrolling
        for _ in range(scroll_depth):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        # Ingest into clickhouse as data become available

        html = await page.content()
        await browser.close()
        return html
    

def scrape_medium(tag="future/recommended", scroll_depth=5):
    """Wrapper to run Playwright synchronously."""
    html = asyncio.run(scrape(tag, scroll_depth))
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract articles
    articles = []
    article_container = soup.find("div", class_="eb gc ec eo ed gd ee eq ef ge eg es eh gf ei gg ej gh ek gi l")
    if article_container:
        for article in article_container.find_all("article"):

            title = article.find("h2").text.strip() if article.find("h2") else "No Title"
            link = list(article.find("div", class_="bh l").children)[0]["data-href"] if article.find("div", class_="bh l") else "No Link"
            paywall = True if article.find("button", class_="l ay ap an") else False

            objs = [x.text.strip() for x in article.find("div", class_="h k").find_all("span")]

            # Pop items from the list and append the last items to claps and comments
            article_age = ""
            if len(objs) > 2 and objs[1:]:
                separator = ''.join(objs[1:])
                article_age = objs[0].split(separator)[0]
                article_age = objs[1] if article_age=='' else article_age
            elif len(objs) == 2:
                article_age = objs[0]

            claps = objs[-3] if len(objs) > 3 else objs[-2]
            comments = objs[-2] if len(objs) > 3 else 0

            articles.append({
                "title" : title, 
                "link" : link,
                "paywall" : paywall,
                "published_date" : age_to_datetime(article_age),
                "claps" : cc_to_int(claps),
                "comments" : cc_to_int(comments),
                "topic_name" : tag.split("/")[0],
                "topic_type" : tag.split("/")[1],
                # "objs" : objs,
            })

    return articles

if __name__=='__main__':
    print(scrape_medium(scroll_depth=1))