from sympy.parsing.latex.lark import parse_latex_lark


def parse_latex(latex: str):
    return parse_latex_lark(latex)


# DEMO
if __name__ == "__main__":
    while True:
        latex = input("Enter latex to parse (exit to quit): ")
        if latex == "exit":
            break
        print(parse_latex(latex))
