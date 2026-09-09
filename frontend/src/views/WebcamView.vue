<script setup>
import { ref } from "vue";

const cameraRunning = ref(false);

const videoFeedUrl = "/video_feed";

const startCamera = () => {
    cameraRunning.value = true;
};

const stopCamera = () => {
    cameraRunning.value = false;
};
</script>

<template>
    <section>

        <h1 class="page-title">
            Live Camera
        </h1>

        <p class="page-subtitle">
            Realtime classroom seat detection
        </p>

        <div class="panel">

            <button class="primary-btn" @click="startCamera">
                Start Camera
            </button>

            <button style="margin-left: 10px" @click="stopCamera">
                Stop Camera
            </button>

            <div v-if="cameraRunning" style="margin-top: 20px">
                <img :src="videoFeedUrl" width="100%">
            </div>

        </div>

    </section>
</template>