import suggestions from '../data/suggestions.json';

const API_BASE = process.env.VUE_APP_API_URL;

export default {
  async streamArticles(genre, type = 'recommended', onMessage, onDone) {
    
    // TODO: Delete this when things are working!
    console.log('Streaming from URL: ' + `${API_BASE}/stream_feed?genre=${encodeURIComponent(genre)}&type=${encodeURIComponent(type)}`);
    
    // Step 1: Trigger the scraper on the backend via POST
    await fetch(`${API_BASE}/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ genre, type })
    });

    // Step 2: Connect to SSE stream
    const url = `${API_BASE}/stream_feed?genre=${encodeURIComponent(genre)}&type=${encodeURIComponent(type)}`;
    const source = new EventSource(url);

    source.onmessage = event => {
      const article = JSON.parse(event.data);
      onMessage(article);
    };

    source.onerror = err => {
      console.error('SSE stream error:', err);
      source.close();
      if (onDone) onDone();
    };

    return source;
  },

  getSuggestions() {
    return suggestions;
  }
};