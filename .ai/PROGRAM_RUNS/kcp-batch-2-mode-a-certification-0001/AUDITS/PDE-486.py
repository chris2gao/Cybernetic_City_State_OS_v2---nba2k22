"""Deterministic audit for PDE-486 (separation of variables, eigenvalue problem).

Every assertion corresponds to a claim the node makes.  Claims not asserted here
must not be described as machine-checked.

Scope honesty: this audit verifies the Dirichlet string case on [0, L] as the
concrete Sturm-Liouville instance the node teaches.  It does NOT prove the
general Sturm-Liouville spectral theorem or completeness of the eigenbasis;
those remain textbook results cited by the node, not machine-checked here.
"""

from __future__ import annotations

import pathlib

import sympy as sp
import yaml

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

# --- the node's ACTUAL code_implementation, loaded and executed -------------
# Not a reimplementation: this reads PDE-486.yaml, executes the exact
# `code_implementation` text in a separate namespace, and calls the function it
# defines. An earlier version asserted against a separately written SymPy copy
# while calling it "the node snippet" - that proved nothing about the node.
#
# TRUST BOUNDARY - read before reusing this pattern:
#   `exec` here uses a SEPARATE NAMESPACE, which is not a security sandbox and
#   must never be described as one. A separate dict prevents accidental symbol
#   collision with this module; it prevents nothing else. Executed code retains
#   full interpreter capability, including filesystem and process access.
#
#   The only thing that makes this safe is provenance, not isolation: the code
#   comes from a TRACKED, REVIEWED node file at the fixed canonical path below.
#   Executing node code from an untracked, unreviewed or caller-supplied path
#   would be unsafe no matter what namespace it ran in.
_NODE_PATH = (
    pathlib.Path(__file__).resolve().parents[4]
    / "08_Domain_Applications"
    / "Math_Mentor"
    / "Pure_Math_Intuition_DB"
    / "PDE-486.yaml"
)
with _NODE_PATH.open("r", encoding="utf-8") as _handle:
    _node = yaml.safe_load(_handle)

_namespace: dict = {}
# Separate namespace only; see the TRUST BOUNDARY note above. Safety here rests
# on _NODE_PATH being the tracked, reviewed canonical node file.
exec(compile(_node["code_implementation"], str(_NODE_PATH) + ":code_implementation", "exec"), _namespace)
_string_modal_sum = _namespace["string_modal_sum"]

A1s, B1s, A2s = sp.symbols("A1s B1s A2s", real=True)
snippet = _string_modal_sum(x, t, L, c, [(1, A1s, B1s), (2, A2s, 0)])
check(
    "node code_implementation (executed verbatim from PDE-486.yaml): the modal sum "
    "satisfies u_tt = c^2 u_xx",
    sp.simplify(sp.diff(snippet, t, 2) - c**2 * sp.diff(snippet, x, 2)) == 0,
)
check(
    "node code_implementation (executed verbatim from PDE-486.yaml): u(0,t) = u(L,t) = 0 "
    "holds exactly by construction for all t",
    sp.simplify(snippet.subs(x, 0)) == 0 and sp.simplify(snippet.subs(x, L)) == 0,
)

# --- boundary: linear + homogeneous does NOT imply separable ----------------
# Counterexample: u_xx + u_yy + x*y*u = 0 is linear and homogeneous.  Under
# u = X(x)Y(y), dividing by XY gives
#     X''/X + Y''/Y + x*y = 0,  i.e.  X''/X + Y''/Y = -x*y.
# The left side has the form f(x) + g(y), whose mixed partial d^2/dxdy is 0,
# while the right side has mixed partial -1.  The contradiction is what rules
# out separation; the constant 1 below is that mixed partial.
#
# NOTE on a rejected earlier attempt: x*y*u_xx + u_yy = 0 is NOT a valid
# counterexample.  Dividing instead by X*Y*y gives x*X''/X + Y''/(y*Y) = 0,
# which separates.  Checking only the quotient by X*Y is insufficient, because
# separation is allowed to multiply through by a nonzero factor first.
y_var = sp.Symbol("y", real=True)
Xf, Yf = sp.Function("X"), sp.Function("Y")
product = Xf(x) * Yf(y_var)
non_separable = (
    sp.diff(product, x, 2) + sp.diff(product, y_var, 2) + x * y_var * product
)
quotient = sp.simplify(non_separable / product)
mixed_partial = sp.simplify(sp.diff(quotient, x, y_var))
check(
    "counterexample u_xx + u_yy + x*y*u = 0: dividing by X*Y leaves a coupling term "
    "whose mixed partial equals 1, contradicting any f(x)+g(y) split. Checked claim: "
    "'no NONTRIVIAL Cartesian product solution X(x)Y(y) exists IN THESE COORDINATES'; "
    "this says nothing about other coordinate systems or the trivial solution u = 0",
    sp.simplify(mixed_partial - 1) == 0,
)
# SAMPLED RESCALING CHECKS - not part of the proof.
# The mixed-partial contradiction above is the whole proof.  These extra checks
# only sample a habit that invalidated an earlier attempt: dividing the equation
# by X*Y*<factor> instead of X*Y can sometimes separate an equation that the
# plain quotient appears to couple.  The sample is NOT exhaustive; passing it
# does not prove that no rescaling separates the equation.
for factor, label in ((y_var, "y"), (x, "x"), (x * y_var, "x*y")):
    rescaled = sp.simplify(sp.diff(sp.simplify(non_separable / (product * factor)), x, y_var))
    check(
        f"sampled rescaling: dividing by X*Y*{label} (not multiplying by it) still leaves "
        f"a nonzero mixed partial; sampled evidence only, not exhaustive",
        sp.simplify(rescaled) != 0,
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
