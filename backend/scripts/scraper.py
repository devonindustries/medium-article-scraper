import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

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

        html = await page.content()
        await browser.close()
        return html

def scrape_medium(tag="future/recommended", scroll_depth=5):
    """Wrapper to run Playwright synchronously."""
    html = asyncio.run(scrape(tag, scroll_depth))
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract articles
    articles = []
    article_container = soup.find("div", class_="cq et cr dc cs eu ct de cu ev cv dg cw ew cx ex cy ey cz ez l")
    if article_container:
        for article in article_container.find_all("article"):

            title = article.find("h2").text.strip() if article.find("h2") else "No Title"
            link = list(article.find("div", class_="bh l").children)[0]["data-href"] if article.find("div", class_="bh l") else "No Link"
            paywall = True if article.find("button", class_="l ay ao am") else False

            objs = [x.text.strip() for x in article.find("div", class_="h k").find_all("span")]
            # objs = article.find("div", class_="h k").find("span").text.strip()

            # TODO: Pop items from the list and append the last items to claps and comments
            article_age = ""
            if len(objs) > 2 and objs[1:]:
                separator = ''.join(objs[1:])
                article_age = objs[0].split(separator)[0]
                article_age = objs[1] if article_age=='' else article_age
            elif len(objs) == 2:
                article_age = objs[0]

            claps = ""
            comments = ""

            articles.append({
                "title" : title, 
                "link" : link,
                "paywall" : paywall,
                "article_age" : article_age,
                "claps" : claps,
                "comments" : comments,
                "objs" : objs,
            })

    return articles

if __name__=='__main__':
    print(scrape_medium(scroll_depth=1))