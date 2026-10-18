import pytest
from apps.stock_analyzer.deterministic import analyze


def uptrend():
    p = [100.0]
    for _ in range(59):
        p.append(round(p[-1] * 1.004, 2))
    return p


def downtrend():
    p = [150.0]
    for _ in range(59):
        p.append(round(p[-1] * 0.996, 2))
    return p


def test_uptrend_is_bullish():
    assert analyze(uptrend()).signal == "BULLISH"


def test_downtrend_is_bearish():
    assert analyze(downtrend()).signal == "BEARISH"


def test_deterministic_same_input_same_output():
    assert analyze(uptrend()).to_dict() == analyze(uptrend()).to_dict()


def test_short_series_has_no_sma():
    r = analyze([100.0, 101.0, 102.0])
    assert r.sma_20 is None and r.sma_50 is None


def test_rejects_bad_input():
    with pytest.raises(ValueError):
        analyze([])
    with pytest.raises(ValueError):
        analyze([100.0, -5.0])
