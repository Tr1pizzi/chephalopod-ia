#!/usr/bin/env python3
import sys

def generate_pddl(board_size, starting_square):
    # Parse the board size (expects format like "8x8")
    try:
        width_str, height_str = board_size.lower().split("x")
        width = int(width_str)
        height = int(height_str)
    except Exception as e:
        raise ValueError("Board size must be in the format <width>x<height> (e.g., 8x8)") from e

    # Generate the list of square names (objects) in column-major order (A1, A2, ..., B1, B2, ...)
    squares = []
    for col in range(width):
        letter = chr(ord('A') + col)
        for row in range(1, height + 1):
            squares.append(f"{letter}{row}")

    # Knight move offsets
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)]

    # Compute valid moves for each square.
    # We use a 0-based index for columns (A is 0, B is 1, etc.) and use 1-based for rows.
    valid_moves = []
    for col in range(width):
        for row in range(1, height + 1):
            from_square = f"{chr(ord('A') + col)}{row}"
            for dx, dy in knight_moves:
                to_col = col + dx
                to_row = row + dy
                # Check if the destination square is within the board limits.
                if 0 <= to_col < width and 1 <= to_row <= height:
                    to_square = f"{chr(ord('A') + to_col)}{to_row}"
                    valid_moves.append((from_square, to_square))

    # Build the PDDL problem file content as a list of lines.
    problem_name = f"knights-tour-{width}x{height}-{starting_square}"
    pddl_lines = []
    pddl_lines.append(f"(define (problem {problem_name})")
    pddl_lines.append("  (:domain knights-tour)")
    
    # List objects
    pddl_lines.append("  (:objects")
    # We'll print eight squares per line for readability (adjust if board is larger)
    line = "    "
    for i, square in enumerate(squares, start=1):
        line += square + " "
        if i % 8 == 0:
            pddl_lines.append(line.strip())
            line = "    "
    if line.strip():
        pddl_lines.append(line.strip())
    pddl_lines.append("  )")
    
    # Initialization section: starting square and all valid moves.
    pddl_lines.append("  (:init")
    pddl_lines.append("    ; The Knight's starting square is arbitrary; here, we have")
    pddl_lines.append("    ; chosen the upper right corner.")
    pddl_lines.append(f"    (at {starting_square})")
    pddl_lines.append(f"    (visited {starting_square})")
    pddl_lines.append("    ; We have to list all valid moves:")
    for frm, to in valid_moves:
        pddl_lines.append(f"    (valid_move {frm} {to})")
    pddl_lines.append("  )")
    
    # Goal: all squares must be visited.
    pddl_lines.append("  (:goal (and")
    for square in squares:
        pddl_lines.append(f"    (visited {square})")
    pddl_lines.append("  ))")
    pddl_lines.append(")")
    
    return "\n".join(pddl_lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: python make_knights_tour_v1.py <board_size> <starting_square>")
        print("Example: python make_knights_tour_v1.py 8x8 A8")
        sys.exit(1)
    
    board_size = sys.argv[1]
    starting_square = sys.argv[2]
    
    pddl_output = generate_pddl(board_size, starting_square)
    print(pddl_output)

if __name__ == "__main__":
    main()
