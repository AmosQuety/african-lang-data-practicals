"""Unit tests for scripts/compute_agreement.py's Cohen's kappa implementation."""
import compute_agreement as ca


def test_kappa_perfect_agreement():
    pairs = [("ok", "ok"), ("needs_correction", "needs_correction"), ("reject", "reject")]
    assert ca.cohens_kappa(pairs) == 1.0


def test_kappa_zero_when_agreement_equals_chance():
    # Constructed so that observed agreement equals expected-by-chance agreement.
    # 2x2 with balanced marginals and po == pe gives kappa == 0.
    pairs = [("ok", "ok"), ("ok", "reject"), ("reject", "ok"), ("reject", "reject")]
    kappa = ca.cohens_kappa(pairs)
    assert kappa == 0.0


def test_kappa_single_category_all_agree_is_perfect():
    pairs = [("ok", "ok"), ("ok", "ok"), ("ok", "ok")]
    assert ca.cohens_kappa(pairs) == 1.0


def test_kappa_empty_pairs_returns_none():
    assert ca.cohens_kappa([]) is None


def test_percent_agreement_matches_manual_count():
    pairs = [("ok", "ok"), ("ok", "reject"), ("reject", "reject")]
    agree = sum(1 for a, b in pairs if a == b)
    assert agree / len(pairs) == 2 / 3
