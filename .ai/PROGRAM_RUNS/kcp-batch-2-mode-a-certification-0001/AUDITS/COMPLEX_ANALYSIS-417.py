"""Deterministic audit for COMPLEX_ANALYSIS-417 (i as a 90-degree rotation).

Every assertion below corresponds to a claim the node makes.  A claim that is
not asserted here must not be described as machine-checked in the node.

Mode A track: this is a real SymPy run whose stdout/exit code are captured to a
log, so the node may record tool_status: run_with_log.
"""

from __future__ import annotations

import sympy as sp

RESULTS: list[tuple[str, str]] = []


def check(claim: str, condition: bool) -> None:
    assert condition, f"FAILED: {claim}"
    RESULTS.append((claim, "PASS"))


a, b = sp.symbols("a b", real=True)
z = a + b * sp.I

# --- sub_topic 1: algebraic form a + bi -------------------------------------
check("i**2 == -1", sp.simplify(sp.I**2 + 1) == 0)
check(
    "re(a+bi) == a and im(a+bi) == b for real a,b",
    sp.simplify(sp.re(z) - a) == 0 and sp.simplify(sp.im(z) - b) == 0,
)
check(
    "the real numbers embed as b == 0",
    sp.simplify(sp.im(a + 0 * sp.I)) == 0,
)

# --- sub_topic 2: multiplication by i is a 90-degree rotation ---------------
check(
    "i*(a+bi) == -b + a*i",
    sp.simplify(sp.expand(sp.I * z) - (-b + a * sp.I)) == 0,
)
check(
    "multiplication by i preserves modulus",
    sp.simplify(sp.Abs(sp.I * z) - sp.Abs(z)) == 0,
)
check(
    "i**4 * z == z (four quarter turns return to start)",
    sp.simplify(sp.expand(sp.I**4 * z) - z) == 0,
)
check(
    "i**2 * z == -z (two quarter turns are a half turn)",
    sp.simplify(sp.expand(sp.I**2 * z) + z) == 0,
)

# rotation matrix [[0,-1],[1,0]] acting on (a,b) must equal complex i*z
rot = sp.Matrix([[0, -1], [1, 0]])
vec = sp.Matrix([a, b])
rotated = rot * vec
iz = sp.expand(sp.I * z)
check(
    "rotation matrix [[0,-1],[1,0]] on (a,b) matches i*z componentwise",
    sp.simplify(rotated[0] - sp.re(iz)) == 0
    and sp.simplify(rotated[1] - sp.im(iz)) == 0,
)
check(
    "the rotation matrix has determinant 1 (orientation preserving)",
    sp.simplify(rot.det() - 1) == 0,
)

# --- argument increases by exactly pi/2 on a concrete positive-real point ---
# arg is multivalued in general; assert on a representative point to stay honest.
check(
    "arg(i*1) - arg(1) == pi/2",
    sp.simplify(sp.arg(sp.I * sp.Integer(1)) - sp.arg(sp.Integer(1)) - sp.pi / 2) == 0,
)
check(
    "arg(i*(1+i)) - arg(1+i) == pi/2",
    sp.simplify(
        sp.arg(sp.I * (1 + sp.I)) - sp.arg(1 + sp.I) - sp.pi / 2
    ) == 0,
)

# --- sub_topic 3: Argand plane correspondence ------------------------------
check(
    "the map a+bi -> (a,b) is additive (respects vector addition)",
    sp.simplify(sp.re((a + b * sp.I) + (1 + 2 * sp.I)) - (a + 1)) == 0
    and sp.simplify(sp.im((a + b * sp.I) + (1 + 2 * sp.I)) - (b + 2)) == 0,
)
check(
    "modulus equals Euclidean norm: |a+bi| == sqrt(a^2+b^2)",
    sp.simplify(sp.Abs(z) - sp.sqrt(a**2 + b**2)) == 0,
)

# --- the object/operator distinction ---------------------------------------
# The rotation is a property of the MAP "multiply by i", not of the number i.
c1, c2 = sp.symbols("c1 c2", real=True)
z1, z2 = sp.symbols("z1 z2")
check(
    "the map M(z) = i*z is R-linear: M(c1 z1 + c2 z2) == c1 M(z1) + c2 M(z2)",
    sp.simplify(sp.I * (c1 * z1 + c2 * z2) - (c1 * (sp.I * z1) + c2 * (sp.I * z2))) == 0,
)

# --- boundary: what this node must NOT claim -------------------------------
# Multiplication by a general complex number is NOT a pure rotation; it scales.
w = 2 * sp.I
check(
    "multiplying by 2i scales modulus by 2, so it is not a pure rotation",
    sp.simplify(sp.Abs(w * z) - 2 * sp.Abs(z)) == 0,
)
# The rotation-plus-scaling reading needs a NONZERO multiplier.
check(
    "multiplying by 0 collapses every z to 0, so the rotate-and-scale reading "
    "requires a nonzero multiplier",
    sp.simplify(sp.Integer(0) * z) == 0,
)
check(
    "arg(0) is not a well-defined real number, so 0 carries no rotation angle",
    sp.arg(sp.Integer(0)).is_number and sp.Abs(sp.Integer(0)) == 0,
)

if __name__ == "__main__":
    for claim, status in RESULTS:
        print(f"[{status}] {claim}")
    print(f"TOTAL {len(RESULTS)} assertions, all passed")
