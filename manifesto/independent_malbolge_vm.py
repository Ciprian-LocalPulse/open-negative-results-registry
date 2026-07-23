#!/usr/bin/env python3
"""
independent_malbolge_vm.py

A from-scratch, standalone implementation of the official Malbolge virtual
machine, written directly from the canonical specification (Ben Olmstead,
1998; as documented on esolangs.org/wiki/Malbolge). This does NOT reuse any
code from the 'malbolge-generator' package used to produce MANIFESTO.mal --
its only purpose is to serve as an independent second opinion on what a
given Malbolge program actually outputs.

Usage:
    python3 independent_malbolge_vm.py MANIFESTO.mal
"""

import sys

ORIGINAL    = ''.join(chr(i) for i in range(33, 127))  # '!' .. '~', 94 chars
TRANSLATED  = "5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@"
assert len(ORIGINAL) == 94 and len(TRANSLATED) == 94
ENCIPHER = {ord(o): t for o, t in zip(ORIGINAL, TRANSLATED)}

# Instruction table: (C + mem[C]) % 94 -> op letter (per reference-interpreter
# convention, matching the esolangs.org "Malbolge" article's main table).
OPCODES = {
    4:  'i',   # C = [D]
    5:  '<',   # PRINT(A % 256)
    23: '/',   # A = INPUT
    39: '*',   # A = [D] = ROTATE_RIGHT([D])
    40: 'j',   # D = [D]
    62: 'p',   # A = [D] = CRAZY_OP(A, [D])
    68: 'o',   # NOP
    81: 'v',   # STOP
}

# Tritwise "crazy" operation table: crazy[d_trit][a_trit] -> result_trit
CRAZY = {
    0: {0: 1, 1: 0, 2: 0},
    1: {0: 1, 1: 0, 2: 2},
    2: {0: 2, 1: 2, 2: 1},
}

WORD_TRITS = 10
MEM_SIZE = 3 ** WORD_TRITS  # 59049


def to_trits(value):
    trits = []
    v = value
    for _ in range(WORD_TRITS):
        trits.append(v % 3)
        v //= 3
    return trits  # trits[0] = least significant


def from_trits(trits):
    value = 0
    for i, t in enumerate(trits):
        value += t * (3 ** i)
    return value


def rotate_right(value):
    trits = to_trits(value)
    new_trits = [trits[(i + 1) % WORD_TRITS] for i in range(WORD_TRITS)]
    return from_trits(new_trits)


def crazy_op(a, d):
    a_trits = to_trits(a)
    d_trits = to_trits(d)
    result_trits = [CRAZY[d_trits[i]][a_trits[i]] for i in range(WORD_TRITS)]
    return from_trits(result_trits)


def load_program(source):
    # Strip whitespace, keep only printable-range characters as instructions.
    program_chars = [c for c in source if not c.isspace()]
    mem = [0] * MEM_SIZE
    for i, c in enumerate(program_chars):
        mem[i] = ord(c)
    prog_len = len(program_chars)
    # Fill the rest of memory via the crazy operation on the two preceding words.
    for i in range(prog_len, MEM_SIZE):
        mem[i] = crazy_op(mem[i - 1], mem[i - 2])
    return mem, prog_len


def run(source, input_data='', max_steps=2_000_000):
    mem, prog_len = load_program(source)
    C = 0
    D = 0
    A = 0
    output = []
    input_iter = iter(input_data)
    steps = 0

    while True:
        steps += 1
        if steps > max_steps:
            raise RuntimeError(f"Exceeded max_steps ({max_steps}) without halting")

        cell = mem[C]
        if not (33 <= cell <= 126):
            raise RuntimeError(
                f"Execution stopped: value at C={C} is {cell}, outside 33-126"
            )

        op_code = (C + cell) % 94
        op = OPCODES.get(op_code, 'o')  # anything unmapped behaves as NOP

        if op == 'i':
            C = mem[D]
            # C will be re-bounded by the mod-increment step below; but we
            # must NOT increment again before the encipher step uses this
            # new C value, per spec ("jumps are not encrypted" trick relies
            # on enciphering the *final* C).
        elif op == '<':
            output.append(chr(A % 256))
        elif op == '/':
            try:
                ch = next(input_iter)
                A = ord(ch)
            except StopIteration:
                A = MEM_SIZE - 1  # conventional EOF sentinel; unused here
        elif op == '*':
            A = rotate_right(mem[D])
            mem[D] = A
        elif op == 'j':
            D = mem[D]
        elif op == 'p':
            A = crazy_op(A, mem[D])
            mem[D] = A
        elif op == 'v':
            break
        elif op == 'o':
            pass  # NOP
        else:
            pass  # unreachable given OPCODES.get default

        # Encipher the value at the (possibly just-updated) C position.
        if 33 <= mem[C] <= 126:
            mem[C] = ord(ENCIPHER[mem[C]])

        C = (C + 1) % MEM_SIZE
        D = (D + 1) % MEM_SIZE

    return ''.join(output)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 independent_malbolge_vm.py <program.mal>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    result = run(source)
    print(result)


if __name__ == '__main__':
    main()
