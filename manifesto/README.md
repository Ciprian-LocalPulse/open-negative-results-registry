# Manifesto Package — English + Malbolge

This package contains the Dark Data Medicine repository manifesto in two
forms, as requested:

| File | What it is |
|---|---|
| `MANIFESTO.md` | The manifesto, in English, in full. |
| `MANIFESTO.mal` | A real, executable **Malbolge** program. When run, it prints the manifesto's core creed: `NO NEGATIVE RESULT DIES IN A DRAWER AGAIN.` |
| `independent_malbolge_vm.py` | A standalone, dependency-free Malbolge interpreter, written directly from the official 1998 specification, that you can use to verify `MANIFESTO.mal` yourself — without trusting the tool that generated it. |

## Why not the *whole* manifesto in Malbolge?

Malbolge is, by design, close to unwritable — the first ever "Hello, World!"
took **two years** to produce, using a search algorithm, not a human typing
code. Writing Malbolge by hand isn't really done; programs are found by
automated search over the space of possible instruction sequences, and the
search cost grows very steeply with output length. In testing for this
package, generating a ~40-character line took a few seconds; a ~75-character
sentence took over a minute and 1.4GB of memory; a 170-character paragraph
exceeded available memory entirely and was killed by the system.

So this package is honest about scope: it doesn't attempt to force the full
manifesto through a process that isn't built for it. Instead, it renders the
manifesto's single, load-bearing sentence — the one the rest of the text is
building toward — as a genuinely working Malbolge program, and gives you the
tools to check that claim yourself rather than take it on faith.

## How to verify it yourself

```bash
python3 independent_malbolge_vm.py MANIFESTO.mal
```

Expected output:
```
NO NEGATIVE RESULT DIES IN A DRAWER AGAIN.
```

`independent_malbolge_vm.py` has no dependencies beyond the Python standard
library, and implements the Malbolge virtual machine from scratch — the
10-trit memory model, the tritwise "crazy" operation, the ternary rotation,
and the 94-character self-modifying encryption table — directly from the
canonical specification (Ben Olmstead, 1998), independently of any tool used
to *generate* `MANIFESTO.mal`. Before trusting it, it was itself checked
against the official reference "cat" program from the specification and
reproduced its documented behavior exactly (echoing an input character, then
outputting the documented `2222222222` ternary → 168 decimal → `¨` on
subsequent reads past EOF) — so you're not just trusting one piece of code
to grade its own homework.

## How `MANIFESTO.mal` was produced

Malbolge programs for arbitrary text are not written by hand; they're found
by automated search. This one was generated using the open-source
`malbolge-generator` toolkit (MIT licensed), which searches the space of
valid execution paths for one that prints the target string, then converts
the result into real, position-correct Malbolge source (as opposed to the
"normalized" instruction-letter form used internally during search, which is
not directly executable — a distinction worth knowing if you go looking at
other Malbolge tools).

## A note on scale

`MANIFESTO.mal` is about 1,200 characters long to produce 43 characters of
output — a roughly 28:1 ratio, which is normal for Malbolge. This isn't a
limitation of this particular generator; it's close to the nature of the
language itself.
