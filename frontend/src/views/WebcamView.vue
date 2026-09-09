<script setup>
import {
  onBeforeUnmount,
  ref
} from "vue";

import api
  from "../services/api";


const cameraRunning =
  ref(false);

const cameraStatus =
  ref("Stopped");

const statusMessage =
  ref(
    "Camera is currently stopped."
  );

const streamKey =
  ref(0);


const webcamStats = ref({
  persons: 0,
  total_seats: 0,
  occupied: 0,
  empty: 0,
  occupancy_rate: 0,
  fps: 0
});


let statusTimer = null;


const loadWebcamStatus =
  async () => {

    try {
      const response =
        await api.get(
          "/api/webcam/status"
        );

      webcamStats.value =
        response.data;

    } catch (error) {
      console.error(
        "WEBCAM STATUS ERROR:",
        error
      );
    }
  };


const startStatusPolling = () => {
  stopStatusPolling();

  loadWebcamStatus();

  statusTimer = setInterval(
    loadWebcamStatus,
    700
  );
};


const stopStatusPolling = () => {
  if (statusTimer) {
    clearInterval(
      statusTimer
    );

    statusTimer = null;
  }
};


const startCamera = async () => {
  try {
    cameraStatus.value =
      "Starting...";

    statusMessage.value =
      "Opening webcam...";


    await api.post(
      "/api/webcam/start"
    );


    streamKey.value++;

    cameraRunning.value =
      true;

    cameraStatus.value =
      "Running";

    statusMessage.value =
      "Webcam is active and analyzing seats.";


    startStatusPolling();

  } catch (error) {
    cameraRunning.value =
      false;

    cameraStatus.value =
      "Error";

    statusMessage.value =
      error.response?.data?.message
      || "Could not start webcam.";

    console.error(
      "START WEBCAM ERROR:",
      error
    );
  }
};


const stopCamera = async () => {
  try {
    cameraStatus.value =
      "Stopping...";

    statusMessage.value =
      "Stopping webcam and saving result...";


    const response =
      await api.post(
        "/api/webcam/stop"
      );


    cameraRunning.value =
      false;

    stopStatusPolling();


    cameraStatus.value =
      "Stopped";

    statusMessage.value =
      response.data.message
      || "Webcam stopped.";


    await loadWebcamStatus();

  } catch (error) {
    cameraStatus.value =
      "Error";

    statusMessage.value =
      error.response?.data?.message
      || "Could not stop webcam.";

    console.error(
      "STOP WEBCAM ERROR:",
      error
    );
  }
};


onBeforeUnmount(() => {
  stopStatusPolling();
});
</script>


<template>
  <section>

    <h1 class="page-title">
      Live Camera
    </h1>

    <p class="page-subtitle">
      Realtime classroom
      seat detection.
    </p>


    <div class="panel">

      <!-- ====================== -->
      <!-- STATUS -->
      <!-- ====================== -->

      <div
        class="camera-status-card"
      >

        <div class="camera-status-row">

          <strong>
            Camera Status
          </strong>

          <span
            class="status-badge"
            :class="{
              running:
                cameraStatus
                === 'Running',

              stopped:
                cameraStatus
                === 'Stopped',

              error:
                cameraStatus
                === 'Error'
            }"
          >
            {{ cameraStatus }}
          </span>

        </div>


        <p>
          {{ statusMessage }}
        </p>

      </div>


      <!-- ====================== -->
      <!-- BUTTON -->
      <!-- ====================== -->

      <button
        class="primary-btn"
        :disabled="cameraRunning"
        @click="startCamera"
      >
        Start Camera
      </button>


      <button
        class="secondary-btn"
        :disabled="!cameraRunning"
        @click="stopCamera"
      >
        Stop Camera
      </button>


      <!-- ====================== -->
      <!-- STREAM -->
      <!-- ====================== -->

      <div
        v-if="cameraRunning"
        class="camera-container"
      >

        <h4>
          Live Detection
        </h4>

        <img
          :key="streamKey"
          :src="
            '/video_feed?t='
            + streamKey
          "
          class="camera-feed"
          alt="Live webcam"
        >

      </div>


      <div
        v-else
        class="camera-placeholder"
      >

        Camera preview will
        appear here after
        pressing Start Camera.

      </div>

    </div>


    <!-- ====================== -->
    <!-- REALTIME STATISTICS -->
    <!-- ====================== -->

    <div class="panel">

      <h3>
        Realtime Statistics
      </h3>


      <div class="result-summary">

        <div class="result-item">

          <span>
            Persons
          </span>

          <strong>
            {{ webcamStats.persons }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Total Seats
          </span>

          <strong>
            {{ webcamStats.total_seats }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Occupied
          </span>

          <strong>
            {{ webcamStats.occupied }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Empty
          </span>

          <strong>
            {{ webcamStats.empty }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Occupancy Rate
          </span>

          <strong>
            {{
              Number(
                webcamStats.occupancy_rate
                || 0
              ).toFixed(1)
            }}%
          </strong>

        </div>


        <div class="result-item">

          <span>
            FPS
          </span>

          <strong>
            {{
              Number(
                webcamStats.fps
                || 0
              ).toFixed(1)
            }}
          </strong>

        </div>

      </div>

    </div>

  </section>
</template>
<style>
/* ============================= */
/* WEBCAM VIEW */
/* ============================= */

.camera-status-card {
  margin-bottom: 22px;

  padding: 16px 18px;

  background: #f8fafc;

  border: 1px solid #e5e7eb;

  border-radius: 12px;
}

.camera-status-row {
  display: flex;

  align-items: center;

  gap: 12px;

  margin-bottom: 8px;
}

.camera-status-card p {
  margin: 0;

  color: #6b7280;
}

.status-badge {
  display: inline-block;

  padding: 5px 11px;

  border-radius: 999px;

  font-size: 13px;

  font-weight: 600;
}

.status-badge.running {
  background: #dcfce7;

  color: #166534;
}

.status-badge.stopped {
  background: #e5e7eb;

  color: #374151;
}

.status-badge.error {
  background: #fee2e2;

  color: #991b1b;
}

.secondary-btn {
  margin-left: 10px;

  background: #e5e7eb;

  color: #111827;
}

.secondary-btn:hover {
  background: #d1d5db;
}

.primary-btn:disabled,
.secondary-btn:disabled {
  cursor: not-allowed;

  opacity: 0.55;
}

.camera-container {
  margin-top: 25px;
}

.camera-container h4 {
  margin-bottom: 12px;
}

.camera-feed {
  display: block;

  width: 100%;
  max-width: 1100px;
  max-height: 700px;

  object-fit: contain;

  border-radius: 12px;

  background: #000;
}

.camera-placeholder {
  margin-top: 22px;

  padding: 70px 25px;

  text-align: center;

  color: #6b7280;

  background: #f3f4f6;

  border: 1px dashed #cbd5e1;

  border-radius: 12px;
}
</style>