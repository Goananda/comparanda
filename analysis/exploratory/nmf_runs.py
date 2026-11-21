"""How many of the twelve complexes come back from other random starting points.

Usage: python3 nmf_runs.py <work_dir>
Six further runs of the factorisation (random initialisation, seeds 11-16) are compared with the solution saved by nmf.py:
each of its components is paired with a component of the run, and the cosine of their motif loadings is printed.
"""
import sys, warnings
warnings.filterwarnings('ignore')
import numpy as np
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
from scipy.optimize import linear_sum_assignment
W = sys.argv[1]
X = np.load(f'{W}/X.npy').astype(float); kg = X.sum(1) >= 15; km = X[kg].sum(0) >= 5; Xs = X[kg][:, km]
W0 = normalize(Xs * np.log(Xs.shape[0] / Xs.sum(0))); H0 = normalize(np.load(f'{W}/nmf_H_12.npy'))
for seed in range(11, 17):
    m = NMF(12, init='random', random_state=seed, max_iter=600, tol=1e-5); m.fit(W0)
    S = H0 @ normalize(m.components_).T; r, c = linear_sum_assignment(-S); v = np.sort(S[r, c])[::-1]
    print(f'seed {seed}: err {m.reconstruction_err_:.3f}; matched at >= 0.95: {(v >= 0.95).sum()}; at >= 0.75: {(v >= 0.75).sum()}; cosines {np.round(v, 2)}', flush=True)
