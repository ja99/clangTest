from pprint import pprint

import clang.cindex

# Set the library path if clang cannot be found automatically
# clang.cindex.Config.set_library_file("/usr/lib/llvm-10/lib/libclang-10.so.1")

# Create an index object
index = clang.cindex.Index.create()

# Parse the C++ file
tu = index.parse("test_cases/example1.cpp")

class AST:
    def __init__(self):
        self.ast = {}

    def add(self, level, node):
        if self.ast.get(level) is None:
            self.ast[level] = []
        self.ast[level].append(node)

    def __str__(self):
        return self.ast

class Node(clang.cindex.Cursor):
    def __init__(self, cursor:clang.cindex.Cursor):
        self.cursor = cursor

    def __str__(self):
        return f"{self.cursor.kind}: {self.cursor.spelling} [{self.cursor.location}]"


ast = AST()

# Function to recursively visit AST nodes
def visit_node(node:clang.cindex.Cursor, level=0):
    print('  ' * level + f"{node.kind}: {node.spelling} [{node.location}]")

    ast.add(level, Node(node))

    for child in node.get_children():
        visit_node(child, level + 1)

# Start visiting the nodes from the root
print(f"{type(tu.cursor)}: {tu.cursor.spelling} [{tu.cursor.location}]")
visit_node(tu.cursor)

pprint(ast)
