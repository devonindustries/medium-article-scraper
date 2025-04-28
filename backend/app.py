import json
import asyncio
import threading
import queue

from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS, cross_origin

from scripts.scraper_handler import ScraperHandler
# from scripts.data_handler import DataHandler

active_scrapers = set()
# dh = DataHandler()
sh = ScraperHandler() # TODO: Initialise with DataHandler

# App + CORS
app = Flask(__name__)

CORS(
    app,
    resources={r"/api/*": {"origins": "https://mediumrare.fly.dev"}},
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
)

# @app.after_request
# def add_cors_headers(response):
#     response.headers['Access-Control-Allow-Origin'] = 'https://mediumrare.fly.dev'
#     response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
#     return response

# ROUTES
# ------

stream_queues = {}

@app.route('/api/stream', methods=['POST'])
@cross_origin()
def start_scraping():

    genre = request.json.get('genre')
    type_ = request.json.get('type')
    tag = f"{genre}/{type_}"

    if tag in stream_queues:
        return {"message": "Scraper already running."}, 200

    q = queue.Queue()
    stream_queues[tag] = q

    def run_scraper(q, tag):
        async def async_scrape():
            if tag in active_scrapers:
                app.logger.info(f"Already scraping tag: {tag}")
                return

            active_scrapers.add(tag)
            app.logger.info(f"Started scraping tag: {tag}")

            try:
                async for article in sh.scrape_medium(tag, 25):
                    # app.logger.info(f"Scraped article: {article['title']}")
                    q.put(article)
            finally:
                app.logger.info(f"Scraping done for: {tag}")
                active_scrapers.discard(tag)
                q.put(None)  # signal to stop generator

        asyncio.run(async_scrape())

    threading.Thread(target=run_scraper, args=(q, tag), daemon=True).start()
    return {"message": "Scraper started"}, 200


@app.route('/api/stream_feed', methods=['GET', 'OPTIONS'])
@cross_origin()
def stream_feed():

    if request.method == "OPTIONS":
        # Handle CORS preflight
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "https://mediumrare.fly.dev")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response, 200

    genre = request.args.get('genre')
    type_ = request.args.get('type')
    tag = f"{genre}/{type_}"

    q = stream_queues.get(tag)
    if not q:
        return {"error": "No stream found for that tag"}, 404

    def stream():
        while True:
            item = q.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return Response(stream_with_context(stream()), mimetype='text/event-stream')


# APP START
# ----------

if __name__ == '__main__':
    
    # NOTE: Do NOT use the default Flask server in production!!!
    # Another NOTE: You could write an article on this topic :D
    app.run(host='0.0.0.0', port=5050, debug=True)