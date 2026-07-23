#!/usr/bin/env python3
"""
Malbolge interpreter, ported line-for-line from Ben Olmstead's 1998
reference C implementation (as archived by Lou Scheffer at
lscheffer.com/malbolge_interp.html). The reference implementation is
used as ground truth in preference to the informal English spec
prose, because a documented discrepancy exists between the two
(notably: '<' outputs and '/' reads input in the reference
interpreter, the OPPOSITE of what the prose describes) and all
historical Malbolge programs, including the canonical "Hello world!"
program, were authored and tested against the reference interpreter's
actual behavior.
"""
import sys

MEMSIZE = 59049  # 3^10

XLAT1 = ("+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI"
         ".v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha")
XLAT2 = ("5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1C"
         "B6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@")
assert len(XLAT1) == 94, len(XLAT1)
assert len(XLAT2) == 94, len(XLAT2)

# 3x3 tritwise "op" table: OP[d_trit][a_trit] -> result_trit
# (row = trit of mem[d], column = trit of register a; verified against
# the 9x9 di-trit table in the reference C source, which is this same
# table applied to trit-pairs for performance)
OP3 = [
    [1, 0, 0],
    [1, 0, 2],
    [2, 2, 1],
]

def to_trits(n):
    t = [0] * 10
    for i in range(10):
        t[i] = n % 3
        n //= 3
    return t  # index 0 = least significant trit

def from_trits(t):
    n = 0
    for i in reversed(range(10)):
        n = n * 3 + t[i]
    return n

def crazy_op(x_val, y_val):
    # Mirrors reference C `op(x, y)` EXACTLY:
    #   for j in 0..5: i += O[y/p9[j]%9][x/p9[j]%9] * p9[j]
    # i.e. row index comes from y's digit, column index from x's digit.
    tx, ty = to_trits(x_val), to_trits(y_val)
    tr = [OP3[ty[i]][tx[i]] for i in range(10)]
    return from_trits(tr)

def rotate_right(n):
    # matches reference C: n/3 + (n%3)*19683   (19683 = 3**9)
    return n // 3 + (n % 3) * 19683


def run(source, input_str="", max_steps=5_000_000):
    mem = [0] * MEMSIZE
    prog = [ch for ch in source if not ch.isspace()]
    n = len(prog)
    if n > MEMSIZE:
        raise ValueError("program too long")

    for i, ch in enumerate(prog):
        code = ord(ch)
        if 33 <= code <= 126:
            idx = (code - 33 + i) % 94
            if XLAT1[idx] not in "ji*p</vo":
                raise ValueError(f"invalid instruction char {ch!r} at pos {i}")
        mem[i] = code

    for i in range(n, MEMSIZE):
        mem[i] = crazy_op(mem[i - 1], mem[i - 2])

    a = c = d = 0
    out = []
    inp_iter = iter(input_str)
    steps = 0

    while True:
        steps += 1
        if steps > max_steps:
            raise RuntimeError(f"exceeded {max_steps} steps without halting")

        if not (33 <= mem[c] <= 126):
            raise RuntimeError(f"pc landed on non-instruction cell at c={c} "
                                f"(mem[c]={mem[c]}) -- reference interpreter "
                                f"would hang here")

        instr = XLAT1[(mem[c] - 33 + c) % 94]

        if instr == 'j':          # d = mem[d]
            d = mem[d]
        elif instr == 'i':        # c = mem[d]   (jump)
            c = mem[d]
        elif instr == '*':        # rotate mem[d] right 1 trit; a = mem[d]
            mem[d] = rotate_right(mem[d])
            a = mem[d]
        elif instr == 'p':        # a = mem[d] = op(a, mem[d])  [exact C call order]
            mem[d] = crazy_op(a, mem[d])
            a = mem[d]
        elif instr == '<':        # OUTPUT a  (reference behaviour, not spec prose)
            out.append(chr(a % 256))
        elif instr == '/':        # INPUT into a (reference behaviour, not spec prose)
            ch = next(inp_iter, None)
            a = 59048 if ch is None else (10 if ch == "\n" else ord(ch))
        elif instr == 'v':        # halt -- no encryption/increment on this instr
            break
        # 'o' and anything else: nop, falls through to common tail

        mem[c] = ord(XLAT2[(mem[c] - 33) % 94])
        c = 0 if c == MEMSIZE - 1 else c + 1
        d = 0 if d == MEMSIZE - 1 else d + 1

    return "".join(out)


if __name__ == "__main__":
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(run(src))
