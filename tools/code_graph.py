import ast
import os
from collections import defaultdict

class CodeGraph:
    def __init__(self):
        self.calls = defaultdict(set)      # A -> B
        self.called_by = defaultdict(set)  # B -> A

    def add_call(self, caller, callee):
        self.calls[caller].add(callee)
        self.called_by[callee].add(caller)


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self, graph, current_function):
        self.graph = graph
        self.current_function = current_function

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            callee = node.func.id
            self.graph.add_call(self.current_function, callee)
        self.generic_visit(node)


def parse_file(filepath, graph):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            visitor = FunctionCallVisitor(graph, func_name)
            visitor.visit(node)


def build_graph(root_dir):
    graph = CodeGraph()

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                parse_file(os.path.join(root, file), graph)

    return graph


# ---- TOOL FUNCTIONS ----

def find_callers(graph, function_name):
    return list(graph.called_by.get(function_name, []))


def find_callees(graph, function_name):
    return list(graph.calls.get(function_name, []))


# ---- CLI (for MCP or testing) ----

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--function", required=True)

    args = parser.parse_args()

    graph = build_graph(args.repo)

    if args.action == "find_callers":
        result = find_callers(graph, args.function)

    elif args.action == "find_callees":
        result = find_callees(graph, args.function)

    else:
        result = {"error": "unknown action"}

    print(json.dumps(result))
