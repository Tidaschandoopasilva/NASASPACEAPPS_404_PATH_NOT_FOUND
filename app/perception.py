"""Convert externally calibrated binary sensor reports into odds updates."""
from math import isfinite


def posterior_probability(prior, likelihood_ratio):
    if not 0 < prior < 1:
        raise ValueError('Prior must lie strictly between zero and one')
    if not isfinite(likelihood_ratio) or likelihood_ratio <= 0:
        raise ValueError('Supply a positive likelihood ratio from held-out calibration')
    return prior * likelihood_ratio / (1 - prior + prior * likelihood_ratio)
