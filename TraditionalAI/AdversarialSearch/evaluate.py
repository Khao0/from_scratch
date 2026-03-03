import subprocess
import re

def run_match(algoA, algoB, row, col, k, p1, p2):
    cmd = [
        "python3",
        "judge_Mac.py",
        algoA,
        algoB,
        str(row),
        str(col),
        str(k),
        str(p1),
        str(p2),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    # output = result.stdout
    output = result.stdout.splitlines()

    for line in reversed(output):
        if "Winner" in line:
            print(line)

    output_lines = result.stdout.strip().splitlines()

    for line in reversed(output_lines):
        if "Winner is Player X" in line:
            return "X"
        elif "Winner is Player O" in line:
            return "O"
        elif "Draw" in line:
            return "Draw"

    print("Unexpected output:")
    print(result.stdout)
    return None


def evaluate(algoA:str, algoB:str, games:int=100, map_size=(6,7), connect_n=4, time_limit =2 ):
    win_A = 0
    win_B = 0
    draw = 0

    for i in range(games):
        print(f"Game {i+1}/{games}")

        if i % 2 == 0:
            result = run_match(algoA, algoB, map_size[0], map_size[1], connect_n, 1, time_limit)
            if result == "X":
                win_A += 1
            elif result == "O":
                win_B += 1
            else:
                draw += 1
        else:
            # Swap order
            result = run_match(algoB, algoA, map_size[0], map_size[1], connect_n, 1, time_limit)
            if result == "X":
                win_B += 1
            elif result == "O":
                win_A += 1
            else:
                draw += 1

    print("\n===== RESULT =====")
    print(f"{algoA} wins: {win_A}")
    print(f"{algoB} wins: {win_B}")
    print(f"Draws: {draw}")
    print(f"Win rate {algoA}: {win_A/games:.2%}")
    print(f"Win rate {algoB}: {win_B/games:.2%}")

if __name__ == "__main__":
    evaluate("algoA.py", "algoB.py", games=10)