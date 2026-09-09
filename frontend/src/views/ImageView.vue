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


const analyzeImage = async () => {

    if (!selectedFile.value) {

        alert(
            "Vui lòng chọn ảnh."
        );

        return;
    }


    const formData =
        new FormData();

    formData.append(
        "image",
        selectedFile.value
    );


    loading.value = true;


    try {

        const response =
            await api.post(
                "/api/analyze/image",
                formData
            );

        result.value =
            response.data;

    } catch (error) {

        console.error(error);

        alert(
            "Phân tích ảnh thất bại."
        );

    } finally {

        loading.value = false;

    }

};
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


        <div class="panel">

            <input type="file" accept="image/*" @change="handleFile">


            <br>


            <button class="primary-btn" :disabled="loading" @click="analyzeImage">

                {{
                    loading
                        ? "Analyzing..."
                        : "Analyze Image"
                }}

            </button>

        </div>


        <div v-if="result" class="panel">

            <h3>
                Analysis Result
            </h3>

            <p>
                Persons:
                {{ result.persons }}
            </p>

            <p>
                Total Seats:
                {{ result.total_seats }}
            </p>

            <p>
                Occupied:
                {{ result.occupied }}
            </p>

            <p>
                Empty:
                {{ result.empty }}
            </p>

            <p>
                Occupancy Rate:
                {{ result.occupancy_rate }}%
            </p>


            <img v-if="result.output_url" :src="result.output_url" class="result-image">

        </div>

    </section>

</template>
<style>
.result-image {
    max-width: 100%;
    margin-top: 20px;
    border-radius: 12px;
}
</style>