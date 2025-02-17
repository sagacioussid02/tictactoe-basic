import asyncio
import json
import websockets
import logging

# Configure logging (important for debugging)
logging.basicConfig(level=logging.INFO)  # Set to DEBUG for more verbose output
logger = logging.getLogger("server")

class Game:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.player1 = None
        self.player2 = None
        self.current_player = "X"  # Starts with X

    def is_valid_move(self, row, col):
        return 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ""

    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        self.current_player = "O" if self.current_player == "X" else "X"

    def check_for_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "":  # Rows
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != "":  # Columns
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":  # Diagonal 1
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":  # Diagonal 2
            return self.board[0][2]
        return None

    def check_for_draw(self):
        for row in self.board:
            for cell in row:
                if cell == "":
                    return False
        return self.check_for_winner() is None  # Draw if no winner

    async def broadcast_game_state(self):
        game_state = {
            "board": self.board,
            "current_player": self.current_player,
            "winner": self.check_for_winner(),
            "draw": self.check_for_draw(),
        }
        message = json.dumps(game_state)
        if self.player1:
            await self.player1.send(message)
        if self.player2:
            await self.player2.send(message)


game = Game()  # Initialize the game

async def handler(websocket):
    global game

    try:
        if game.player1 is None:
            game.player1 = websocket
            player = "X"
            logger.info("Player 1 connected")
        elif game.player2 is None:
            game.player2 = websocket
            player = "O"
            logger.info("Player 2 connected")
        else:
            await websocket.send(json.dumps({"error": "Game is full"}))
            logger.warning("Connection attempt from a full game")
            return

        await game.broadcast_game_state()

        async for message in websocket:
            try:
                move = json.loads(message)
                row = move.get("row")
                col = move.get("col")

                if game.current_player == player and game.is_valid_move(row, col):
                    game.make_move(row, col)
                    await game.broadcast_game_state()
                else:
                  logger.debug("Invalid move received")

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
            except TypeError:
                logger.error("Invalid move format")

    except Exception as e: # Catch and log any other exceptions
        logger.exception(f"An error occurred: {e}") # Log the full traceback

    finally:
        if game.player1 == websocket:
            game.player1 = None
            logger.info("Player 1 disconnected")
        elif game.player2 == websocket:
            game.player2 = None
            logger.info("Player 2 disconnected")

        if game.player1 is None and game.player2 is None:
            game = Game() # Reset if no players left
            logger.info("Game reset")



async def main():
    async with websockets.serve(handler, "localhost", 8765):
        logger.info("Server started on localhost:8765")  # Now you'll see this!
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    try:
      asyncio.run(main())
    except Exception as e:
        logger.exception(f"A fatal error occurred: {e}")