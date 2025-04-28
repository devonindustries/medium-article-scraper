import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/HomeView.vue';
import Articles from '../views/ArticleView.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/articles/:genre', name: 'Articles', component: Articles, props: true }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;