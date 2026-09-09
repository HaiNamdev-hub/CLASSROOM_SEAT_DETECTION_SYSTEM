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

            <th>
              ID
            </th>

            <th>
              Time
            </th>

            <th>
              Source
            </th>

            <th>
              File
            </th>

            <th>
              Persons
            </th>

            <th>
              Total
            </th>

            <th>
              Occupied
            </th>

            <th>
              Empty
            </th>

            <th>
              Rate
            </th>

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
              {{
                item.occupancy_rate
              }}%
            </td>

          </tr>

        </tbody>

      </table>

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
</style>