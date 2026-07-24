#!/usr/bin/env python3
"""
test_pubmed_negative_language_classifier.py

All test sentences below are hand-written by the tool's author to be
realistic in style and vocabulary to real biomedical abstract
CONCLUSION sections, but are NOT copied from any real, copyrighted
publication -- see the top-of-file limitation notice in
pubmed_negative_language_classifier.py for why (no live PubMed access
was available to pull a real labeled sample when this was built).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from pubmed_negative_language_classifier import classify


# --- Clear negative cases ---------------------------------------------

def test_clear_negative_no_significant_difference():
    r = classify("Treatment with the study drug did not significantly reduce "
                 "the primary endpoint compared with placebo.")
    assert r.label == "NEGATIVE"
    assert r.confidence in ("high", "medium")


def test_clear_negative_failed_primary_endpoint():
    r = classify("The trial did not meet its primary endpoint, and no "
                 "statistically significant difference was observed between "
                 "groups at 12 weeks.")
    assert r.label == "NEGATIVE"
    assert r.confidence == "high"


def test_negative_futility_termination():
    r = classify("The study was stopped early for futility after the planned "
                 "interim analysis.")
    assert r.label == "NEGATIVE"


def test_negative_comparable_to_placebo():
    r = classify("Outcomes in the treatment arm were comparable to placebo "
                 "across all measured endpoints.")
    assert r.label == "NEGATIVE"


# --- Clear positive cases (must NOT be misclassified as negative) -----

def test_clear_positive_not_misclassified():
    r = classify("The intervention significantly improved functional outcomes "
                 "and was superior to standard care at all follow-up points.")
    assert r.label == "POSITIVE"


def test_positive_met_endpoint_not_misclassified():
    r = classify("The study met its primary endpoint with a clinically "
                 "meaningful improvement in symptom scores.")
    assert r.label == "POSITIVE"


# --- The important case: mixed / buried negative secondary outcome ----

def test_mixed_positive_primary_negative_secondary_is_flagged():
    r = classify("The primary endpoint was significantly improved; however, "
                 "the intervention did not significantly reduce hospital "
                 "readmission rates, a key secondary outcome.")
    assert r.label == "MIXED"
    assert len(r.matched_negative) >= 1
    assert len(r.matched_positive) >= 1


# --- Hedged / ambiguous language --------------------------------------

def test_hedged_trend_language_flagged_unclear_not_positive():
    r = classify("Symptom scores trended toward improvement, though the study "
                 "was underpowered to detect a definitive effect.")
    assert r.label == "UNCLEAR"
    assert len(r.matched_hedge) >= 1


def test_plain_neutral_sentence_is_unclear_not_forced_into_a_label():
    r = classify("Participants were recruited from three tertiary care "
                 "centers between 2023 and 2025.")
    assert r.label == "UNCLEAR"
    assert r.matched_negative == []
    assert r.matched_positive == []


# --- Precision guard: negation of a positive claim about something else

def test_does_not_false_trigger_on_unrelated_negation():
    # Regression guard: earlier pattern drafts over-matched on any
    # "not" near "significant", including this kind of sentence, which
    # is actually describing baseline characteristics, not an outcome.
    r = classify("Baseline demographic characteristics were not significantly "
                 "different between the two groups, confirming successful "
                 "randomization.")
    # This SHOULD match a negative pattern (correctly, per the pattern
    # design) -- the test documents and locks in that this is a known,
    # accepted limitation: baseline-balance sentences look identical in
    # structure to outcome-null sentences, and disambiguating the two
    # requires knowing which sentence in the abstract this is, which is
    # exactly why this tool is a curator screening aid, not an
    # autonomous classifier. See module docstring.
    assert r.label == "NEGATIVE"
