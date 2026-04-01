import sympy
from sympy_latex_parser import parse_latex


def compute_derivative(latex: str, var_name: str = "x") -> str:
    """
    Computes the derivative of a LaTeX expression with respect to a variable.

    Args:
        latex (str): The expression in LaTeX format.
        var_name (str): The name of the variable to differentiate with respect to. Defaults to "x".

    Returns:
        str: The LaTeX string of the resulting derivative.
    """
    try:
        # Parse the LaTeX expression to a SymPy object
        expression = parse_latex(latex)

        # Create the symbol for the variable
        var_symbol = sympy.Symbol(var_name)

        # Differentiate
        derivative = sympy.diff(expression, var_symbol)

        # Convert back to LaTeX
        return sympy.latex(derivative)
    except Exception as e:
        return f"Error computing derivative: {str(e)}"


# DEMO
if __name__ == "__main__":
    print("-" * 23)
    print("DERIVATIVES CALC CONSOLE")
    print("-" * 23)
    while True:
        try:
            latex = input("\nEnter expression in LaTeX (exit to quit): ")
            if latex.strip().lower() == "exit":
                break
                
            var = input("Enter variable to differentiate (default: x): ")
            if var.strip().lower() == "exit":
                break
            if not var.strip():
                var = "x"
                
            result = compute_derivative(latex, var)
            print(f"Result: {result}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
