<script setup>
import {
  onMounted,
  ref
} from "vue";

import api
  from "../services/api";

const stats = ref({
  total_seats: 0,
  occupied_seats: 0,
  empty_seats: 0,
  occupancy_rate: 0
});

const loadStatistics = async () => {

  try {

    const response = await api.get(
      "/api/statistics"
    );

    stats.value = response.data;

  } catch (error) {

    console.error(
      "Không thể tải statistics:",
      error
    );

  }
};

onMounted(
  loadStatistics
);
</script>


<template>

  <section>

    <h1 class="page-title">
      Classroom Seat Detection
    </h1>

    <p class="page-subtitle">
      AI-powered classroom occupancy monitoring
    </p>


    <div class="stat-grid">

      <div class="stat-card">

        <span>
          Total Seats
        </span>

        <h2>
          {{ stats.total_seats }}
        </h2>

      </div>


      <div class="stat-card">

        <span>
          Occupied
        </span>

        <h2>
          {{ stats.occupied_seats }}
        </h2>

      </div>


      <div class="stat-card">

        <span>
          Empty
        </span>

        <h2>
          {{ stats.empty_seats }}
        </h2>

      </div>


      <div class="stat-card">

        <span>
          Occupancy Rate
        </span>

        <h2>
          {{ stats.occupancy_rate }}%
        </h2>

      </div>

    </div>


    <div class="panel">

      <h3>
        System Status
      </h3>

      <p>
        Backend:
        Connected
      </p>

      <p>
        YOLO:
        Ready
      </p>

    </div>

  </section>

</template>