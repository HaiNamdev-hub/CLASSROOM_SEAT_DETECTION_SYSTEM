<script setup>
import {
  onBeforeUnmount,
  ref
} from "vue";

import api
  from "../services/api";


const selectedFile = ref(null);

const previewUrl = ref(null);

const loading = ref(false);

const progress = ref(0);

const status = ref("");

const result = ref(null);

const errorMessage = ref("");


const handleFile = event => {
  const file = event.target.files[0];

  selectedFile.value = file;

  result.value = null;
  errorMessage.value = "";
  progress.value = 0;
  status.value = "";

  if (previewUrl.value) {
    URL.revokeObjectURL(
      previewUrl.value
    );
  }

  if (file) {
    previewUrl.value =
      URL.createObjectURL(file);
  } else {
    previewUrl.value = null;
  }
};


const sleep = ms => {
  return new Promise(
    resolve =>
      setTimeout(
        resolve,
        ms
      )
  );
};


const pollProgress = async jobId => {
  while (true) {
    const response =
      await api.get(
        `/api/analyze/video/progress/${jobId}`
      );

    const job =
      response.data;

    progress.value =
      Math.round(
        job.progress || 0
      );

    status.value =
      job.status || "";

    if (
      job.status === "completed"
    ) {
      result.value = job;

      loading.value = false;

      return;
    }

    if (
      job.status === "failed"
    ) {
      loading.value = false;

      errorMessage.value =
        job.message
        || "Phân tích video thất bại.";

      return;
    }

    await sleep(500);
  }
};


const analyzeVideo = async () => {
  if (!selectedFile.value) {
    errorMessage.value =
      "Vui lòng chọn video trước.";

    return;
  }

  loading.value = true;

  result.value = null;

  progress.value = 0;

  status.value =
    "uploading";

  errorMessage.value = "";


  const formData =
    new FormData();

  formData.append(
    "video",
    selectedFile.value
  );


  try {
    const response =
      await api.post(
        "/api/analyze/video",
        formData
      );

    const jobId =
      response.data.job_id;

    status.value =
      "processing";

    await pollProgress(
      jobId
    );

  } catch (error) {
    console.error(
      "VIDEO ERROR:",
      error
    );

    loading.value = false;

    if (
      error.response?.data?.message
    ) {
      errorMessage.value =
        error.response.data.message;
    } else {
      errorMessage.value =
        "Phân tích video thất bại.";
    }
  }
};


onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(
      previewUrl.value
    );
  }
});
</script>


<template>
  <section>

    <h1 class="page-title">
      Video Analysis
    </h1>

    <p class="page-subtitle">
      Upload classroom video
      and analyze seat occupancy.
    </p>


    <!-- ========================== -->
    <!-- UPLOAD -->
    <!-- ========================== -->

    <div class="panel">

      <h3>
        Upload Video
      </h3>

      <input
        type="file"
        accept="video/*"
        @change="handleFile"
      >


      <!-- Preview video gốc -->
      <div
        v-if="previewUrl"
        class="upload-preview"
      >

        <h4>
          Original Video
        </h4>

        <video
          :src="previewUrl"
          controls
          class="preview-video"
        >
        </video>

      </div>


      <div
        style="margin-top: 18px"
      >

        <button
          class="primary-btn"
          :disabled="loading"
          @click="analyzeVideo"
        >
          {{
            loading
              ? "Processing..."
              : "Analyze Video"
          }}
        </button>

      </div>


      <p
        v-if="errorMessage"
        class="error-message"
      >
        {{ errorMessage }}
      </p>


      <!-- ========================== -->
      <!-- PROGRESS -->
      <!-- ========================== -->

      <div
        v-if="loading"
        class="progress-area"
      >

        <p
          v-if="
            status === 'uploading'
          "
        >
          Uploading video...
        </p>


        <p
          v-else-if="
            status === 'converting'
          "
        >
          Converting video
          for browser playback...
        </p>


        <p
          v-else
        >
          Processing:
          {{ progress }}%
        </p>


        <div class="progress-track">

          <div
            class="progress-bar"
            :style="{
              width:
                progress + '%'
            }"
          >
          </div>

        </div>

      </div>

    </div>


    <!-- ========================== -->
    <!-- RESULT -->
    <!-- ========================== -->

    <div
      v-if="result"
      class="panel"
    >

      <h3>
        Processing Complete
      </h3>


      <div class="result-summary">

        <div class="result-item">

          <span>
            Persons
          </span>

          <strong>
            {{ result.persons }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Total Seats
          </span>

          <strong>
            {{ result.total_seats }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Occupied
          </span>

          <strong>
            {{ result.occupied }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Empty
          </span>

          <strong>
            {{ result.empty }}
          </strong>

        </div>


        <div class="result-item">

          <span>
            Occupancy Rate
          </span>

          <strong>
            {{
              Number(
                result.occupancy_rate
              ).toFixed(1)
            }}%
          </strong>

        </div>


        <div class="result-item">

          <span>
            Average FPS
          </span>

          <strong>
            {{
              Number(
                result.fps || 0
              ).toFixed(1)
            }}
          </strong>

        </div>

      </div>


      <div
        v-if="result.output_url"
        class="result-video-wrapper"
      >

        <h4>
          Detection Result
        </h4>

        <video
          :key="result.output_url"
          controls
          preload="metadata"
          class="result-video"
        >

          <source
            :src="result.output_url"
            type="video/mp4"
          >

          Your browser does not
          support video playback.

        </video>

      </div>

    </div>

  </section>
</template>
<style>
/* ============================= */
/* VIDEO VIEW */
/* ============================= */

.upload-preview {
  margin-top: 20px;
}

.preview-video {
  display: block;
  width: 100%;
  max-width: 950px;
  max-height: 600px;

  margin-top: 12px;

  border-radius: 12px;

  background: #000;
}

.progress-area {
  margin-top: 22px;
}

.progress-area p {
  margin-bottom: 10px;

  color: #374151;

  font-weight: 500;
}

.progress-track {
  width: 100%;
  height: 16px;

  background: #e5e7eb;

  border-radius: 999px;

  overflow: hidden;
}

.progress-bar {
  height: 100%;

  background: #2563eb;

  border-radius: 999px;

  transition:
    width 0.3s ease;
}

.result-video-wrapper {
  margin-top: 28px;
}

.result-video-wrapper h4 {
  margin-bottom: 12px;
}

.result-video {
  display: block;

  width: 100%;
  max-width: 1100px;
  max-height: 700px;

  border-radius: 12px;

  background: #000;
}

.error-message {
  margin-top: 15px;

  color: #dc2626;

  font-weight: 500;
}
</style>