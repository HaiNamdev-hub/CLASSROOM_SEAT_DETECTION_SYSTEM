import {
  createRouter,
  createWebHistory
} from "vue-router";

import DashboardView
  from "../views/DashboardView.vue";

import ImageView
  from "../views/ImageView.vue";

import VideoView
  from "../views/VideoView.vue";

import WebcamView
  from "../views/WebcamView.vue";

import HistoryView
  from "../views/HistoryView.vue";

const routes = [
  {
    path: "/",
    component: DashboardView
  },
  {
    path: "/image",
    component: ImageView
  },
  {
    path: "/video",
    component: VideoView
  },
  {
    path: "/webcam",
    component: WebcamView
  },
  {
    path: "/history",
    component: HistoryView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;