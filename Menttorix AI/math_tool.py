import sympy as sp
from sympy import symbols, Function, dsolve, Eq, sin, cos, tan, exp, log, sqrt
from sympy.physics.units import length, time, speed, acceleration
from sympy.physics.mechanics import dynamicsymbols
from langchain_core.tools import tool
from typing import List, Dict, Tuple, Any

class ComprehensiveMathEngine:
    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')
        self.constants = {
            'pi': sp.pi,
            'e': sp.E,
            'g': 9.81,  # acceleration due to gravity (m/s^2)
            'c': 299792458,  # speed of light (m/s)
        }

    def parse(self, expr):
        return sp.sympify(expr, locals=self.constants)

math_engine = ComprehensiveMathEngine()

# Algebra Tools
@tool
def solve_equation(eq: str) -> List[str]:
    """
    Solve a single equation, including polynomial, trigonometric, and exponential equations.

    Args:
        eq (str): The equation to solve, e.g., "x**2 - 4*x + 4 = 0" or "sin(x) = 1/2"

    Returns:
        List[str]: A list of solutions as strings

    Example:
        >> solve_equation("x**2 - 4*x + 4 = 0")
        ['2', '2']
    """
    return [str(sol) for sol in sp.solve(math_engine.parse(eq))]

@tool
def solve_system(eqs: List[str]) -> List[str]:
    """
    Solve a system of equations, including linear and non-linear systems.

    Args:
        eqs (List[str]): A list of equations to solve, e.g., ["x + y - 10", "2*x - y - 5"]

    Returns:
        List[str]: A list of solution sets as strings

    Example:
        >> solve_system(["x + y - 10", "2*x - y - 5"])
        ['{x: 5, y: 5}']
    """
    parsed_eqs = [math_engine.parse(eq) for eq in eqs]
    return [str(sol) for sol in sp.solve(parsed_eqs)]


@tool
def factor(expr: str) -> str:
    """
    Factor an algebraic expression, including complex factorizations.

    Args:
        expr (str): The expression to factor, e.g., "x**2 - 9"

    Returns:
        str: The factored expression as a string

    Example:
        >> factor("x**2 - 9")
        '(x - 3)*(x + 3)'
    """
    return str(sp.factor(math_engine.parse(expr)))

@tool
def expand(expr: str) -> str:
    """Expand an algebraic expression."""
    return str(sp.expand(math_engine.parse(expr)))

# Calculus Tools
@tool
def differentiate(expr: str, var: str) -> str:
    """
    Differentiate an expression with respect to a variable, with support for higher-order derivatives.

    Args:
        expr (str): The expression to differentiate, e.g., "x**3 + 2*x"
        var (str): The variable to differentiate with respect to, e.g., "x"
        order (int, optional): The order of differentiation. Defaults to 1.

    Returns:
        str: The differentiated expression as a string

    Example:
        >> differentiate("x**3 + 2*x", "x", 2)
        '6*x'
    """
    return str(sp.diff(math_engine.parse(expr), math_engine.parse(var), order))


@tool
def limit(expr: str, var: str, point: float) -> str:
    """Calculate the limit of an expression."""
    return str(sp.limit(math_engine.parse(expr), math_engine.parse(var), point))

@tool
def series(expr: str, var: str, point: float, n: int) -> str:
    """Calculate the series expansion of an expression."""
    return str(sp.series(math_engine.parse(expr), math_engine.parse(var), point, n).removeO())

# Linear Algebra Tools
@tool
def matrix_multiply(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """Multiply two matrices."""
    matrix_A = sp.Matrix(A)
    matrix_B = sp.Matrix(B)
    result = matrix_A * matrix_B
    return [list(map(float, row)) for row in result.tolist()]

@tool
def determinant(A: List[List[float]]) -> float:
    """Calculate the determinant of a matrix."""
    matrix_A = sp.Matrix(A)
    return float(matrix_A.det())

@tool
def eigenvalues(A: List[List[float]]) -> Dict[float, int]:
    """Calculate the eigenvalues of a matrix."""
    matrix_A = sp.Matrix(A)
    return {float(k): v for k, v in matrix_A.eigenvals().items()}

# Physics Tools
@tool
def kinematics(v0: float, a: float, t: float) -> str:
    """Solve a kinematics equation."""
    s = sp.Function('s')
    eq = sp.Eq(s(math_engine.t).diff(math_engine.t, 2), a)
    solution = sp.dsolve(eq, s(math_engine.t), ics={s(0): 0, s(math_engine.t).diff(math_engine.t).subs(math_engine.t, 0): v0})
    return str(solution)

@tool
def projectile_motion(v0: float, angle: float, g: float = 9.81) -> Tuple[str, str]:
    """Calculate projectile motion."""
    theta = sp.rad(angle)
    x = v0 * sp.cos(theta) * math_engine.t
    y = v0 * sp.sin(theta) * math_engine.t - 0.5 * g * math_engine.t**2
    return (str(x), str(y))

@tool
def simple_harmonic_motion(A: float, omega: float, phi: float) -> str:
    """Calculate simple harmonic motion."""
    return str(A * sp.cos(omega * math_engine.t + phi))

# Engineering Tools
@tool
def beam_deflection(L: float, E: float, I: float, w: float) -> str:
    """Calculate beam deflection."""
    x = sp.Symbol('x')
    return str(w * x**2 * (L - x)**2 / (24 * E * I))

@tool
def fluid_flow(rho: float, v: float, D: float, mu: float) -> float:
    """Calculate Reynolds number for fluid flow."""
    Re = rho * v * D / mu
    return float(Re)

