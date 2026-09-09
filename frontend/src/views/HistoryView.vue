<script setup>
import {
  onMounted,
  ref
} from "vue";

import api
  from "../services/api";


const history = ref(
  []
);


const loadHistory = async () => {

  try {

    const response =
      await api.get(
        "/api/history"
      );

    history.value =
      response.data;

  } catch (error) {

    console.error(error);

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


    <div class="panel">

      <table class="history-table">

        <thead>

          <tr>

            <th>
              Time
            </th>

            <th>
              Source
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
              {{ item.created_at }}
            </td>

            <td>
              {{ item.source_type }}
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
}

.history-table th,
.history-table td {
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}
</style>