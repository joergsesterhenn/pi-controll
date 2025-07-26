<template>
  <v-card class="pa-4 mt-4" title="🚪 Door Control">
    <v-row align="center" justify="center">
      <v-btn color="green" @click="moveDoor('up')">
        <v-icon>mdi-arrow-up-bold</v-icon>
      </v-btn>
      <v-spacer />
      <v-btn color="red" @click="moveDoor('down')">
        <v-icon>mdi-arrow-down-bold</v-icon>
      </v-btn>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
async function moveDoor(direction: 'up' | 'down') {
  await fetch(`/door?direction=${direction}`, { method: 'POST' });
}
</script>
