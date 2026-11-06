import ast
import sys
from pathlib import Path


DANGEROUS_FUNCTIONS = {
    "loads",
    "load"
}

DANGEROUS_MODULES = {
    "pickle",
    "cPickle",
    "dill",
    "shelve"
}


class PickleScanner(ast.NodeVisitor):

    def __init__(self):
        self.findings = []

    def visit_Call(self, node):

        function_name = None
        module_name = None

        if isinstance(node.func, ast.Attribute):
            function_name = node.func.attr

            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id

        elif isinstance(node.func, ast.Name):
            function_name = node.func.id

        if (
            function_name in DANGEROUS_FUNCTIONS
            and module_name in DANGEROUS_MODULES
        ):
            self.findings.append({
                "line": node.lineno,
                "function": function_name,
                "module": module_name,
                "severity": "HIGH",
                "issue": "Potential unsafe deserialization"
            })

        self.generic_visit(node)


def scan_file(filename):

    path = Path(filename)

    if not path.is_file():
        print("[ERROR] File not found.")
        return

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        scanner = PickleScanner()
        scanner.visit(tree)

        print("\n===== PICKLE SECURITY REPORT =====")
        print("File:", filename)

        if scanner.findings:

            for finding in scanner.findings:
                print("\n[WARNING] Unsafe deserialization candidate")
                print("Line:", finding["line"])
                print("Module:", finding["module"])
                print("Function:", finding["function"])
                print("Severity:", finding["severity"])
                print("Issue:", finding["issue"])

        else:
            print("[SAFE] No matching calls detected.")

    except SyntaxError as error:
        print("[ERROR] Syntax error:", error)

    except Exception as error:
        print("[ERROR]", error)


if __name__ == "__main__":

    filename = input(
        "Enter Python file path to scan: "
    )

    scan_file(filename)import ast
import sys
from pathlib import Path


DANGEROUS_FUNCTIONS = {
    "loads",
    "load"
}

DANGEROUS_MODULES = {
    "pickle",
    "cPickle",
    "dill",
    "shelve"
}


class PickleScanner(ast.NodeVisitor):

    def __init__(self):
        self.findings = []

    def visit_Call(self, node):

        function_name = None
        module_name = None

        if isinstance(node.func, ast.Attribute):
            function_name = node.func.attr

            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id

        elif isinstance(node.func, ast.Name):
            function_name = node.func.id

        if (
            function_name in DANGEROUS_FUNCTIONS
            and module_name in DANGEROUS_MODULES
        ):
            self.findings.append({
                "line": node.lineno,
                "function": function_name,
                "module": module_name,
                "severity": "HIGH",
                "issue": "Potential unsafe deserialization"
            })

        self.generic_visit(node)


def scan_file(filename):

    path = Path(filename)

    if not path.is_file():
        print("[ERROR] File not found.")
        return

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        scanner = PickleScanner()
        scanner.visit(tree)

        print("\n===== PICKLE SECURITY REPORT =====")
        print("File:", filename)

        if scanner.findings:

            for finding in scanner.findings:
                print("\n[WARNING] Unsafe deserialization candidate")
                print("Line:", finding["line"])
                print("Module:", finding["module"])
                print("Function:", finding["function"])
                print("Severity:", finding["severity"])
                print("Issue:", finding["issue"])

        else:
            print("[SAFE] No matching calls detected.")

    except SyntaxError as error:
        print("[ERROR] Syntax error:", error)

    except Exception as error:
        print("[ERROR]", error)


if __name__ == "__main__":

    filename = input(
        "Enter Python file path to scan: "
    )

    scan_file(filename)