<script setup>
import {
  ref
} from "vue";

import api
  from "../services/api";


const selectedFile = ref(
  null
);

const loading = ref(
  false
);

const result = ref(
  null
);


const handleFile = event => {

  selectedFile.value =
    event.target.files[0];

};


const analyzeVideo = async () => {

  if (!selectedFile.value) {

    alert(
      "Vui lòng chọn video."
    );

    return;

  }


  const formData =
    new FormData();

  formData.append(
    "video",
    selectedFile.value
  );


  loading.value = true;


  try {

    const response =
      await api.post(
        "/api/analyze/video",
        formData
      );

    result.value =
      response.data;

  } catch (error) {

    console.error(error);

    alert(
      "Phân tích video thất bại."
    );

  } finally {

    loading.value = false;

  }

};
</script>


<template>

  <section>

    <h1 class="page-title">
      Video Analysis
    </h1>

    <div class="panel">

      <input
        type="file"
        accept="video/*"
        @change="handleFile"
      >


      <br>


      <button
        class="primary-btn"
        @click="analyzeVideo"
      >

        {{
          loading
            ? "Processing..."
            : "Analyze Video"
        }}

      </button>

    </div>


    <div
      v-if="result"
      class="panel"
    >

      <h3>
        Processing Complete
      </h3>

      <p>
        Occupancy Rate:
        {{ result.occupancy_rate }}%
      </p>


      <video
        v-if="result.output_url"
        controls
        width="100%"
      >

        <source
          :src="
            'http://127.0.0.1:5000'
            + result.output_url
          "
          type="video/mp4"
        >

      </video>

    </div>

  </section>

</template>