<template>
  <v-card class="pa-4 mt-4" title="🚪 Hühnerklappe">
    <v-row align="center" justify="center">
      <v-btn color="green" @click="moveDoor('up')">
        <v-icon>mdi-arrow-up-bold</v-icon>
      </v-btn>
      <div class="text-body-1 font-weight-medium">{{ doorStatusText }}</div>
      <v-btn color="red" @click="moveDoor('down')">
        <v-icon>mdi-arrow-down-bold</v-icon>
      </v-btn>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const doorStatus = ref<number>(0)

const DoorStateLabels = [
  'Unbekannt',
  'Offen',
  'Geschlossen',
  'Öffnet...',
  'Schließt...'
]

const doorStatusText = computed(() => DoorStateLabels[doorStatus.value] ?? 'Fehler')

async function fetchDoorState() {
  try {
    const res = await fetch('/door-state')
    const data = await res.json()
    doorStatus.value = data.status
  } catch (err) {
    console.error('Fehler beim Abrufen des Türstatus:', err)
    doorStatus.value = 0 // fallback to UNDEFINED
  }
}

setInterval(fetchDoorState, 2000)

onMounted(() => {
  fetchDoorState()
})

async function moveDoor(direction: 'up' | 'down') {
  await fetch(`/door?direction=${direction}`, { method: 'POST' });
}
</script>
