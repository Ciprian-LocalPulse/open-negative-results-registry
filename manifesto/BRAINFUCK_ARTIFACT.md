# BRAINFUCK_ARTIFACT.md

## What `DARKDATA.bf` is

`DARKDATA.bf`, at the repository root, is a small Brainfuck program that prints the string `DARKDATA`. It is a second esoteric-language companion artifact alongside `MANIFEST.mb` (Malbolge) — see `MALBOLGE_ARTIFACT.md` for that one's rationale, which applies equally here.

Unlike Malbolge, Brainfuck programs of this size are entirely tractable to hand-author and hand-verify, so this note is short: there is no cryptanalysis to document, only a straightforward algorithm and a correctness check.

## How it was built

The program uses a standard loop-based encoding technique (the same one real Brainfuck "Hello, World!" programs use): for each character, the generator searches for a pair of small integers `(a, b)` such that `a × b` lands close to the target ASCII value, then emits a multiplication loop (`>` set a counter to `b`, loop adding `a` per iteration `<`) followed by a small direct adjustment for the remainder, rather than emitting one `+` per unit of value. This keeps the program compact — 117 bytes for 8 characters, versus 613 bytes for the naive one-`+`-per-unit approach also tried during development.

The generator script is not included in this repository (it is a one-off build tool, not part of the registry's tooling); the technique is described above in full so the program is reproducible and auditable by inspection, not just by trust.

## Verification

A minimal, standard Brainfuck interpreter (30,000-cell tape, 8-bit wrapping cells — the conventional configuration) is included at `assets/brainfuck_interpreter.py`, MIT licensed like the rest of this project's tooling.

```
$ python3 assets/brainfuck_interpreter.py DARKDATA.bf
DARKDATA
```

Brainfuck's semantics are simple and uncontested (unlike Malbolge's, where the prose specification and reference implementation disagree on I/O instruction direction — see `MALBOLGE_ARTIFACT.md`), so a single correct-by-inspection interpreter run is sufficient verification here; there is no equivalent ambiguity to cross-check against.

---

*Consistent with `MANIFEST.md` §II.4 and `MALBOLGE_ARTIFACT.md`: nothing here is asserted without a way to check it.*
