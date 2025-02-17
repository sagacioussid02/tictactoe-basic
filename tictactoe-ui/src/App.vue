<template>
  <div class="game-board">
    <div v-for="(row, i) in board" :key="i" class="board-row">
      <button v-for="(cell, j) in row" :key="j" @click="handleMove(i, j)" :disabled="cell !== ''">
        {{ cell }}
      </button>
    </div>
    <div v-if="winner">Winner: {{ winner }}</div>
    <div v-if="draw">It's a draw!</div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  setup() {
    const board = ref([['', '', ''], ['', '', ''], ['', '', '']]);
    const winner = ref(null);
    const draw = ref(false);
    const ws = ref(null);

    onMounted(() => {
      ws.value = new WebSocket('ws://localhost:8765');

      ws.value.onmessage = (event) => {
        const gameState = JSON.parse(event.data);
        board.value = gameState.board;
        winner.value = gameState.winner;
        draw.value = gameState.draw;
      };

      ws.value.onopen = () => {
        console.log('Connected to WebSocket server');
      };

      ws.value.onclose = () => {
        console.log('Disconnected from WebSocket server');
      };
    });

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close();
      }
    });

    const handleMove = (row, col) => {
      console.log("handleMove called:", row, col);
      if (board.value[row][col] === '' && ws.value) {
        const move = { row, col };
        ws.value.send(JSON.stringify(move));
      }
    };

    return {
      board,
      winner,
      draw,
      handleMove,
    };
  },
};
</script>

<style scoped>
.game-board {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.board-row {
  display: flex;
}

button {
  width: 50px;
  height: 50px;
  font-size: 20px;
  border: 1px solid black;
  margin: 5px;
  cursor: pointer;
}

button:disabled {
  cursor: default;
}
</style>