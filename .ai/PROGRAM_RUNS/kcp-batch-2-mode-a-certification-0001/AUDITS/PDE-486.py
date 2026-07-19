"""Deterministic audit for PDE-486 (separation of variables, eigenvalue problem).

Every assertion corresponds to a claim the node makes.  Claims not asserted here
must not be described as machine-checked.

Scope honesty: this audit verifies the Dirichlet string case on [0, L] as the
concrete Sturm-Liouville instance the node teaches.  It does NOT prove the
general Sturm-Liouville spectral theorem or completeness of the eigenbasis;
those remain textbook results cited by the node, not machine-checked here.
"""

from __future__ import annotations

import sympy as sp

RESULTS: list[tuple[str, str]] = []


def check(claim: str, condition: bool) -> None:
    assert condition, f"FAILED: {claim}"
    RESULTS.append((claim, "PASS"))


x = sp.Symbol("x", real=True)
t = sp.Symbol("t", real=True)
L = sp.Symbol("L", positive=True, real=True)
c = sp.Symbol("c", positive=True, real=True)
n, m = sp.symbols("n m", positive=True, integer=True)


def eigenfunction(k):
    return sp.sin(k * sp.pi * x / L)


def eigenvalue(k):
    return (k * sp.pi / L) ** 2


# --- sub_topic 1: the eigenvalue problem itself ----------------------------
for k in (1, 2, 3):
    y = eigenfunction(k)
    lam = eigenvalue(k)
    check(
        f"y_{k} satisfies y'' + lambda*y == 0 with lambda = ({k}pi/L)^2",
        sp.simplify(sp.diff(y, x, 2) + lam * y) == 0,
    )
    check(
        f"y_{k} satisfies the Dirichlet boundary conditions y(0)=y(L)=0",
        sp.simplify(y.subs(x, 0)) == 0 and sp.simplify(y.subs(x, L)) == 0,
    )

check(
    "eigenvalues are strictly increasing: lambda_1 < lambda_2 < lambda_3",
    sp.simplify(eigenvalue(2) - eigenvalue(1)).is_positive is True
    and sp.simplify(eigenvalue(3) - eigenvalue(2)).is_positive is True,
)

# --- sub_topic 2: orthogonality and normalisation --------------------------
for j, k in ((1, 2), (1, 3), (2, 3), (2, 4)):
    integral = sp.integrate(eigenfunction(j) * eigenfunction(k), (x, 0, L))
    check(
        f"eigenfunctions {j} and {k} are orthogonal on [0,L]",
        sp.simplify(integral) == 0,
    )

for k in (1, 2, 3):
    norm_sq = sp.integrate(eigenfunction(k) ** 2, (x, 0, L))
    check(
        f"||y_{k}||^2 == L/2 (nonzero, so the basis is normalisable)",
        sp.simplify(norm_sq - L / 2) == 0,
    )

# Sampled (not general) orthogonality check.  The name says "sampled" because only
# the listed integer pairs are substituted; this is NOT a general symbolic proof.
general = sp.integrate(
    sp.sin(n * sp.pi * x / L) * sp.sin(m * sp.pi * x / L), (x, 0, L)
)
check(
    "sampled integer pairs (2,5) and (3,7): integral of sin(n pi x/L) sin(m pi x/L) "
    "vanishes; sampled evidence only, not a general symbolic proof",
    sp.simplify(general.subs({n: 2, m: 5})) == 0
    and sp.simplify(general.subs({n: 3, m: 7})) == 0,
)

# --- sub_topic 3: separation of variables actually separates ---------------
X = sp.Function("X")
T = sp.Function("T")
u = X(x) * T(t)
wave_residual = sp.diff(u, t, 2) - c**2 * sp.diff(u, x, 2)
# dividing by c^2 X T must split into a pure-t term and a pure-x term
separated = sp.simplify(sp.expand(wave_residual / (c**2 * X(x) * T(t))))
t_part = sp.diff(T(t), t, 2) / (c**2 * T(t))
x_part = sp.diff(X(x), x, 2) / X(x)
check(
    "wave equation separates as T''/(c^2 T) - X''/X == 0",
    sp.simplify(separated - (t_part - x_part)) == 0,
)

# --- sub_topic 4: modal superposition solves the PDE -----------------------
A1, A2 = sp.symbols("A1 A2", real=True)
u_modal = A1 * sp.sin(sp.pi * x / L) * sp.cos(c * sp.pi * t / L) + A2 * sp.sin(
    2 * sp.pi * x / L
) * sp.cos(2 * c * sp.pi * t / L)
check(
    "a two-mode superposition satisfies the wave equation u_tt = c^2 u_xx",
    sp.simplify(sp.diff(u_modal, t, 2) - c**2 * sp.diff(u_modal, x, 2)) == 0,
)
check(
    "the superposition still satisfies both boundary conditions",
    sp.simplify(u_modal.subs(x, 0)) == 0 and sp.simplify(u_modal.subs(x, L)) == 0,
)

# Fourier coefficient extraction works because of orthogonality
target = 3 * sp.sin(sp.pi * x / L) - 5 * sp.sin(2 * sp.pi * x / L)
coeff1 = sp.simplify(
    sp.integrate(target * eigenfunction(1), (x, 0, L)) / (L / 2)
)
coeff2 = sp.simplify(
    sp.integrate(target * eigenfunction(2), (x, 0, L)) / (L / 2)
)
check(
    "orthogonality recovers coefficients 3 and -5 from a known combination",
    sp.simplify(coeff1 - 3) == 0 and sp.simplify(coeff2 + 5) == 0,
)

# --- boundary: linear + homogeneous does NOT imply separable ----------------
# Counterexample: x*y*u_xx + u_yy = 0 is linear and homogeneous, yet dividing by
# X(x)Y(y) leaves a term depending on both variables.  If the quotient could be
# split as f(x) + g(y), its mixed second partial would vanish; it does not.
y_var = sp.Symbol("y", real=True)
Xf, Yf = sp.Function("X"), sp.Function("Y")
product = Xf(x) * Yf(y_var)
non_separable = x * y_var * sp.diff(product, x, 2) + sp.diff(product, y_var, 2)
quotient = sp.simplify(non_separable / product)
mixed_partial = sp.simplify(sp.diff(quotient, x, y_var))
check(
    "counterexample x*y*u_xx + u_yy = 0 is linear and homogeneous but NOT separable "
    "(mixed partial of the quotient is nonzero), so separability is an extra hypothesis",
    mixed_partial != 0,
)

# --- boundary: what this audit does NOT establish --------------------------
check(
    "a non-eigenfunction (x) fails the Dirichlet condition at x=L, so not every "
    "smooth function is an eigenfunction",
    sp.simplify(x.subs(x, L) - L) == 0 and sp.simplify(L) != 0,
)

if __name__ == "__main__":
    for claim, status in RESULTS:
        print(f"[{status}] {claim}")
    print(f"TOTAL {len(RESULTS)} assertions, all passed")
