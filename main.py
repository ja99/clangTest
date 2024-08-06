from pprint import pprint

import clang.cindex
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CField:
    name: str
    type: str
    n_bits: Optional[int]
    comment: str
    line_range: (int, int)
    column_range: (int, int)


@dataclass
class CStruct:
    name: str
    fields: List[CField]
    comment: str
    line_range: (int, int)
    column_range: (int, int)


@dataclass
class CComment:
    comment: str
    line_range: (int, int)
    column_range: (int, int)


def get_comments(file_path:str) -> list[CComment]:
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_path)
    tokens = translation_unit.cursor.get_tokens()
    comments = []
    for token in tokens:
        if token.kind == clang.cindex.TokenKind.COMMENT:
            line_range, column_range = get_ranges(token)
            comment = CComment(
                comment=token.spelling,
                line_range=line_range,
                column_range=column_range
            )
            comments.append(comment)
    return comments


def get_ranges(node: clang.cindex.Cursor) -> ((int, int), (int, int)):
    return ((node.extent.start.line, node.extent.end.line), (node.extent.start.column, node.extent.end.column))


def parse_field(field_node: clang.cindex.Cursor) -> CField:
    name = field_node.spelling
    type_name = field_node.type.spelling
    n_bits = None

    # Check for bit field
    if field_node.get_bitfield_width() > 0:
        n_bits = field_node.get_bitfield_width()

    comment = get_comment(field_node)

    line_range, column_range = get_ranges(field_node)

    return CField(name=name, type=type_name, n_bits=n_bits, comment=comment, line_range=line_range,
                  column_range=column_range)


def parse_struct(struct_node: clang.cindex.Cursor) -> CStruct:
    struct_name = struct_node.spelling
    fields = []

    for child in struct_node.get_children():
        if child.kind == clang.cindex.CursorKind.FIELD_DECL:
            fields.append(parse_field(child))

    comment = get_comment(struct_node)

    line_range, column_range = get_ranges(struct_node)

    return CStruct(name=struct_name, fields=fields, comment=comment, line_range=line_range, column_range=column_range)


def parse_header_file(filename: str) -> list[CStruct]:
    index = clang.cindex.Index.create()
    translation_unit = index.parse(filename)

    structs: list[CStruct] = []

    for node in translation_unit.cursor.get_children():
        if node.kind == clang.cindex.CursorKind.STRUCT_DECL:
            structs.append(parse_struct(node))

    return structs


if __name__ == "__main__":
    # Replace with your actual header file path
    header_file_path = "test_cases/example2.h"
    comments = get_comments(header_file_path)
    pprint(comments)
    exit()


    structs = parse_header_file(header_file_path)

    for struct in structs:
        print(f"Struct: {struct.name}")
        print(f"Comment: {struct.comment}")
        print(f"Line Range: {struct.line_range}")
        print(f"Column Range: {struct.column_range}")
        for field in struct.fields:
            print(f"  Field Name: {field.name}")
            print(f"    Type: {field.type}")
            print(f"    Bits: {field.n_bits}")
            print(f"    Comment: {field.comment}")
            print(f"    Line Range: {field.line_range}")
            print(f"    Column Range: {field.column_range}")
