"""
canonical_ast_hash.py — AST 拓扑同构化哈希
============================================
Drop-in replacement for hash(strip(code)) in live_evo_bank.py.

Zero LLM. Zero network. Pure stdlib (ast + hashlib + builtins).

Invariant under:
  ✓ α-renaming       (x→y, foo→bar)
  ✓ comment/docstring changes
  ✓ formatting        (空格/换行/缩进风格)
  ✓ type annotations  (全部擦除)
  ✓ commutative swap  (a+b ↔ b+a, a*b ↔ b*a, a&b ↔ b&a)
  ✓ decorator changes (全部擦除)

Preserved (semantically load-bearing):
  ✗ control flow topology  (if/for/while/try 骨架)
  ✗ operator types         (Add vs Sub vs Mult)
  ✗ literal values         (42, "hello")
  ✗ builtin names          (len, range, print)
  ✗ attribute names        (.append, .sort — 语义锚点)
"""

import ast
import hashlib
import builtins as _b

_BUILTINS = frozenset(dir(_b))
_COMMUTATIVE = (ast.Add, ast.Mult, ast.BitAnd, ast.BitOr, ast.BitXor)


class _Canon(ast.NodeTransformer):
    """DFS α-renaming + commutative normalization + docstring/annotation erasure."""

    def __init__(self):
        self._sc: list[dict[str, str]] = [{}]   # scope stack
        self._n: int = 0                          # monotonic counter

    # ── scope management ─────────────────────────────────────
    def _push(self):
        self._sc.append({})

    def _pop(self):
        self._sc.pop()

    def _α(self, name: str) -> str:
        """Map identifier → canonical tag by DFS encounter order."""
        if name in _BUILTINS:
            return name                           # preserve builtins
        for scope in reversed(self._sc):
            if name in scope:
                return scope[name]                # already bound
        tag = f"ξ{self._n}"                       # fresh canonical symbol
        self._n += 1
        self._sc[-1][name] = tag
        return tag

    # ── docstring stripper ───────────────────────────────────
    @staticmethod
    def _ds(body: list) -> list:
        if (body
                and isinstance(body[0], ast.Expr)
                and isinstance(getattr(body[0], "value", None), ast.Constant)
                and isinstance(body[0].value.value, str)):
            return body[1:]
        return body

    # ── scope-bearing nodes ──────────────────────────────────
    def visit_Module(self, node):
        node.body = self._ds(node.body)
        self.generic_visit(node)
        return node

    def _vf(self, node):
        """FunctionDef / AsyncFunctionDef."""
        node.name = self._α(node.name)
        node.decorator_list = []
        node.returns = None
        self._push()
        for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
            a.arg = self._α(a.arg)
            a.annotation = None
        for va in (node.args.vararg, node.args.kwarg):
            if va:
                va.arg = self._α(va.arg)
                va.annotation = None
        node.body = self._ds(node.body)
        self.generic_visit(node)
        self._pop()
        return node

    visit_FunctionDef = _vf
    visit_AsyncFunctionDef = _vf

    def visit_ClassDef(self, node):
        node.name = self._α(node.name)
        node.decorator_list = []
        self._push()
        node.body = self._ds(node.body)
        self.generic_visit(node)
        self._pop()
        return node

    def visit_Lambda(self, node):
        self._push()
        for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
            a.arg = self._α(a.arg)
            a.annotation = None
        self.generic_visit(node)
        self._pop()
        return node

    # ── leaf identifiers ─────────────────────────────────────
    def visit_Name(self, node):
        node.id = self._α(node.id)
        return node

    def visit_Global(self, node):
        node.names = [self._α(n) for n in node.names]
        return node

    visit_Nonlocal = visit_Global

    # ── commutative normalization ────────────────────────────
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, _COMMUTATIVE):
            if ast.dump(node.left) > ast.dump(node.right):
                node.left, node.right = node.right, node.left
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        node.values.sort(key=ast.dump)
        return node

    def visit_Set(self, node):
        self.generic_visit(node)
        node.elts.sort(key=ast.dump)
        return node

    # ── annotation erasure ───────────────────────────────────
    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        if node.value is not None:
            # Convert AnnAssign to standard Assign
            return ast.Assign(targets=[node.target], value=node.value)
        else:
            # Just an annotation without assignment, erase it
            return None


# ═════════════════════════════════════════════════════════════
#  PUBLIC API — drop-in replacement for your current hash
# ═════════════════════════════════════════════════════════════

def canonical_ast_hash(source: str) -> str:
    """
    Compute topology-invariant SHA-256 of Python source code.

    Two programs with identical algorithm skeletons but different
    variable names / comments / formatting / commutative operand
    ordering will produce **the same hash**.

    Pure local. Zero network. Zero LLM.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return hashlib.sha256(source.strip().encode()).hexdigest()

    # erase all positional metadata (line/col numbers)
    for node in ast.walk(tree):
        for attr in ("lineno", "col_offset", "end_lineno",
                     "end_col_offset", "type_comment"):
            if hasattr(node, attr):
                setattr(node, attr, None)

    tree = _Canon().visit(tree)
    sig = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(sig.encode()).hexdigest()


# ═════════════════════════════════════════════════════════════
#  PROOF: five programs, one hash
# ═════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # --- Variant A: original ---
    code_a = '''
def calculate_sum(data_list):
    """Compute the total."""
    total = 0
    for item in data_list:
        total = total + item  # accumulate
    return total
'''

    # --- Variant B: renamed everything ---
    code_b = '''
def foo(xs):
    acc = 0
    for x in xs:
        acc = acc + x
    return acc
'''

    # --- Variant C: swapped commutative operand (item + total) ---
    code_c = '''
def bar(numbers):
    result = 0
    for n in numbers:
        result = n + result
    return result
'''

    # --- Variant D: different formatting + type hints ---
    code_d = '''
def qux(
    seq: list[int],
) -> int:
    s: int = 0
    for elem in seq:
        s = s + elem
    return s
'''

    # --- Variant E: wildly different names + docstring ---
    code_e = '''
def zzz_aggregator(input_vector):
    \"\"\"This function does something completely unrelated (not really).\"\"\"
    accumulator_variable = 0
    for each_element in input_vector:
        accumulator_variable = each_element + accumulator_variable
    return accumulator_variable
'''

    hashes = {
        "A (original)":     canonical_ast_hash(code_a),
        "B (renamed)":      canonical_ast_hash(code_b),
        "C (commutative)":  canonical_ast_hash(code_c),
        "D (annotations)":  canonical_ast_hash(code_d),
        "E (extreme rename)": canonical_ast_hash(code_e),
    }

    print("=" * 72)
    print("CANONICAL AST HASH — TOPOLOGY INVARIANCE PROOF")
    print("=" * 72)
    for label, h in hashes.items():
        print(f"  {label:24s} → {h[:16]}...")
    print("-" * 72)

    unique = set(hashes.values())
    if len(unique) == 1:
        print(f"  ✅ ALL FIVE VARIANTS COLLAPSE TO ONE HASH: {list(unique)[0][:24]}...")
        print("  → Memory bank dedup: OPERATIONAL")
    else:
        print(f"  ❌ DIVERGENCE DETECTED: {len(unique)} distinct hashes")
        for label, h in hashes.items():
            print(f"     {label}: {h[:24]}")
    print("=" * 72)
