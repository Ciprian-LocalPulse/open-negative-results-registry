#!/usr/bin/env python3
"""
pubmed_negative_language_classifier.py

Level-1 pipeline component: screens PubMed abstract CONCLUSION text for
language indicating a negative or null finding, so that abstracts whose
*primary published claim* is positive but whose *secondary or tertiary*
outcomes were negative -- the results most likely to be buried and
never make it into a trial registry's status field -- can be flagged
for a human curator to review as potential Dark Data Medicine entries.

This is a heuristic, pattern-based screening tool, not a trained
machine-learning classifier, and it is not a substitute for the human
curator review required by docs/CURATION_GUIDE.md before anything it
flags is merged into data/. It is designed for high recall at the
screening stage (better to show a curator ten false positives than to
silently miss one real negative finding) rather than for autonomous
decision-making.

IMPORTANT LIMITATION, STATED DIRECTLY: this classifier's pattern list
was developed from the established evidence-based-medicine literature
on how RCT conclusion sentences are conventionally phrased (structured-
abstract CONCLUSION sections, hedging-language research, and the
general "did/did not reach significance" vocabulary used across
biomedical writing) -- not by fitting to a labeled corpus of real
abstracts pulled live from PubMed, because live query access to
NCBI E-utilities was not available in the environment this script was
built and tested in. The bundled test suite therefore uses realistic,
hand-written synthetic example sentences, not verbatim reproductions
of real (and copyrighted) abstract text. Before production use, this
classifier should be validated against a labeled sample of real
abstracts and its precision/recall measured properly -- see the
"Known limitations" section of docs/FAQ.md once this is merged.

Usage:
    python pubmed_negative_language_classifier.py --text "..."
    python pubmed_negative_language_classifier.py --file abstracts.txt
    (one abstract's conclusion text per line)
"""

import argparse
import re
from dataclasses import dataclass, field


@dataclass
class ClassificationResult:
    label: str              # "NEGATIVE", "POSITIVE", "MIXED", "UNCLEAR"
    confidence: str         # "high", "medium", "low"
    matched_negative: list = field(default_factory=list)
    matched_positive: list = field(default_factory=list)
    matched_hedge: list = field(default_factory=list)


# Patterns are intentionally phrase-level, not single keywords, because
# single keywords like "significant" are useless on their own -- almost
# every clinical conclusion sentence contains that word regardless of
# direction. Ordered roughly by how unambiguous each pattern is.
NEGATIVE_PATTERNS = [
    r"\bdid not (significantly )?(improve|reduce|increase|differ|change|affect)\b",
    r"\bno (statistically )?significant (difference|improvement|effect|benefit|association)\b",
    r"\bnot significantly different\b",
    r"\bno significant differences?\b",
    r"\bwas not (statistically )?significant\b",
    r"\bfailed to (reach|achieve|demonstrate|show)\b",
    r"\bno (evidence|benefit) (was|of|for)\b",
    r"\bnot superior to\b",
    r"\bcomparable to placebo\b",
    r"\bdoes not support\b",
    r"\bwas discontinued (due to|because of) (lack of|insufficient) efficacy\b",
    r"\bterminated (early )?for futility\b",
    r"\bstudy was stopped\b.*\bfutility\b",
    r"\bno clinically meaningful\b",
    r"\bdid not meet (its |the )?primary endpoint\b",
]

POSITIVE_PATTERNS = [
    r"\bsignificantly (improved|reduced|increased|decreased)\b",
    r"\bsuperior to\b",
    r"\bmet (its |the )?primary endpoint\b",
    r"\bclinically meaningful (improvement|benefit|reduction)\b",
    r"\bwell tolerated and effective\b",
    r"\bstrong(ly)? support(s|ed)?\b",
]

# Hedging language that softens either direction -- flags the sentence
# as worth a closer human look even if a NEGATIVE or POSITIVE pattern
# also matched, since hedged claims are exactly where automatic
# classification is least reliable.
HEDGE_PATTERNS = [
    r"\btrend(ed)? toward(s)?\b",
    r"\bsuggests? (a )?possible\b",
    r"\bwarrants? further (study|investigation|research)\b",
    r"\bunderpowered\b",
    r"\bpreliminary (findings|results|data)\b",
    r"\bmay be (due to|attributable to) (small sample|limited power)\b",
]


def classify(text: str) -> ClassificationResult:
    text_lower = text.lower()

    neg_hits = [p for p in NEGATIVE_PATTERNS if re.search(p, text_lower)]
    pos_hits = [p for p in POSITIVE_PATTERNS if re.search(p, text_lower)]
    hedge_hits = [p for p in HEDGE_PATTERNS if re.search(p, text_lower)]

    if neg_hits and not pos_hits:
        confidence = "high" if len(neg_hits) > 1 or not hedge_hits else "medium"
        return ClassificationResult("NEGATIVE", confidence, neg_hits, pos_hits, hedge_hits)

    if pos_hits and not neg_hits:
        confidence = "high" if len(pos_hits) > 1 or not hedge_hits else "medium"
        return ClassificationResult("POSITIVE", confidence, neg_hits, pos_hits, hedge_hits)

    if neg_hits and pos_hits:
        # Both fired -- common in abstracts reporting a positive primary
        # endpoint alongside a negative secondary one, which is exactly
        # the buried-negative-result case this tool exists to surface.
        return ClassificationResult("MIXED", "medium", neg_hits, pos_hits, hedge_hits)

    if hedge_hits:
        return ClassificationResult("UNCLEAR", "low", neg_hits, pos_hits, hedge_hits)

    return ClassificationResult("UNCLEAR", "low", [], [], [])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", help="Single conclusion-sentence text to classify")
    ap.add_argument("--file", help="Path to a file with one abstract conclusion per line")
    args = ap.parse_args()

    if args.text:
        texts = [args.text]
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
    else:
        ap.error("Provide --text or --file")

    for t in texts:
        r = classify(t)
        print(f"[{r.label:8s} conf={r.confidence:6s}] {t[:100]}")
        if r.matched_negative:
            print(f"           negative cues: {len(r.matched_negative)} pattern(s) matched")
        if r.matched_positive:
            print(f"           positive cues: {len(r.matched_positive)} pattern(s) matched")
        if r.matched_hedge:
            print(f"           hedge cues:    {len(r.matched_hedge)} pattern(s) matched")


if __name__ == "__main__":
    main()
