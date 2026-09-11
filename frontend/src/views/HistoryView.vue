<script setup>
import {
  onMounted,
  ref
} from "vue";

import api
  from "../services/api";


const history = ref([]);

const loading = ref(false);

const errorMessage = ref("");


// Dữ liệu đang được xem
const selectedItem = ref(null);

const showMediaModal = ref(false);


const loadHistory = async () => {

  loading.value = true;
  errorMessage.value = "";

  try {

    const response =
      await api.get(
        "/api/history"
      );

    history.value =
      response.data;

  } catch (error) {

    console.error(
      "History error:",
      error
    );

    errorMessage.value =
      "Không thể tải lịch sử.";

  } finally {

    loading.value = false;

  }

};


const viewMedia = (item) => {

  selectedItem.value = item;

  showMediaModal.value = true;

};


const closeMedia = () => {

  showMediaModal.value = false;

  selectedItem.value = null;

};


onMounted(
  loadHistory
);
</script>


<template>

  <section>

    <h1 class="page-title">
      Analysis History
    </h1>

    <p class="page-subtitle">
      Previous classroom analysis results.
    </p>


    <div class="panel">

      <button
        class="primary-btn"
        @click="loadHistory"
      >
        Refresh
      </button>


      <p v-if="loading">
        Loading...
      </p>


      <p
        v-if="errorMessage"
      >
        {{ errorMessage }}
      </p>


      <p
        v-if="
          !loading
          && history.length === 0
        "
      >
        No analysis history.
      </p>


      <table
        v-if="history.length > 0"
        class="history-table"
      >

        <thead>

          <tr>

            <th>ID</th>

            <th>Time</th>

            <th>Source</th>

            <th>File</th>

            <th>Persons</th>

            <th>Total</th>

            <th>Occupied</th>

            <th>Empty</th>

            <th>Rate</th>

            <!-- Thêm cột này -->
            <th>View</th>

          </tr>

        </thead>


        <tbody>

          <tr
            v-for="item in history"
            :key="item.id"
          >

            <td>
              {{ item.id }}
            </td>

            <td>
              {{ item.created_at }}
            </td>

            <td>
              {{ item.source_type }}
            </td>

            <td>
              {{ item.source_name }}
            </td>

            <td>
              {{ item.persons }}
            </td>

            <td>
              {{ item.total_seats }}
            </td>

            <td>
              {{ item.occupied_seats }}
            </td>

            <td>
              {{ item.empty_seats }}
            </td>

            <td>
              {{ item.occupancy_rate }}%
            </td>


            <!-- Nút xem ảnh/video -->
            <td>

              <button
                class="view-btn"
                @click="viewMedia(item)"
              >
                View
              </button>

            </td>

          </tr>

        </tbody>

      </table>

    </div>


    <!-- Modal xem ảnh/video -->
    <div
      v-if="showMediaModal && selectedItem"
      class="modal-overlay"
      @click.self="closeMedia"
    >

      <div class="media-modal">

        <div class="modal-header">

          <div>

            <h2>
              Analysis Media
            </h2>

            <p>
              {{ selectedItem.created_at }}
            </p>

          </div>


          <button
            class="close-btn"
            @click="closeMedia"
          >
            ×
          </button>

        </div>


        <div class="media-container">

          <!-- Nếu là ảnh -->
          <img
            v-if="
              selectedItem.source_type === 'image'
            "
            :src="selectedItem.media_url"
            class="history-image"
            alt="Classroom analysis"
          >


          <!-- Nếu là video -->
          <video
            v-else-if="
              selectedItem.source_type === 'video'
            "
            :src="selectedItem.media_url"
            class="history-video"
            controls
          >
          </video>


          <p v-else>
            Không hỗ trợ loại file này.
          </p>

        </div>


        <div class="media-info">

          <p>
            <strong>File:</strong>
            {{ selectedItem.source_name }}
          </p>

          <p>
            <strong>Persons:</strong>
            {{ selectedItem.persons }}
          </p>

          <p>
            <strong>Occupied:</strong>
            {{ selectedItem.occupied_seats }}
          </p>

          <p>
            <strong>Empty:</strong>
            {{ selectedItem.empty_seats }}
          </p>

          <p>
            <strong>Occupancy Rate:</strong>
            {{ selectedItem.occupancy_rate }}%
          </p>

        </div>

      </div>

    </div>

  </section>

</template>


<style>
.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.history-table th,
.history-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.history-table th {
  background: #f9fafb;
}


/* Nút View */

.view-btn {
  padding: 7px 14px;
  border: none;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  cursor: pointer;
}

.view-btn:hover {
  background: #1d4ed8;
}


/* Modal */

.modal-overlay {
  position: fixed;
  inset: 0;

  background: rgba(
    0,
    0,
    0,
    0.6
  );

  display: flex;
  align-items: center;
  justify-content: center;

  padding: 20px;

  z-index: 1000;
}


.media-modal {
  background: white;

  width: 90%;
  max-width: 900px;

  max-height: 90vh;

  overflow-y: auto;

  border-radius: 12px;

  padding: 24px;

  box-shadow:
    0 20px 50px
    rgba(0, 0, 0, 0.25);
}


.modal-header {
  display: flex;

  justify-content: space-between;

  align-items: flex-start;

  margin-bottom: 20px;
}


.modal-header h2 {
  margin: 0;
}


.modal-header p {
  margin-top: 5px;

  color: #6b7280;
}


.close-btn {
  border: none;

  background: none;

  font-size: 30px;

  cursor: pointer;

  color: #6b7280;
}


.media-container {
  width: 100%;

  display: flex;

  justify-content: center;

  background: #111827;

  border-radius: 10px;

  overflow: hidden;
}


.history-image,
.history-video {
  display: block;

  max-width: 100%;

  max-height: 550px;

  object-fit: contain;
}


.media-info {
  margin-top: 20px;

  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(180px, 1fr)
    );

  gap: 10px;
}


.media-info p {
  margin: 0;

  padding: 10px;

  background: #f9fafb;

  border-radius: 6px;
}
</style>