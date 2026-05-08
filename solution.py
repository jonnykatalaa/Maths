"""
Numerical Analysis Homework 2025-2026
NTUA, School of Mechanical Engineering
K. Giannakoglou / V. Asouti

Student key digits (last 3 digits of registration number):
    K1 = 6, K2 = 6, K3 = 0

This single script solves all 7 problems from scratch (no black-box numerical
libraries are used for the underlying algorithms; numpy is used only for
arrays and dense linear-algebra; matplotlib is used only for plotting).

Run:
    python3 solution.py

It produces:
    plots/p1_bezier.png
    plots/p2_tangent.png
    plots/p4_eqspaced.png
    plots/p5_spline.png
    plots/p5_compare.png
    plots/p6_bspline.png
    plots/p7_intersections.png
    results.txt   (numerical tables / Newton-Raphson logs / Gauss quadrature)
"""

from __future__ import annotations

import os
from math import comb

import numpy as np
import matplotlib

matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Student key digits
# ---------------------------------------------------------------------------
K1, K2, K3 = 6, 6, 0


# ---------------------------------------------------------------------------
# Helpers: Bernstein basis, Bezier curve and its derivative
# ---------------------------------------------------------------------------
def bernstein(n: int, i: int, t):
    """Bernstein basis polynomial B_{i,n}(t) = C(n,i) t^i (1-t)^(n-i)."""
    return comb(n, i) * np.power(t, i) * np.power(1.0 - t, n - i)


def bezier(t, P):
    """Evaluate Bezier curve of degree n = len(P)-1 at t (scalar or 1-D array)."""
    P = np.asarray(P, dtype=float)
    n = len(P) - 1
    t = np.atleast_1d(np.asarray(t, dtype=float))
    out = np.zeros((t.size, P.shape[1]))
    for i in range(n + 1):
        b = bernstein(n, i, t)
        out += np.outer(b, P[i])
    return out


def bezier_deriv(t, P):
    """First derivative of Bezier curve (returns dx/dt, dy/dt)."""
    P = np.asarray(P, dtype=float)
    n = len(P) - 1
    Q = n * (P[1:] - P[:-1])  # control points of derivative (degree n-1)
    t = np.atleast_1d(np.asarray(t, dtype=float))
    out = np.zeros((t.size, P.shape[1]))
    for i in range(n):
        b = bernstein(n - 1, i, t)
        out += np.outer(b, Q[i])
    return out


# ---------------------------------------------------------------------------
# Gauss-Legendre nodes / weights for n = 2..5 on [-1, 1]
# (computed analytically from the Legendre-polynomial roots, NOT looked up
#  from a library at run-time)
# ---------------------------------------------------------------------------
def gauss_legendre(n: int):
    if n == 2:
        x = np.array([-1.0 / np.sqrt(3.0), 1.0 / np.sqrt(3.0)])
        w = np.array([1.0, 1.0])
    elif n == 3:
        x = np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)])
        w = np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0])
    elif n == 4:
        a = np.sqrt(3.0 / 7.0 - (2.0 / 7.0) * np.sqrt(6.0 / 5.0))
        b = np.sqrt(3.0 / 7.0 + (2.0 / 7.0) * np.sqrt(6.0 / 5.0))
        x = np.array([-b, -a, a, b])
        wa = (18.0 + np.sqrt(30.0)) / 36.0
        wb = (18.0 - np.sqrt(30.0)) / 36.0
        w = np.array([wb, wa, wa, wb])
    elif n == 5:
        a = (1.0 / 3.0) * np.sqrt(5.0 - 2.0 * np.sqrt(10.0 / 7.0))
        b = (1.0 / 3.0) * np.sqrt(5.0 + 2.0 * np.sqrt(10.0 / 7.0))
        x = np.array([-b, -a, 0.0, a, b])
        wa = (322.0 + 13.0 * np.sqrt(70.0)) / 900.0
        wb = (322.0 - 13.0 * np.sqrt(70.0)) / 900.0
        w0 = 128.0 / 225.0
        w = np.array([wb, wa, w0, wa, wb])
    else:
        raise ValueError("Gauss-Legendre only implemented for n in {2,3,4,5}.")
    return x, w


def gauss_integrate(f, a: float, b: float, n: int) -> float:
    """Approximate ∫_a^b f(t) dt by Gauss-Legendre with n nodes."""
    x, w = gauss_legendre(n)
    t = 0.5 * (b - a) * x + 0.5 * (a + b)
    vals = np.array([f(ti) for ti in t])
    return 0.5 * (b - a) * float(np.sum(w * vals))


# ---------------------------------------------------------------------------
# Natural cubic spline (Problem 5)
# ---------------------------------------------------------------------------
def natural_cubic_spline(x: np.ndarray, y: np.ndarray):
    """Solve for the second derivatives M_i of a natural cubic spline.

    Returns the array M (one entry per data point, M[0] = M[n] = 0).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x) - 1  # number of intervals
    h = np.diff(x)

    # Tridiagonal system: M[0] = M[n] = 0,
    # h[i-1] M[i-1] + 2 (h[i-1]+h[i]) M[i] + h[i] M[i+1]
    #    = 6 ((y[i+1]-y[i])/h[i]  -  (y[i]-y[i-1])/h[i-1]),  i = 1..n-1.
    A = np.zeros((n + 1, n + 1))
    rhs = np.zeros(n + 1)
    A[0, 0] = 1.0
    A[n, n] = 1.0
    for i in range(1, n):
        A[i, i - 1] = h[i - 1]
        A[i, i] = 2.0 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        rhs[i] = 6.0 * (
            (y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1]
        )
    M = np.linalg.solve(A, rhs)
    return M


def eval_natural_spline(x_eval, x: np.ndarray, y: np.ndarray, M: np.ndarray):
    """Evaluate the natural cubic spline at x_eval (scalar or array)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    M = np.asarray(M, dtype=float)
    h = np.diff(x)

    def _eval_one(xv: float) -> float:
        # find segment i such that x[i] <= xv <= x[i+1]
        i = int(np.searchsorted(x, xv) - 1)
        i = max(0, min(i, len(x) - 2))
        u = x[i + 1] - xv
        t = xv - x[i]
        hi = h[i]
        return (
            (M[i] * u ** 3 + M[i + 1] * t ** 3) / (6.0 * hi)
            + (y[i] / hi - M[i] * hi / 6.0) * u
            + (y[i + 1] / hi - M[i + 1] * hi / 6.0) * t
        )

    if np.isscalar(x_eval):
        return _eval_one(float(x_eval))
    return np.array([_eval_one(float(v)) for v in np.asarray(x_eval)])


# ---------------------------------------------------------------------------
# Uniform cubic B-spline interpolation (Problem 6)
# ---------------------------------------------------------------------------
# Curve segment k (k = 0..N-2 where data has N points) is
#   S_k(t) = (1/6) [ (1-t)^3 P_k    +  (3 t^3 - 6 t^2 + 4) P_{k+1}
#                 + (-3 t^3 + 3 t^2 + 3 t + 1) P_{k+2}  +  t^3 P_{k+3} ],
# t ∈ [0, 1], with control points P_0 .. P_{N+1}  (N+2 in total).
# Interpolation conditions:  S_k(0) = data_k, k = 0..N-2,  S_{N-2}(1) = data_{N-1}
# Equivalent compact form:   (P_k + 4 P_{k+1} + P_{k+2}) / 6 = data_k,  k = 0..N-1.
# Two extra equations are needed; we use the natural BCs S''(0) = S''(end) = 0
# which translate to:   P_0 - 2 P_1 + P_2 = 0,
#                       P_{N-1} - 2 P_N + P_{N+1} = 0.
def cubic_bspline_basis(t: float):
    return np.array(
        [
            (1.0 - t) ** 3,
            3.0 * t ** 3 - 6.0 * t ** 2 + 4.0,
            -3.0 * t ** 3 + 3.0 * t ** 2 + 3.0 * t + 1.0,
            t ** 3,
        ]
    ) / 6.0


def cubic_bspline_basis_deriv(t: float):
    return np.array(
        [
            -3.0 * (1.0 - t) ** 2,
            9.0 * t ** 2 - 12.0 * t,
            -9.0 * t ** 2 + 6.0 * t + 3.0,
            3.0 * t ** 2,
        ]
    ) / 6.0


def bspline_segment(t: float, P0, P1, P2, P3):
    b = cubic_bspline_basis(t)
    return b[0] * P0 + b[1] * P1 + b[2] * P2 + b[3] * P3


def bspline_curve_eval(u: float, cps: np.ndarray) -> np.ndarray:
    """Evaluate uniform cubic B-spline at u in [0, n_seg] where n_seg = len(cps)-3."""
    n_seg = len(cps) - 3
    if u < 0:
        u = 0.0
    if u > n_seg:
        u = float(n_seg)
    seg = int(min(int(u), n_seg - 1))
    t = u - seg
    return bspline_segment(t, cps[seg], cps[seg + 1], cps[seg + 2], cps[seg + 3])


def interpolating_cubic_bspline(data: np.ndarray) -> np.ndarray:
    """Return the (N+2) control points of the natural interpolating B-spline."""
    N = len(data)  # number of data points
    A = np.zeros((N + 2, N + 2))
    rhs = np.zeros((N + 2, data.shape[1]))

    # Natural BC at start:  P_0 - 2 P_1 + P_2 = 0
    A[0, 0] = 1.0
    A[0, 1] = -2.0
    A[0, 2] = 1.0
    # Interpolation conditions (rows 1 .. N)
    for k in range(N):
        A[k + 1, k] = 1.0 / 6.0
        A[k + 1, k + 1] = 4.0 / 6.0
        A[k + 1, k + 2] = 1.0 / 6.0
        rhs[k + 1] = data[k]
    # Natural BC at end:  P_{N-1} - 2 P_N + P_{N+1} = 0
    A[N + 1, N - 1] = 1.0
    A[N + 1, N] = -2.0
    A[N + 1, N + 1] = 1.0

    Px = np.linalg.solve(A, rhs[:, 0])
    Py = np.linalg.solve(A, rhs[:, 1])
    return np.column_stack([Px, Py])


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
PLOTS = "plots"
os.makedirs(PLOTS, exist_ok=True)
RESULTS_LINES: list[str] = []


def log(line: str = "") -> None:
    print(line)
    RESULTS_LINES.append(line)


# ===========================================================================
# Problem 1 + 2 : Bezier curve and tangent angle
# ===========================================================================
log("=" * 72)
log("PROBLEM 1 - Bezier curve")
log("=" * 72)

P_bz = np.array(
    [
        [0.0, 0.0],
        [3.0, 4.0 + K2 / 12.0],
        [4.0 + K1 / 10.0, 10.0],
        [5.5, 3.0],
        [6.0, 5.0 + K3 / 8.0],
        [7.0, 0.0],
    ]
)
log("Control points (K1=%d, K2=%d, K3=%d):" % (K1, K2, K3))
for i, pt in enumerate(P_bz):
    log(f"  P{i} = ({pt[0]:.6f}, {pt[1]:.6f})")

# Symbolic-style printout of the parametric polynomials -------------------
# x(t) = sum_{i=0..5} C(5,i) t^i (1-t)^(5-i) * X_i
# y(t) = sum_{i=0..5} C(5,i) t^i (1-t)^(5-i) * Y_i
log("")
log("Parametric form (degree-5 Bezier):")
log("  x(t) = Σ_{i=0..5}  C(5,i) t^i (1-t)^(5-i) X_i")
log("  y(t) = Σ_{i=0..5}  C(5,i) t^i (1-t)^(5-i) Y_i,   t ∈ [0,1]")
log("with the X_i, Y_i listed above.")

# Expanded polynomial form (collected powers of t)
def expand_bezier_poly(P):
    """Return coefficients of t^0..t^n for x(t) and y(t)."""
    n = len(P) - 1
    coeffs = np.zeros((n + 1, P.shape[1]))
    # x(t) = Σ C(n,i) X_i  t^i (1-t)^(n-i)
    # expand (1-t)^(n-i) = Σ_{j=0..n-i} C(n-i,j) (-1)^j t^j
    for i in range(n + 1):
        for j in range(n - i + 1):
            c = comb(n, i) * comb(n - i, j) * (-1) ** j
            coeffs[i + j] += c * P[i]
    return coeffs


coeffs_xy = expand_bezier_poly(P_bz)
log("")
log("Expanded polynomial form  x(t)=Σ a_k t^k,  y(t)=Σ b_k t^k:")
log("    k :   a_k (x)        b_k (y)")
for k, (ax, ay) in enumerate(coeffs_xy):
    log(f"    {k} : {ax:14.6f}  {ay:14.6f}")

# 100 sample points
t_arr = np.linspace(0.0, 1.0, 100)
curve = bezier(t_arr, P_bz)

plt.figure(figsize=(8, 6))
plt.plot(curve[:, 0], curve[:, 1], "b-", lw=2, label="Bezier curve")
plt.plot(P_bz[:, 0], P_bz[:, 1], "ro--", alpha=0.5, label="Control polygon")
for i, (x, y) in enumerate(P_bz):
    plt.annotate(f"P{i}", (x, y), textcoords="offset points", xytext=(6, 6))
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title(f"Problem 1 – Bezier curve  (K1={K1}, K2={K2}, K3={K3})")
plt.savefig(os.path.join(PLOTS, "p1_bezier.png"), dpi=120, bbox_inches="tight")
plt.close()

# -------------------- Problem 2 : tangent angle --------------------
log("")
log("=" * 72)
log("PROBLEM 2 - Tangent angle distribution")
log("=" * 72)

deriv = bezier_deriv(t_arr, P_bz)
angles_deg = np.degrees(np.arctan2(deriv[:, 1], deriv[:, 0]))

plt.figure(figsize=(8, 6))
plt.plot(t_arr, angles_deg, "b-", lw=2)
plt.grid(True)
plt.xlabel("t")
plt.ylabel("tangent angle θ(t) [degrees]")
plt.title("Problem 2 – Tangent angle along the Bezier curve")
plt.savefig(os.path.join(PLOTS, "p2_tangent.png"), dpi=120, bbox_inches="tight")
plt.close()

log("Tangent angle θ(t) = atan2(dy/dt, dx/dt). Sampled at the same 100 t.")
log("  θ(0)   = %8.3f deg" % angles_deg[0])
log("  θ(0.5) = %8.3f deg" % np.degrees(np.arctan2(*bezier_deriv(0.5, P_bz)[0][::-1])))
log("  θ(1)   = %8.3f deg" % angles_deg[-1])

# ===========================================================================
# Problem 3 : Volume of revolution around the x axis
# ===========================================================================
log("")
log("=" * 72)
log("PROBLEM 3 - Volume of revolution by Gauss-Legendre quadrature")
log("=" * 72)
log("V = π ∫_0^7 y(x)^2 dx = π ∫_0^1 y(t)^2 x'(t) dt")
log("Integrand g(t) = y(t)^2 · x'(t) is a polynomial of degree 5·2 + 4 = 14.")
log("A Gauss rule with m nodes integrates polynomials of degree 2m-1 exactly,")
log("so m ≥ 8 are required for an EXACT answer.  m = 2..5 are therefore")
log("approximations; we tabulate them next to the exact analytic value V*")
log("obtained by symbolic polynomial expansion + term-by-term integration.")


def volume_integrand(t: float) -> float:
    p = bezier(t, P_bz)[0]
    dp = bezier_deriv(t, P_bz)[0]
    return p[1] ** 2 * dp[0]


# Exact analytic value of the integral via polynomial multiplication
def _poly_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.zeros(len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return out


x_coef = coeffs_xy[:, 0]                                    # x(t) coeffs, deg 5
y_coef = coeffs_xy[:, 1]                                    # y(t) coeffs, deg 5
xprime_coef = np.array(                                     # x'(t)         deg 4
    [k * x_coef[k] for k in range(1, len(x_coef))]
)
y2_coef = _poly_mul(y_coef, y_coef)                         # y²(t)         deg 10
g_coef = _poly_mul(y2_coef, xprime_coef)                    # integrand     deg 14
V_exact = float(np.pi * sum(g_coef[k] / (k + 1) for k in range(len(g_coef))))

volumes: dict[int, float] = {}
for m in (2, 3, 4, 5):
    volumes[m] = np.pi * gauss_integrate(volume_integrand, 0.0, 1.0, m)

log("")
log(f"  Exact analytic value:  V* = {V_exact:.12f}")
log("")
log("  m |        V(m)              |   |V(m) - V*|")
log("  --+--------------------------+----------------")
for m in (2, 3, 4, 5):
    err = abs(volumes[m] - V_exact)
    log(f"  {m} |  {volumes[m]:22.12f}  |  {err:.6e}")

# ===========================================================================
# Problem 4 : 8 equally-x-spaced points via Newton-Raphson
# ===========================================================================
log("")
log("=" * 72)
log("PROBLEM 4 - Eight equally x-spaced points (Newton-Raphson)")
log("=" * 72)

x_targets = np.linspace(0.0, 7.0, 8)


def newton_raphson_for_x(x_target: float, t0: float, tol: float = 1e-12,
                         max_iter: int = 50):
    """Solve x(t) - x_target = 0 by Newton-Raphson; returns (t*, log)."""
    t = t0
    history = []
    for k in range(max_iter):
        x_t = bezier(t, P_bz)[0, 0]
        dx_t = bezier_deriv(t, P_bz)[0, 0]
        f = x_t - x_target
        history.append((k, t, x_t, f))
        if abs(f) < tol:
            break
        t = t - f / dx_t
        if t < 0.0:
            t = 0.0
        if t > 1.0:
            t = 1.0
    return t, history


t_pts: list[float] = []
xy_pts: list[tuple[float, float]] = []
nr_logs: dict[float, list] = {}
for xt in x_targets:
    t_init = float(xt) / 7.0  # uniform initial guess
    t_star, hist = newton_raphson_for_x(float(xt), t_init)
    p_star = bezier(t_star, P_bz)[0]
    t_pts.append(t_star)
    xy_pts.append((float(p_star[0]), float(p_star[1])))
    nr_logs[float(xt)] = hist

log("Newton-Raphson update:  t_{k+1} = t_k - (x(t_k) - x*) / x'(t_k)")
log("Initial guess t_0 = x*/7 (linear in x*).")
log("")
log("    i |   x_i (target) |    t_i      |    y_i     | iters")
log("   ---+----------------+-------------+------------+-------")
for i, (xt, (x, y)) in enumerate(zip(x_targets, xy_pts)):
    log(f"    {i} | {xt:14.6f} | {t_pts[i]:11.8f} | {y:10.6f} | {len(nr_logs[float(xt)])}")

# Detailed convergence printout for two representative targets (x=2 and x=5)
for xt in (2.0, 5.0):
    log("")
    log(f"Newton-Raphson convergence for x* = {xt:.1f}:")
    log("    k |     t_k        |   x(t_k)    |  f = x(t_k)-x*")
    log("   ---+----------------+-------------+----------------")
    for (k, t_k, x_k, f_k) in nr_logs[xt]:
        log(f"    {k} | {t_k:14.10f} | {x_k:11.8f} | {f_k:14.6e}")

# Plot Problem 4
xs_pts = np.array([p[0] for p in xy_pts])
ys_pts = np.array([p[1] for p in xy_pts])
plt.figure(figsize=(8, 6))
plt.plot(curve[:, 0], curve[:, 1], "b-", lw=2, label="Bezier curve")
plt.plot(xs_pts, ys_pts, "ro", markersize=8, label="8 equally-x-spaced points")
for i, (x, y) in enumerate(xy_pts):
    plt.annotate(f"{i}", (x, y), textcoords="offset points", xytext=(6, 6))
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Problem 4 – 8 equally-x-spaced points on the Bezier curve")
plt.savefig(os.path.join(PLOTS, "p4_eqspaced.png"), dpi=120, bbox_inches="tight")
plt.close()

# ===========================================================================
# Problem 5 : Natural cubic spline through these 8 points
# ===========================================================================
log("")
log("=" * 72)
log("PROBLEM 5 - Natural cubic spline through the 8 points of problem 4")
log("=" * 72)

M_spline = natural_cubic_spline(xs_pts, ys_pts)
log("Second derivatives (M_i = S''(x_i)):  with M_0 = M_7 = 0  (natural BCs).")
for i, mi in enumerate(M_spline):
    log(f"  M_{i} = {mi:14.8f}")

x_dense = np.linspace(0.0, 7.0, 400)
y_spline_dense = eval_natural_spline(x_dense, xs_pts, ys_pts, M_spline)

plt.figure(figsize=(8, 6))
plt.plot(x_dense, y_spline_dense, "g-", lw=2, label="Natural cubic spline")
plt.plot(xs_pts, ys_pts, "ro", markersize=8, label="interpolation points")
plt.grid(True)
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Problem 5 – Natural cubic spline through 8 points")
plt.savefig(os.path.join(PLOTS, "p5_spline.png"), dpi=120, bbox_inches="tight")
plt.close()

plt.figure(figsize=(8, 6))
plt.plot(curve[:, 0], curve[:, 1], "b-", lw=2, label="Bezier (problem 1)")
plt.plot(x_dense, y_spline_dense, "g--", lw=2, label="Natural cubic spline (Q5)")
plt.plot(xs_pts, ys_pts, "ro", markersize=7, label="8 common points")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Problem 5 – Bezier vs. natural cubic spline")
plt.savefig(os.path.join(PLOTS, "p5_compare.png"), dpi=120, bbox_inches="tight")
plt.close()

# ===========================================================================
# Problem 6 : Cubic B-spline interpolation through 5 given points
# ===========================================================================
log("")
log("=" * 72)
log("PROBLEM 6 - Interpolating cubic B-spline (uniform knots, natural BCs)")
log("=" * 72)

data6 = np.array(
    [
        [0.5, 6.0],
        [2.0, 2.0 + K2 / 12.0],
        [4.0 + K1 / 10.0, 1.0],
        [5.0, 4.0],
        [6.0, 8.0 + K3 / 8.0],
    ]
)
log("Data points (5):")
for i, pt in enumerate(data6):
    log(f"  Q{i} = ({pt[0]:.6f}, {pt[1]:.6f})")

cps6 = interpolating_cubic_bspline(data6)
log("")
log("Resulting B-spline control points (7 in total, P_0 .. P_6):")
for i, pt in enumerate(cps6):
    log(f"  P_{i} = ({pt[0]:.6f}, {pt[1]:.6f})")

# Print the explicit polynomial of every segment, in t ∈ [0,1]
log("")
log("Explicit polynomials for each of the 4 segments  (t ∈ [0,1]):")
log("Each segment k uses control points P_k, P_{k+1}, P_{k+2}, P_{k+3} and")
log("has the form  S_k(t) = α_0 + α_1 t + α_2 t^2 + α_3 t^3  for x and y.")
# basis -> monomial conversion
# B0 = ( -t^3 + 3 t^2 - 3 t + 1) / 6
# B1 = ( 3 t^3 - 6 t^2       + 4) / 6
# B2 = (-3 t^3 + 3 t^2 + 3 t + 1) / 6
# B3 = (   t^3                  ) / 6
basis_to_mono = (
    np.array(
        [
            [+1, -3, +3, -1],  # constant, t, t^2, t^3 of B0
            [+4,  0, -6, +3],  # B1
            [+1, +3, +3, -3],  # B2
            [ 0,  0,  0, +1],  # B3
        ]
    )
    / 6.0
)
for k in range(len(cps6) - 3):
    Pk = cps6[k : k + 4]            # 4 x 2 array
    coeffs = basis_to_mono.T @ Pk   # (4 monomial powers) x 2  (x and y columns)
    log(f"  Segment {k+1}/4  (between Q_{k} and Q_{k+1}):")
    for power in range(4):
        log(
            f"    t^{power}: x-coeff = {coeffs[power, 0]:12.6f}, "
            f"y-coeff = {coeffs[power, 1]:12.6f}"
        )

# Sanity check : interpolation conditions
log("")
log("Sanity check at the data points:")
log("   k |   target (x,y)             |  S_k(0)")
n_seg = len(cps6) - 3
for k in range(n_seg + 1):  # 5 conditions: S_0(0)..S_3(0) and S_3(1)
    if k < n_seg:
        v = bspline_segment(0.0, *cps6[k:k + 4])
    else:
        v = bspline_segment(1.0, *cps6[n_seg - 1: n_seg + 3])
    log(f"   {k} | ({data6[k,0]:8.5f}, {data6[k,1]:8.5f}) "
        f"| ({v[0]:8.5f}, {v[1]:8.5f})")

# Sample curve for plotting
n_dense = 400
us = np.linspace(0.0, n_seg, n_dense)
bsp_curve = np.array([bspline_curve_eval(u, cps6) for u in us])

plt.figure(figsize=(8, 6))
plt.plot(bsp_curve[:, 0], bsp_curve[:, 1], "m-", lw=2, label="Cubic B-spline")
plt.plot(data6[:, 0], data6[:, 1], "ko", markersize=8, label="data points")
plt.plot(cps6[:, 0], cps6[:, 1], "c--", alpha=0.6, label="control polygon")
for i, (x, y) in enumerate(cps6):
    plt.annotate(f"P{i}", (x, y), textcoords="offset points", xytext=(5, 5),
                 fontsize=8, color="c")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Problem 6 – Cubic B-spline interpolation of 5 points")
plt.savefig(os.path.join(PLOTS, "p6_bspline.png"), dpi=120, bbox_inches="tight")
plt.close()

# ===========================================================================
# Problem 7 : Intersections of the cubic spline (Q5) with the B-spline (Q6)
# ===========================================================================
log("")
log("=" * 72)
log("PROBLEM 7 - Intersections (fixed-point iteration)")
log("=" * 72)

# Cubic spline (Q5) is y = y_s(x) for x ∈ [x_0, x_7] = [0, 7].
# B-spline curve (Q6) is parametric (x_b(u), y_b(u)) for u ∈ [0, 4].
# An intersection satisfies   F(u) := y_b(u) - y_s(x_b(u)) = 0
# AND also x_b(u) ∈ [0, 7] (which is true throughout because x_b ∈ [0.5, 6]).
#
# Fixed-point form:  u = G(u) := u - α F(u),
# with α a constant; convergence requires |G'(u*)| < 1, i.e. 0 < α F'(u*) < 2.
# We set α automatically from a numerical estimate of F'(u_0).

def F7(u: float) -> float:
    pt = bspline_curve_eval(u, cps6)
    return pt[1] - eval_natural_spline(pt[0], xs_pts, ys_pts, M_spline)


def fixed_point(u0: float, alpha: float, tol: float = 1e-10,
                max_iter: int = 500):
    u = u0
    history = [(0, u, F7(u))]
    for k in range(1, max_iter + 1):
        f = F7(u)
        u_new = u - alpha * f
        # keep within parameter range
        u_new = max(0.0, min(float(n_seg) - 1e-12, u_new))
        history.append((k, u_new, F7(u_new)))
        if abs(u_new - u) < tol and abs(history[-1][2]) < tol:
            return u_new, history
        u = u_new
    return u, history


# Locate sign changes of F on [0, n_seg] using a fine sampling.
u_samp = np.linspace(0.0, float(n_seg) - 1e-9, 4000)
F_samp = np.array([F7(u) for u in u_samp])
brackets: list[tuple[float, float]] = []
for i in range(len(u_samp) - 1):
    if F_samp[i] * F_samp[i + 1] < 0:
        brackets.append((u_samp[i], u_samp[i + 1]))
log(f"Detected {len(brackets)} sign changes of F(u) on [0,{n_seg}]:")
for lo, hi in brackets:
    log(f"  bracket  u ∈ [{lo:.6f}, {hi:.6f}]")

intersections: list[tuple[float, float, float]] = []
for idx, (lo, hi) in enumerate(brackets):
    u0 = 0.5 * (lo + hi)
    eps = 1e-4
    Fp = (F7(u0 + eps) - F7(u0 - eps)) / (2.0 * eps)
    if Fp == 0.0:
        alpha = 0.05 * (1.0 if F7(u0) >= 0 else -1.0)
    else:
        alpha = 1.0 / Fp  # gives |1 - α F'| ≈ 0 near u_0  (rapid contraction)
    u_star, hist = fixed_point(u0, alpha)
    pt = bspline_curve_eval(u_star, cps6)
    intersections.append((u_star, float(pt[0]), float(pt[1])))
    log("")
    log(f"Intersection {idx+1}: starting bracket [{lo:.4f}, {hi:.4f}], "
        f"α = {alpha:.6f}")
    log(f"    converged to  u* = {u_star:.10f},  "
        f"(x*, y*) = ({pt[0]:.8f}, {pt[1]:.8f})  in {len(hist)-1} iterations")
    log("    iter |        u_k         |       F(u_k)")
    log("    -----+--------------------+-------------------")
    show = hist if len(hist) <= 12 else hist[:6] + [("...", "...", "...")] + hist[-5:]
    for entry in show:
        if entry[0] == "...":
            log("     ... |        ...         |        ...")
        else:
            k, uk, fk = entry
            log(f"    {k:5d} | {uk:18.12f} | {fk:18.6e}")

plt.figure(figsize=(8, 6))
plt.plot(x_dense, y_spline_dense, "g-", lw=2, label="Cubic spline (Q5)")
plt.plot(bsp_curve[:, 0], bsp_curve[:, 1], "m-", lw=2, label="Cubic B-spline (Q6)")
for i, (u, x, y) in enumerate(intersections):
    plt.plot(x, y, "r*", markersize=15)
    plt.annotate(f" I{i+1}", (x, y), textcoords="offset points", xytext=(6, 4),
                 color="r", fontsize=10)
plt.grid(True)
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Problem 7 – Intersections (cubic spline ∩ cubic B-spline)")
plt.savefig(os.path.join(PLOTS, "p7_intersections.png"), dpi=120, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# Write a short results.txt that mirrors the console output
# ---------------------------------------------------------------------------
with open("results.txt", "w") as fh:
    fh.write("\n".join(RESULTS_LINES) + "\n")

print()
print("Done.  Plots are in ./plots/   numerical results in ./results.txt")
