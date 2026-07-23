# MALBOLGE_ARTIFACT.md

## What `MANIFEST.mb` is, and how it was verified

`MANIFEST.mb`, at the root of this repository, is a Malbolge program — included as a small companion artifact to `MANIFEST.md`, in keeping with this account's convention of pairing serious project documentation with an esoteric-language artifact. This note exists so nothing about that file has to be taken on faith.

## What it is not

It is **not** a translation of `MANIFEST.md`, and no such translation is claimed anywhere in this repository. Malbolge programs of any real complexity are not hand-authored; they are found by search or built with dedicated assembler tooling, because every instruction encrypts itself on execution. Nothing resembling a multi-paragraph English document can be encoded in it by hand within any practical effort. `MANIFEST.mb` is a short, historically established program, reproduced and verified, not a novel encoding of this repository's text.

## Provenance

The 88-character program in `MANIFEST.mb` is cross-published, identically, across independently maintained sources spanning more than two decades — Wikipedia's "Malbolge" article, Gregory Laughlin's "Malbolge (a second look)" (oklo.org, 2022), and the Esolang wiki. We treat that convergence as strong evidence the transcription is faithful, on the same logic this registry's own curation checklist applies to a submitted result's source: cross-check independent sources rather than trust one.

## Independent verification

Rather than take the program's claimed output on faith from secondary sources, an interpreter was written from Ben Olmstead's original 1998 specification and reference C implementation (archived at `lscheffer.com`) — not from a third-party library — and included in this repository at `assets/malbolge_interpreter.py`, MIT licensed like the rest of the project's tooling. The reference C source was treated as ground truth over the prose specification where the two disagree (they do, on the I/O instructions), since every historical Malbolge program was authored and tested against the reference interpreter's actual behavior.

Running it:

```
$ python3 assets/malbolge_interpreter.py MANIFEST.mb
Hello, world.
```

The exact wording — lowercase *w*, closing period, not "Hello, World!" — matches the documented original output precisely, including details that secondary paraphrases sometimes render differently. That specificity is itself evidence the interpreter is correct rather than coincidentally close: a flawed interpreter is far more likely to produce visibly wrong output than to reproduce an exact, rarely-quoted-verbatim string by chance.

## Limitations, stated plainly

This confirms the interpreter reproduces this program's documented behavior; it is not a formal proof of correctness across the full instruction set. A second reference program (a Malbolge `cat`/echo implementation) was not successfully verified in the time available and is not included here. Classical Malbolge has no debugger by design, which the original specification states without irony — deeper verification was scoped to what this artifact required, not pursued exhaustively.

---

*Consistent with `MANIFEST.md` §II.4: this note exists so that no claim made about this artifact has to be taken on faith.*
