"""Posterior sampling and two-observation lookahead for simulated mesh scouting."""
import numpy as np

from app.environment import PROFILES


def tail_loss(losses, tail=.1):
    values = np.sort(np.asarray(losses))
    count = max(1, int(np.ceil(len(values) * tail)))
    return float(values[-count:].mean())


def field_prior(index, condition):
    multiplier = PROFILES[condition].risk_multiplier
    mean = np.clip((.0005 + .018 * index**2) * multiplier, .0001, .25)
    return mean * 30, (1 - mean) * 30


def scout_options(routes, alpha, beta, seed):
    """Rank candidate itineraries by posterior loss and probe the most useful vertex."""
    if not routes:
        return [], []
    rng = np.random.default_rng(seed)
    cells = np.unique(np.concatenate(routes))
    a, b = alpha[cells].copy(), beta[cells].copy()
    scores, logs = [], []
    indices = [np.searchsorted(cells, route) for route in routes]
    for _ in range(2):
        samples = rng.beta(a, b, size=(256, len(cells)))

        def evaluate(fields):
            return [tail_loss(1 - np.exp(np.log1p(-fields[:, ix]).sum(axis=1)))
                    for ix in indices]

        scores = evaluate(samples)
        best = indices[int(np.argmin(scores))]
        candidates = np.unique(best[::max(1, len(best)//8)])
        candidates = [i for i in candidates if int(cells[i]) not in {log['vertex'] for log in logs}]
        if not candidates:
            break
        winner = None
        for candidate in candidates:
            row, col = divmod(int(cells[candidate]), 226)
            nearby = np.hypot(cells//226-row, cells%226-col)
            weights = np.exp(-nearby**2/8)
            observation_probability = samples[:, candidate].mean()
            outcomes = []
            for hazardous in (False, True):
                batch = rng.beta(a + weights*hazardous, b + weights*(not hazardous),
                                 size=samples.shape)
                outcomes.append(min(evaluate(batch)))
            improvement = min(scores) - np.dot([1-observation_probability, observation_probability],outcomes)
            if winner is None or improvement > winner[0]:
                winner = improvement, candidate, weights
        improvement, candidate, weights = winner
        hazardous = bool(rng.random() < a[candidate]/(a[candidate]+b[candidate]))
        a += weights*hazardous
        b += weights*(not hazardous)
        logs.append({'vertex':int(cells[candidate]),'hazardous':hazardous,
                     'estimated_tail_reduction':float(improvement)})
    samples = rng.beta(a, b, size=(512, len(cells)))
    return evaluate(samples), logs
