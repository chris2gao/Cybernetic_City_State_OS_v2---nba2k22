import yaml
import sys
import traceback

def create_restricted_globals():
    # Only allow safe mathematical and tensor libraries
    import math
    import sympy as sp
    try:
        import torch
    except ImportError:
        torch = None
        
    return {
        '__builtins__': {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'complex': complex, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
            'filter': filter, 'float': float, 'format': format, 'frozenset': frozenset,
            'getattr': getattr, 'hasattr': hasattr, 'hash': hash, 'hex': hex,
            'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
            'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
            'min': min, 'next': next, 'object': object, 'oct': oct, 'pow': pow,
            'print': print, 'property': property, 'range': range, 'repr': repr,
            'reversed': reversed, 'round': round, 'set': set, 'slice': slice,
            'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple, 'type': type,
            'zip': zip, 'AssertionError': AssertionError, 'Exception': Exception,
            'ValueError': ValueError, 'TypeError': TypeError, 'KeyError': KeyError,
            'IndexError': IndexError, 'StopIteration': StopIteration,
            '__import__': __import__
        },
        'math': math,
        'sympy': sp,
        'sp': sp,
        'torch': torch
    }

def run_sanity_audit(yaml_content):
    try:
        data = yaml.safe_load(yaml_content)
        # Handle both root-level fields and nested concept_node structures
        concept = data.get('concept_node', data) if isinstance(data, dict) else {}
        audit = concept.get('v8_sanity_audit', {})
        code = audit.get('sympy_pseudo_code', '')
        
        if not code:
            return False, "No sympy_pseudo_code found in YAML."
            
        print(f"--- Running Sandbox Audit for [{concept.get('id', 'UNKNOWN')}] ---")
        
        restricted_globals = create_restricted_globals()
        
        # Compile first to catch syntax errors
        try:
            compiled_code = compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
            
        # Execute in restricted globals
        try:
            exec(compiled_code, restricted_globals)
            return True, "Passed"
        except AssertionError as e:
            return False, f"Assertion Failed: {e}"
        except Exception as e:
            return False, f"Runtime Error: {type(e).__name__}: {e}"
            
    except Exception as e:
        return False, f"YAML Parsing Error: {e}"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sandbox_evaluator.py <path_to_yaml>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
        
    success, msg = run_sanity_audit(content)
    if success:
        print(f"[PASS] {msg}")
        sys.exit(0)
    else:
        print(f"[FAIL] {msg}")
        sys.exit(1)
