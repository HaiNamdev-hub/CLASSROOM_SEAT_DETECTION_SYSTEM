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

const result = ref(null);

const errorMessage = ref("");


const handleFile = event => {
  const file = event.target.files[0];

  selectedFile.value = file;

  result.value = null;
  errorMessage.value = "";

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


const analyzeImage = async () => {
  if (!selectedFile.value) {
    errorMessage.value =
      "Vui lòng chọn ảnh trước.";

    return;
  }

  loading.value = true;

  result.value = null;

  errorMessage.value = "";


  const formData =
    new FormData();

  formData.append(
    "image",
    selectedFile.value
  );


  try {
    const response =
      await api.post(
        "/api/analyze/image",
        formData
      );

    result.value =
      response.data;

  } catch (error) {
    console.error(
      "IMAGE ANALYSIS ERROR:",
      error
    );

    if (
      error.response
      && error.response.data
      && error.response.data.message
    ) {
      errorMessage.value =
        error.response.data.message;
    } else {
      errorMessage.value =
        "Phân tích ảnh thất bại.";
    }

  } finally {
    loading.value = false;
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
      Image Analysis
    </h1>

    <p class="page-subtitle">
      Upload classroom image
      and analyze seat occupancy.
    </p>


    <!-- ============================= -->
    <!-- UPLOAD PANEL -->
    <!-- ============================= -->

    <div class="panel">

      <h3>
        Upload Image
      </h3>


      <input
        type="file"
        accept="image/*"
        @change="handleFile"
      >


      <!-- Preview ảnh gốc -->
      <div
        v-if="previewUrl"
        class="upload-preview"
      >

        <h4>
          Original Image
        </h4>

        <img
          :src="previewUrl"
          alt="Image preview"
          class="preview-image"
        >

      </div>


      <div
        style="margin-top: 18px"
      >

        <button
          class="primary-btn"
          :disabled="loading"
          @click="analyzeImage"
        >

          {{
            loading
              ? "Analyzing..."
              : "Analyze Image"
          }}

        </button>

      </div>


      <p
        v-if="errorMessage"
        class="error-message"
      >
        {{ errorMessage }}
      </p>

    </div>


    <!-- ============================= -->
    <!-- RESULT PANEL -->
    <!-- ============================= -->

    <div
      v-if="result"
      class="panel"
    >

      <h3>
        Analysis Result
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

      </div>


      <!-- Ảnh kết quả từ backend -->
      <div
        v-if="result.output_url"
        class="result-image-wrapper"
      >

        <h4>
          Detection Result
        </h4>

        <img
          :src="result.output_url"
          alt="Detection result"
          class="result-image"
        >

      </div>


      <!-- Trạng thái từng seat -->
      <div
        v-if="
          result.seats
          && result.seats.length > 0
        "
        class="seat-result-section"
      >

        <h4>
          Seat Status
        </h4>


        <div class="seat-grid">

          <div
            v-for="seat in result.seats"
            :key="seat.seat_id"
            class="seat-card"
            :class="{
              occupied:
                seat.status
                === 'Occupied',

              empty:
                seat.status
                === 'Empty'
            }"
          >

            <strong>
              {{ seat.seat_id }}
            </strong>

            <span>
              {{ seat.status }}
            </span>

          </div>

        </div>

      </div>

    </div>

  </section>
</template>
<style>
.upload-preview {
  margin-top: 20px;
}

.preview-image {
  display: block;
  width: 100%;
  max-width: 800px;
  max-height: 550px;
  object-fit: contain;
  margin-top: 10px;
  border-radius: 12px;
  background: #f3f4f6;
}

.error-message {
  margin-top: 15px;
  color: #dc2626;
  font-weight: 500;
}

.result-summary {
  display: grid;

  grid-template-columns:
    repeat(5, minmax(120px, 1fr));

  gap: 15px;

  margin-top: 20px;
}

.result-item {
  padding: 18px;
  background: #f8fafc;
  border-radius: 10px;
}

.result-item span {
  display: block;
  color: #6b7280;
  margin-bottom: 8px;
}

.result-item strong {
  font-size: 24px;
}

.result-image-wrapper {
  margin-top: 25px;
}

.result-image {
  display: block;
  width: 100%;
  max-width: 950px;
  max-height: 700px;
  object-fit: contain;
  margin-top: 10px;
  border-radius: 12px;
}

.seat-result-section {
  margin-top: 25px;
}

.seat-grid {
  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(140px, 1fr)
    );

  gap: 12px;
}

.seat-card {
  display: flex;
  flex-direction: column;
  gap: 6px;

  padding: 15px;

  border-radius: 10px;

  border:
    1px solid #e5e7eb;
}

.seat-card.occupied {
  background: #fee2e2;
  border-color: #fca5a5;
}

.seat-card.empty {
  background: #dcfce7;
  border-color: #86efac;
}

@media (
  max-width: 900px
) {
  .result-summary {
    grid-template-columns:
      repeat(2, 1fr);
  }
}

@media (
  max-width: 600px
) {
  .result-summary {
    grid-template-columns:
      1fr;
  }
}
</style>