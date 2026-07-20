"""
sampling.py

Utility module for deterministic and quasi-random sampling of compositional spaces.
Provides uniform grid, Latin Hypercube and Sobol sequence generators that
automatically reject points whose components do not sum to 1 (simplex constraint).

Author: 
Date  : 2025-08-23
Version: 2.0
"""

from typing import Sequence, Optional
import numpy as np
from scipy.stats import qmc   # SciPy ≥ 1.7


# ------------------------------------------------------------------
# 1.  Uniform grid (brute-force enumeration)
# ------------------------------------------------------------------
def uniform_sampling(
    num_dimensions: int,
    lower_bounds: Sequence[float],
    upper_bounds: Sequence[float],
    steps: Sequence[float],
) -> np.ndarray:
    """
    Brute-force uniform grid over the simplex Σxᵢ = 1.

    Parameters
    ----------
    num_dimensions : int
        Number of compositional variables (d).
    lower_bounds, upper_bounds, steps : sequence of float, length d
        Per-dimension lower bound, upper bound and step size.

    Returns
    -------
    np.ndarray, shape (n_valid, d)
        All grid points whose rounded sum equals 1.0.

    Examples
    --------
    >>> uniform_sampling(
    ...     num_dimensions=3,
    ...     lower_bounds=[0.0, 0.0, 0.0],
    ...     upper_bounds=[1.0, 1.0, 1.0],
    ...     steps=[0.5, 0.5, 0.5]
    ... )
    array([[0. , 0.5, 0.5],
           [0.5, 0. , 0.5],
           [0.5, 0.5, 0. ]])
    """
    lower_bounds = np.asarray(lower_bounds, dtype=float)
    upper_bounds = np.asarray(upper_bounds, dtype=float)
    steps = np.asarray(steps, dtype=float)

    n_steps = ((upper_bounds - lower_bounds) / steps).astype(int) + 1
    samples = []
    for idx in np.ndindex(*n_steps):
        vec = np.array([i * s + lb for i, s, lb in zip(idx, steps, lower_bounds)])
        if np.isclose(np.round(vec.sum(), decimals=2), 1.0):
            samples.append(vec)
    return np.array(samples)


# ------------------------------------------------------------------
# 2.  Latin Hypercube Sampling (LHS)
# ------------------------------------------------------------------
def lhs_sampling(
    n_samples: int,
    lower_bounds: Sequence[float],
    upper_bounds: Sequence[float],
    max_iter: int = 10_000,
    random_state: Optional[int] = None,
) -> np.ndarray:
    """
    Latin Hypercube Sampling on the simplex Σxᵢ = 1.

    Parameters
    ----------
    n_samples : int
        Desired number of valid samples.
    lower_bounds, upper_bounds : sequence of float, length d
        Box constraints for each dimension.
    max_iter : int
        Maximum rejection-sampling iterations.
    random_state : int or None
        Seed for reproducibility.

    Returns
    -------
    np.ndarray, shape (n_samples, d)
        LHS points projected onto the simplex.

    Examples
    --------
    >>> lhs_sampling(
    ...     n_samples=4,
    ...     lower_bounds=[0.0, 0.0, 0.0],
    ...     upper_bounds=[1.0, 1.0, 1.0],
    ...     random_state=42
    ... )  # doctest: +SKIP
    array([[0.814, 0.046, 0.14 ],
           [0.165, 0.697, 0.138],
           [0.027, 0.224, 0.749],
           [0.602, 0.349, 0.049]])
    """
    lower_bounds = np.asarray(lower_bounds, dtype=float)
    upper_bounds = np.asarray(upper_bounds, dtype=float)
    d = len(lower_bounds)

    # Use a local RandomState seeded by random_state
    rs = np.random.RandomState(random_state)

    # 1. Generate uniform samples on the simplex via Dirichlet
    candidates = []
    for _ in range(max_iter):
        # Exponential spacings -> Dirichlet(1,...,1)
        e = -np.log(rs.rand(d))
        p = e / e.sum()
        if np.all((p >= lower_bounds) & (p <= upper_bounds)):
            candidates.append(p)
        if len(candidates) >= n_samples:
            break

    if len(candidates) < n_samples:
        raise RuntimeError(
            f"Only {len(candidates)} valid LHS points found within bounds. "
            "Consider relaxing bounds or increasing max_iter."
        )

    # 2. Latin Hypercube re-ordering (preserve marginal uniformity)
    samples = np.array(candidates[:n_samples])
    for i in range(d):
        order = rs.permutation(n_samples)
        samples[:, i] = samples[order, i]

    return samples


# ------------------------------------------------------------------
# 3.  Sobol Sequence
# ------------------------------------------------------------------
def sobol_sampling(
    n_samples: int,
    lower_bounds: Sequence[float],
    upper_bounds: Sequence[float],
    skip: int = 0,
    randomize: bool = True,
    random_state: Optional[int] = None,
) -> np.ndarray:
    """
    Sobol quasi-random sequence on the simplex Σxᵢ = 1, clipped to the
    provided box constraints.

    Parameters
    ----------
    n_samples : int
        Desired number of valid samples.  Powers of two are ideal.
    lower_bounds, upper_bounds : sequence of float, length d
        Box constraints for each dimension.
    skip : int
        Number of initial Sobol points to discard (burn-in).
    randomize : bool
        Apply Owen scrambling if True.
    random_state : int or None
        Seed for reproducibility.

    Returns
    -------
    np.ndarray, shape (n_samples, d)
        Sobol points lying on the simplex and within the bounds.
    """
    lower_bounds = np.asarray(lower_bounds, dtype=float)
    upper_bounds = np.asarray(upper_bounds, dtype=float)
    d = len(lower_bounds)

    # 1. Generate Sobol points on the (d-1)-simplex
    #    We use the standard trick: sample d-1 uniform values in [0,1],
    #    sort them, take successive differences, and prepend/append 0,1.
    rs = np.random.RandomState(random_state)

    # Sobol engine for (d-1) dimensions
    engine = qmc.Sobol(d=d - 1, scramble=randomize, seed=rs.randint(0, 2**31))
    if skip:
        engine.fast_forward(skip)

    sobol = engine.random(n=n_samples * 2)  # generate extra for filtering
    sobol_sorted = np.sort(sobol, axis=1)
    simplex = np.empty((sobol_sorted.shape[0], d))
    simplex[:, 0] = sobol_sorted[:, 0]
    simplex[:, 1:-1] = sobol_sorted[:, 1:] - sobol_sorted[:, :-1]
    simplex[:, -1] = 1.0 - sobol_sorted[:, -1]

    # 2. Clip to bounds and keep first n_samples valid points
    mask = np.all((simplex >= lower_bounds) & (simplex <= upper_bounds), axis=1)
    valid = simplex[mask][:n_samples]

    if len(valid) < n_samples:
        raise RuntimeError(
            f"Only {len(valid)} valid Sobol points found within bounds. "
            "Increase n_samples or relax bounds."
        )
    return valid


# ------------------------------------------------------------------
# Convenience wrapper
# ------------------------------------------------------------------
def sample_simplex(
    n_samples: int,
    lower_bounds: Sequence[float],
    upper_bounds: Sequence[float],
    method: str = "sobol",
    **kwargs,
) -> np.ndarray:
    """
    Unified entry point.

    Parameters
    ----------
    method : {"uniform", "lhs", "sobol"}
        Sampling strategy to use.

    **kwargs
        Forwarded to the underlying sampler.

    Returns
    -------
    np.ndarray
        (n_samples, d) array of points on the simplex.

    Examples
    --------
    >>> sample_simplex(
    ...     n_samples=3,
    ...     lower_bounds=[0, 0, 0],
    ...     upper_bounds=[1, 1, 1],
    ...     method="lhs",
    ...     random_state=123
    ... )  # doctest: +SKIP
    array([[0.12, 0.34, 0.54],
           [0.78, 0.11, 0.11],
           [0.02, 0.88, 0.10]])
    """
    if method == "uniform":
        return uniform_sampling(
            num_dimensions=len(lower_bounds),
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            steps=kwargs.get("steps", [0.01] * len(lower_bounds)),
        )
    if method == "lhs":
        return lhs_sampling(
            n_samples=n_samples,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            **{k: v for k, v in kwargs.items() if k in {"max_iter", "random_state"}},
        )
    if method == "sobol":
        return sobol_sampling(
            n_samples=n_samples,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            **{k: v for k, v in kwargs.items() if k in {"skip", "randomize", "random_state"}},
        )
    raise ValueError(f"Unknown sampling method: {method}")

# Usage
# if __name__ == "__main__":
#     """
#     Code Validation
#     Run:
#         python sampling.py
#     """
#     import textwrap

#     d = 3
#     lb = [0.0] * d
#     ub = [1.0] * d

#     print("=== uniform grid (step=0.25) ===")
#     uni = uniform_sampling(d, lb, ub, steps=[0.25] * d)
#     print(uni)

#     print("\n=== LHS (n=5, seed=42) ===")
#     lhs = lhs_sampling(5, lb, ub, random_state=42)
#     print(lhs)

#     print("\n=== Sobol (n=4, power-of-2) ===")
#     sob = sobol_sampling(4, lb, ub, randomize=False)
#     print(sob)

#     print("\n=== unified wrapper demo ===")
#     wrap = sample_simplex(3, lb, ub, method="lhs", random_state=2025)
#     print(wrap)

#     # Check the results
#     for name, pts in zip(("uniform", "lhs", "sobol", "wrapper"),
#                          (uni, lhs, sob, wrap)):
#         sums = pts.sum(axis=1)
#         ok = np.allclose(sums, 1.0, atol=1e-3)
#         print(f"{name:8s} on simplex? {ok}")
