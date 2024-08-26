"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
import chess.engine
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.types import MOVE, HOMEMADE_ARGS_TYPE
import logging

from openai import OpenAI
from chess_dspy import load_optimized_engine

from typing import Optional
from lib.config import Configuration
from lib import model
from lib.types import OPTIONS_GO_EGTB_TYPE, COMMANDS_TYPE, MOVE

from dotenv import load_dotenv
load_dotenv()
# import os
client = OpenAI()

# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)

import dspy
# task_model = dspy.OpenAI(model="gpt-4o", max_tokens=4000)
task_model = dspy.OpenAI(model="ft:gpt-4o-mini-2024-07-18:devpy:puzzlegod-it1-129ex:9zLUVZ9j", max_tokens=4000, temperature=1.0)
dspy.settings.configure(lm=task_model, trace=[])


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass



prompt = """Given a series of chess moves in Portable Game Notation (PGN) format, your task is to determine and return the correct next move in Standard Algebraic Notation (SAN) format.

---

Follow the following format.

Pgn: The chess position
Reasoning: Let's think step by step in order to ${{produce the answer}}. We ...
Answer: The correct next move in SAN format

---

Pgn: 1. e4 e5 2. Ne2 Bc5 3. Ng3 d6 4. Bc4 h6 5. O-O Nf6 6. d3 O-O 7. Nh5 Bg4 8. Nxf6+ Qxf6 9.
Reasoning: Let's think step by step in order to Pgn: 1. e4 e5 2. Ne2 Bc5 3. Ng3 d6 4. Bc4 h6 5. O-O Nf6 6. d3 O-O 7. Nh5 Bg4 8. Nxf6+ Qxf6 9. Reasoning: Let's think step by step in order to determine the best move for White. After 8...Qxf6, Black has captured the knight on f6, and now White needs to respond. The most logical move for White is to play 9. Qxg4, capturing the bishop on g4. This move not only gains material but also puts pressure on Black's position.

---

Pgn: 1. e4 d5 2. exd5 Qxd5 3. Nc3 Qd8 4. Nf3 Nf6 5. h3 Bf5 6. Bc4 e6 7. d3 Be7 8. Qe2 O-O 9. Bd2 a6 10. g4 Bg6 11. Ne5 b5 12. Bb3 c5 13. h4 h6 14. Nxg6 fxg6 15. g5 Nd5 16. Nxd5 exd5 17. Qe6+ Kh7 18. Bxd5 Bxg5 19. O-O-O Bxd2+ 20. Rxd2 Rf6 21. Qe4 Ra7 22. h5 Re7 23. hxg6+ Kh8 24. Qg2 Qd6 25. Re2 Rxe2 26. Rxh6+ gxh6 27. g7+ Kh7 28.
Reasoning: Let's think step by step in order to determine the best move for White. The position after 28. is critical as White has a strong initiative and is threatening to deliver checkmate or win material. The last move played by Black was 27...Kh7, which puts the Black king in a precarious position. White has several options to consider, but the most effective move is to play 29. g8=Q+. This move promotes the pawn on g7 to a queen, delivering check to the Black king. The newly promoted queen will also create a significant threat, as it can potentially lead to checkmate on the next move if Black does not respond adequately.

---

Pgn: 1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Nc3 Nxe4 8. O-O Bxc3 9. d5 Bf6 10. Re1 Ne7 11. Rxe4 d6 12. Bg5 Bxg5 13. Nxg5 h6 14. Nf3 O-O 15. Qe2 Ng6 16. Re1 Bf5 17. Rd4 a6 18. Bd3 Bxd3 19. Qxd3 Qd7 20. h4 Rae8 21. Rxe8 Rxe8 22. h5 Ne5 23. Nxe5 Rxe5 24. g4 Qe7 25. Kg2 Re1 26. Qf5 g6 27. hxg6 fxg6 28. Qxg6+ Qg7 29. Qxg7+ Kxg7 30. Rd2 Kf6 31. f4 Re4 32. Kf3 Rc4 33. b3 Rc5 34. Ke4 Ra5 35. a4 Rc5 36. Rd3 Rc1 37. Rh3 Kg6 38. f5+ Kg5 39. Kf3 Rc3+ 40. Kg2
Answer: Rxh3

---

Pgn: 1. e4 e5 2. f4 exf4 3. Bc4 d6 4. Nc3 h6 5. d4 g5 6. h4 Bg7 7. hxg5 hxg5 8. Rxh8 Bxh8 9. Qh5 Qf6 10. Nd5 Qxd4 11. Nxc7+ Kd8 12. Nf3 Qxe4+ 13. Be2 Kxc7 14. Qxh8 Ne7 15. Nxg5 Qxg2 16. Bxf4 Bg4 17. O-O-O Qxe2 18. Bxd6+ Kb6 19. Qd4+ Kc6 20.
Answer: Qc3+

---

Pgn: 1. e4 e5 2. d3 Nc6 3. Be2 d5 4. exd5 Qxd5 5. Bf3 Qd8 6. Bxc6+ bxc6 7. Nf3 Bd6 8. O-O h6 9. Qe2 Qf6 10. d4 Bg4 11. dxe5 Bxf3 12. exf6+ Bxe2 13. Re1 Nxf6 14. Rxe2+ Be7 15. b3 O-O-O 16. Rxe7
Answer: Rd1+

---

Pgn: {pgn}
Reasoning: Let's think step by step in order to """

def move_stack_to_numbered_pgn(board):
    pgn_list = []
    current_board = chess.Board()
    
    for move_number, move in enumerate(board.move_stack, start=1):
        if move_number % 2 == 1:  # White's move
            pgn_list.append(f"{(move_number + 1) // 2}.")
        
        pgn_list.append(current_board.san(move))
        current_board.push(move)

    move_number = len(board.move_stack) + 1
    if move_number % 2 == 1:  # White's move
            pgn_list.append(f"{(move_number + 1) // 2}.")
    
    # Join the moves into a single string with proper spacing
    pgn_string = ' '.join(pgn_list)
    
    return pgn_string


class RawBot(ExampleEngine):
    """LLM powered bot"""

    def __init__(self, commands: COMMANDS_TYPE, options: OPTIONS_GO_EGTB_TYPE, stderr: Optional[int],
                 draw_or_resign: Configuration, game: Optional[model.Game], **popen_args: str):
        """Start Stockfish."""
        super().__init__(commands, options, stderr, draw_or_resign, game, **popen_args)
        # self.engine = chess.engine.SimpleEngine.popen_uci(f"./stockfish/stockfish-ubuntu-x86-64-sse41-popcnt")

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose a random move."""

        # response = client.chat.completions.create(
        #     model=model_name,
        #     messages=[
        #         {"role": "user", "content": prompt.format(pgn=pgn)}
        #     ],
        #     temperature=0,
        #     max_tokens=1000,
        #     top_p=1,
        #     frequency_penalty=0,
        #     presence_penalty=0
        # )
        # predicted_response = response.choices[0].message.content.strip().split("\nAnswer: ")[-1]
        
        pgn = move_stack_to_numbered_pgn(board)
        print(pgn)
        program = load_optimized_engine()
        
        try:
            res = []
            # for i in range(3):
            result = program(pgn=pgn)
            print(result.board)
            result.board.push(result.move)
            print("after\n",result.board)
            nwinfo = self.engine.analyse(result.board,chess.engine.Limit(depth=20))
            print(nwinfo, result)
            # res.append((nwinfo.get("score"), result))

            # print(res)
            # sorted_res = sorted(res, key=lambda x: x[0], reverse=True)
            # best_result = sorted_res[0]

            print(result)
            print(result.answer)
            print(result.move)
            if result.move is not None:
                return PlayResult(result.move, None)
        except Exception as e:
            print(e)

        # if result.move is not None:
        #     return PlayResult(result.move, None)
        # else:
        random_move = random.choice(list(board.legal_moves))
        print("playing random:", random_move)
        return PlayResult(random_move, None)



# Bot names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    """Get the first move when sorted by san representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically."""
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Get the first move when sorted by uci representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically in uci representation."""
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)


class ComboEngine(ExampleEngine):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc > 10:
            # Choose a random move.
            move = random.choice(possible_moves)
        else:
            # Choose the first move alphabetically in uci representation.
            possible_moves.sort(key=str)
            move = possible_moves[0]
        return PlayResult(move, None, draw_offered=draw_offered)
