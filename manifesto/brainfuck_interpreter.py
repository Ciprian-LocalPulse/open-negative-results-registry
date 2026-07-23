#!/usr/bin/env python3
"""Minimal, standard Brainfuck interpreter (30000-cell tape, 8-bit wrapping cells)."""
import sys

def run(code, cell_count=30000):
    code = "".join(c for c in code if c in "+-<>[].,")
    # precompute bracket matches
    stack = []
    match = {}
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            j = stack.pop()
            match[i] = j
            match[j] = i
    tape = [0] * cell_count
    ptr = 0
    out = []
    ip = 0
    steps = 0
    while ip < len(code):
        steps += 1
        if steps > 20_000_000:
            raise RuntimeError("too many steps")
        c = code[ip]
        if c == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif c == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif c == ">":
            ptr = (ptr + 1) % cell_count
        elif c == "<":
            ptr = (ptr - 1) % cell_count
        elif c == ".":
            out.append(chr(tape[ptr]))
        elif c == ",":
            tape[ptr] = 0
        elif c == "[":
            if tape[ptr] == 0:
                ip = match[ip]
        elif c == "]":
            if tape[ptr] != 0:
                ip = match[ip]
        ip += 1
    return "".join(out)

if __name__ == "__main__":
    src = open(sys.argv[1]).read()
    sys.stdout.write(run(src))
