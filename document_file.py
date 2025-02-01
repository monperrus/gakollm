import ast
import astor

class DocstringReplacer(ast.NodeTransformer):
    """AST Node Transformer to replace module docstring."""

    def visit_Module(self, node):
        """Visit Module node and replace docstring."""

        # Replace docstring
        node.body[0] = ast.Assign(
            targets=,
            value=ast.Str(s='New module docstring')
        )

        # Continue with default visitation
        return self.generic_visit(node)


def parse_and_rewrite_python_program(filename):
    """Parse Python program, replace docstring, and rewrite the program."""

    # Parse Python source code into AST
    with open(filename, 'r') as source:
        tree = ast.parse(source.read())

    # Replace docstring
    DocstringReplacer().visit(tree)

    # Rewrite the Python program
    with open(filename, 'w') as source:
        source.write(astor.to_source(tree))


if __name__ == "__main__":
    parse_and_rewrite_python_program('test.py')
