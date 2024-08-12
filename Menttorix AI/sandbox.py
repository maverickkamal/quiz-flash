from langchain_core.tools import tool
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
from RestrictedPython.Eval import default_guarded_getiter, default_guarded_getitem
import math

class AdvancedCodeExecutor:
    def __init__(self):
        self.safe_globals = {
            '__builtins__': safe_builtins,
            '_getiter_': default_guarded_getiter,
            '_getitem_': default_guarded_getitem,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            'math': math,
        }

    def execute_code(self, code):
        try:
            byte_code = compile_restricted(
                code,
                '<inline>',
                'exec'
            )
            exec(byte_code, self.safe_globals)
            return self.safe_globals.get('result', None)
        except Exception as e:
            return f"Error: {str(e)}"

@tool
def execute_safe_code(code: str) -> str:
    """
    Safely executes Python code with restricted access to built-ins and the math module.
    
    Args:
        code (str): The Python code to execute.
    
    Returns:
        str: The result of the code execution or an error message if execution fails.
    """
    executor = AdvancedCodeExecutor()
    result = executor.execute_code(code)
    return str(result)

# Example usage
if __name__ == "__main__":
    # Test with Fibonacci sequence
    fibonacci_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)
result = [fibonacci(i) for i in range(10)]
    """
    print("Fibonacci sequence:", execute_safe_code(fibonacci_code))

    # Test with prime numbers
    prime_code = """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True
result = [n for n in range(100) if is_prime(n)]
    """
    print("Prime numbers up to 100:", execute_safe_code(prime_code))
