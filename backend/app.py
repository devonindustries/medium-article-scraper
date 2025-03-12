from flask import Flask, request, jsonify
from scripts.db import SessionLocal, wait_for_mysql
from scripts.models import Article
from scripts.scraper import scrape_medium

# Step 1: Create the Flask app
app = Flask(__name__)

# Step 2: Wait for MySQL to be ready before starting
wait_for_mysql()

@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape Medium and save articles to MySQL."""
    session = SessionLocal()
    try:
        data = request.get_json()
        tag = data.get("tag", "future/recommended")
        scroll_depth = int(data.get("scroll_depth", 5))

        articles = scrape_medium(tag, scroll_depth)

        # Save articles manually
        for article in articles:
            existing_article = session.query(Article).filter_by(link=article["link"]).first()
            if not existing_article:
                new_article = Article(title=article["title"], link=article["link"], tag=tag)
                session.add(new_article)

        session.commit()
        return jsonify({"message": "Scraping complete", "articles_scraped": len(articles)})

    except Exception as e:
        session.rollback()
        print(f"Error in /scrape: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

@app.route('/articles', methods=['GET'])
def get_articles():
    """Retrieve saved articles."""
    session = SessionLocal()
    try:
        articles = session.query(Article).order_by(Article.scraped_at.desc()).all()
        return jsonify([article.to_dict() for article in articles])

    except Exception as e:
        print(f"Error in /articles: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Starting Flask server on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=True)