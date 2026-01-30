import subprocess
import time
import select
import sys


def send_time_receive(myprocess, mymessage, timeout):
    # Send message to the program
    if mymessage is not None:
        myprocess.stdin.write((mymessage + "\n").encode())
        myprocess.stdin.flush()

    timeout += 0.003
    start_time = time.time()
    # Wait for input from the program with time limit T
    while True:
        rlist, _, _ = select.select([myprocess.stdout], [], [], timeout)
        if rlist:
            myoutput = myprocess.stdout.readline().decode().strip()
            return 0, myoutput  # receive input successfully
        elif time.time() - start_time > timeout:
            return 1, ""  # Timed out


# check if the game has a winner
def check_consecutive(matrix, k):
    def check_consecutive_in_list(lst, k):
        count = 0
        prev = None
        for char in lst:
            if char == prev and char != ".":
                count += 1
                if count == k:
                    return True
            else:
                prev = char
                count = 1
        return False

    # Check rows
    for row in matrix:
        if check_consecutive_in_list(row, k):
            return True

    # Check columns
    for col in range(len(matrix[0])):
        column = [matrix[row][col] for row in range(len(matrix))]
        if check_consecutive_in_list(column, k):
            return True

    # Check diagonals
    for i in range(len(matrix) - k + 1):
        for j in range(len(matrix[0]) - k + 1):
            diagonal = [matrix[i + x][j + x] for x in range(k)]
            if check_consecutive_in_list(diagonal, k):
                return True
    for i in range(len(matrix) - k + 1):
        for j in range(len(matrix[0]) - k + 1):
            diagonal = [matrix[i + x][j + k - 1 - x] for x in range(k)]
            if check_consecutive_in_list(diagonal, k):
                return True

    return False


# Display the current board
def print_board(board):
    for row in board[::-1]:
        print("".join(row))


def main():
    if len(sys.argv) != 8:
        print("Usage: python3 judge.py <path-to-programA> <path-to-programB> <N> <M> <X> <F> <T>")
        return
    N = int(sys.argv[3])
    M = int(sys.argv[4])
    X = int(sys.argv[5])
    F = int(sys.argv[6])
    T = float(sys.argv[7])
    board = [["." for _ in range(M)] for _ in range(N)]
    processAcommand = ["python3", sys.argv[1]]
    programBcommand = ["python3", sys.argv[2]]
    winner = 2

    # Start Program A
    processA = subprocess.Popen(processAcommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    status, message = send_time_receive(processA, None, 2.1)
    print("A: ", message if status == 0 else "Timed Out")
    if status == 1:
        winner = F

    # Start Program B
    processB = subprocess.Popen(programBcommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    status, message = send_time_receive(processB, None, 2.1)
    print("B: ", message if status == 0 else "Timed Out")
    if status == 1:
        winner = 1 - F

    turn = 1 - F
    first_message = " ".join([str(x) for x in [N, M, 1, X, T]])
    second_message = " ".join([str(x) for x in [N, M, 0, X, T]])
    message = first_message
    turn_count = 0
    while turn_count != N * M and winner == 2:

        # send and receive message
        myprocess = processA if turn == 0 else processB
        if turn_count == 1:
            message = second_message + "\n" + message
        status, message = send_time_receive(myprocess, message, T)

        # if Timed Out
        if status == 1:
            print("Program " + ("A" if turn == 0 else "B") + " Timed out")
            winner = 1 - turn
            break

        print("Program " + ("A" if turn == 0 else "B") + " moves " + message)
        turn_count += 1

        move = int(message)
        # Check for illegal moves
        if move < 0 or move >= M:
            print("Illegal move")
            winner = 1 - turn
            break

        # insert the disc into the board
        r = 0
        while r < N and board[r][move] != ".":
            r += 1
        if r == N:
            print("Illegal move")
            winner = 1 - turn
            break
        board[r][move] = ("X" if turn == 0 else "O")

        print_board(board)

        # check if there is a winner
        if check_consecutive(board, X) == True:
            winner = turn
            break

        turn = 1 - turn

    processA.terminate()
    processB.terminate()
    if winner == 2:
        print("Result: Draw")
    else:
        print("Result: Winner is Player " + ("X" if winner == 0 else "O"))


if __name__ == "__main__":
    main()
