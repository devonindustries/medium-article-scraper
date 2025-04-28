<template>
  <div class="container mt-5">
    <h2>Articles in <b>{{ displayGenre }}</b></h2>
    <div v-if="loading" class="text-center my-5">Loading...</div>
    <ul class="list-group" v-else>
      <li v-for="article in displayedArticles" :key="article.id" class="list-group-item article-card mb-3 shadow-sm" @click="goToArticle(article)">
        <div class="row g-0 align-items-center">
          <!-- Left side: Image -->
          <div class="col-3">
            <img
              :src="article.article_image"
              alt="Article Image"
              class="img-fluid rounded-start h-100 w-100 object-fit-cover"
            />
          </div>

          <!-- Right side: Article details -->
          <div class="col-9 d-flex flex-column justify-content-center px-3">
            <!-- Title -->
            <h5 class="mb-2">{{ article.title }}</h5>

            <!-- Claps, Comments, Date, Author -->
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex flex-column">
                <div class="d-flex align-items-center mb-1">
                  <small class="mr-3">
                    <i class="bi bi-hand-thumbs-up mr-1"></i> {{ article.claps }}
                  </small>
                  <small class="mr-3">
                    <i class="bi bi-chat mr-1"></i> {{ article.comments }}
                  </small>
                  <small>{{ formatDate(article.published_date) }}</small>
                </div>
              </div>

              <div class="d-flex align-items-center">
                <small>{{ article.author }}</small>
                <img
                  :src="article.profile_image"
                  alt="Profile Image"
                  class="rounded-circle ml-2"
                  style="width: 30px; height: 30px;"
                />
              </div>
            </div>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>
  

<script>
import api from '../services/api';

export default {
  data() {
    return {
      // Articles data
      articles: [],
      freeArticles: [],
      loading: true,
      streamSource: null,

      // Page limiting
      displayedArticles: [],
      articlesPerPage: 8,
      currentPage: 1,

      // Genre from route
      genre: this.$route.params.genre,
    };
  },
  watch: {
    articles: {
      handler(newArticles) {
        this.freeArticles = newArticles.filter(article => article.paywall === false);
      },
      deep: true,
      immediate: true
    }
  },
  computed: {
    displayGenre() {
      return this.$route.params.genre.replace('-', ' ');
    }
  },
  methods: {

    // Streaming articles
    async startStreaming() {
      if (this.streamSource) {
        this.streamSource.close(); // Close previous stream if open
      }

      console.log("streaming from: ", this.genre);

      this.streamSource = await api.streamArticles(
        this.genre,
        'recommended',
        (article) => {
          if (this.loading) {
            this.loading = false;
          }
          this.articles.push(article);

          // Deduplicate based on title
          this.articles = [...new Map(this.articles.map(a => [a.title, a])).values()];

          // Update displayed list after adding new articles
          this.updateDisplayedArticles();
        },
        () => {
          console.log('Stream ended or errored.');
        }
      );
    },

    // Navigation
    goToArticle(article) {
      window.open(article.link, '_blank');
    },

    // Date formatting
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },

    // Scroll handling
    updateDisplayedArticles() {
      const end = this.currentPage * this.articlesPerPage;
      this.displayedArticles = this.freeArticles.slice(0, end);
    },
    handleScroll() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const fullHeight = document.documentElement.offsetHeight;

      if (scrollTop + windowHeight >= fullHeight - 100) {
        this.currentPage++;
        this.updateDisplayedArticles();
      }
    },
  },
  async mounted() {
    await this.startStreaming();
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeUnmount() {
    if (this.streamSource) this.streamSource.close();
    window.removeEventListener('scroll', this.handleScroll);
  }
};
</script>


<style scoped>
.article-card {
  transition: transform 0.2s ease-in-out;
  cursor: pointer;
}

.article-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.object-fit-cover {
  object-fit: cover;
}
</style>