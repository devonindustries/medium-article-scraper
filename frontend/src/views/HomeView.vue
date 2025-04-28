<template>
  <div class="d-flex justify-content-center align-items-center vh-100 position-relative bg-light">
    <div class="input-group search-box">
      <input
        v-model="genre"
        @keyup.enter="searchGenre"
        :placeholder="`Search articles in ${rotatingSuggestion}`"
        class="form-control rounded-start shadow-sm"
      />
      <button class="btn btn-outline-secondary rounded-end shadow-sm" @click="searchGenre">
        <i class="bi bi-search"></i>
      </button>
    </div>
    <div class="bubble-container position-absolute w-100 h-100 overflow-hidden">
      <div
        v-for="bubble in bubbles"
        :key="bubble.id"
        class="bubble shadow-sm"
        @click="selectGenre(bubble.genre.replace(' ', '-'))"
        :style="bubble.style"
      >
        {{ bubble.genre }}
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      genre: '',
      suggestions: [],
      rotatingSuggestion: 'science',
      bubbles: [],
      isSpawningBubbles: true,
      active: true,
    };
  },
  methods: {
    async fetchSuggestions() {
      const res = await api.getSuggestions();
      this.suggestions = res;
    },
    rotateSuggestion() {
      setInterval(() => {
        const random = this.suggestions[Math.floor(Math.random() * this.suggestions.length)];
        this.rotatingSuggestion = random;
      }, 3000);
    },
    spawnBubbles() {
      setInterval(() => {
        if (!this.suggestions.length) return;

        const suggestion = this.suggestions[Math.floor(Math.random() * this.suggestions.length)];
        const top = 10 + Math.random() * 80;
        const left = 10 + Math.random() * 80;
        const duration = 6 + Math.random() * 2;
        const delay = Math.random(); // up to 1s delay before starting animation

        const bubble = {
          id: Date.now(),
          genre: suggestion,
          style: {
            top: `${top}%`,
            left: `${left}%`,
            animation: `fadeInOut ${duration}s ease-in-out forwards, floatAround ${duration}s ease-in-out forwards`,
            animationDelay: `${delay}s`,
          }
        };

        this.bubbles.push(bubble);

        setTimeout(() => {
          const index = this.bubbles.findIndex(b => b.id === bubble.id);
          if (index !== -1) this.bubbles.splice(index, 1);
        }, (duration + delay) * 1000);
      }, 1000);
    },
    searchGenre() {
      if (this.genre.trim()) {
        this.$router.push({ name: 'Articles', params: { genre: this.genre.trim().replace(' ', '-') } });
      }
    },
    selectGenre(genre) {
      this.$router.push({ name: 'Articles', params: { genre } });
    }
  },
  async mounted() {
    await this.fetchSuggestions();
    this.rotateSuggestion();

    this.isSpawningBubbles = true;
    this.spawnBubbles();
  },
  beforeUnmount() {
    this.isSpawningBubbles = false;
    this.bubbles = [];
  },
};
</script>

<style>
.search-box {
    width: 60%;
    max-width: 600px;
    z-index: 10;
}

input.form-control {
    border-top-left-radius: 25px !important;
    border-bottom-left-radius: 25px !important;
    height: 45px;
}

button.btn {
    border-top-right-radius: 25px !important;
    border-bottom-right-radius: 25px !important;
    height: 45px;
    background-color: #e9ecef;
    border-color: #ced4da;
    color: #495057;
}

.bubble-container {
    pointer-events: none;
    z-index: 1;
}

.bubble {
  pointer-events: auto;
  position: absolute;
  white-space: nowrap;
  font-size: 0.9rem;
  transition: transform 0.3s;
  background-color: white;
  padding: 8px 14px;
  border-radius: 20px;
  cursor: pointer;
  transform: translate(-50%, -50%);
  opacity: 0;
}

.bubble:hover {
  background-color: lightgray;
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

@keyframes floatAround {
  0% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -48%) scale(1.05);
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>