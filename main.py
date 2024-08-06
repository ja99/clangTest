import json
from pprint import pprint

import clang.cindex
from dataclasses import dataclass
from typing import List, Optional
import tomllib
import tomli_w
import tomlkit


@dataclass
class CField:
    name: str
    type: str
    n_bits: Optional[int]
    comments: list[str]
    line_range: (int, int)
    column_range: (int, int)

    def __dict__(self):
        return {
            "name": self.name,
            "type": self.type,
            "n_bits": self.n_bits if self.n_bits else -1,
            "comments": self.comments,
            "line_range": self.line_range,
            "column_range": self.column_range
        }


@dataclass
class CStruct:
    name: str
    fields: List[CField]
    comments: list[str]
    line_range: (int, int)
    column_range: (int, int)

    def __dict__(self):
        return {
            "name": self.name,
            "fields": [field.__dict__() for field in self.fields],
            "comments": self.comments,
            "line_range": self.line_range,
            "column_range": self.column_range
        }


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

def associate_comments(structs: list[CStruct], comments: list[CComment]) -> list[CStruct]:
    for struct in structs:
        for comment in comments:
            # check if comment is immediately before the struct
            if comment.line_range[1] + 1 == struct.line_range[0]:
                struct.comments.append(comment.comment)

            # check if comment is within range of field
            for field in struct.fields:
                if comment.line_range[0] >= field.line_range[0] and comment.line_range[1] <= field.line_range[1]:
                    field.comments.append(comment.comment)

    return structs


def get_ranges(node: clang.cindex.Cursor) -> ((int, int), (int, int)):
    return ((node.extent.start.line, node.extent.end.line),
            (node.extent.start.column, node.extent.end.column))


def parse_field(field_node: clang.cindex.Cursor) -> CField:
    name = field_node.spelling
    type_name = field_node.type.spelling
    n_bits = None

    # Check for bit field
    if field_node.get_bitfield_width() > 0:
        n_bits = field_node.get_bitfield_width()

    line_range, column_range = get_ranges(field_node)

    return CField(name=name, type=type_name, n_bits=n_bits, comments=[], line_range=line_range,
                  column_range=column_range)


def parse_struct(struct_node: clang.cindex.Cursor) -> CStruct:
    struct_name = struct_node.spelling
    fields = []

    for child in struct_node.get_children():
        if child.kind == clang.cindex.CursorKind.FIELD_DECL:
            fields.append(parse_field(child))


    line_range, column_range = get_ranges(struct_node)

    return CStruct(name=struct_name, fields=fields, comments=[], line_range=line_range, column_range=column_range)


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

    structs = parse_header_file(header_file_path)
    structs = associate_comments(structs, comments)

    for struct in structs:
        s = json.dumps(struct.__dict__())
        # pprint(s)
        s = tomlkit.dumps(struct.__dict__())
        print(s)
