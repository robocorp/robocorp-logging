import sys
from typing import (
    Iterator,
    Optional,
    List,
    Tuple,
    Generic,
    TypeVar,
)

import ast as ast_module
import typing
import ast


class _NodesProviderVisitor(ast_module.NodeVisitor):
    def __init__(self, on_node=lambda node: None):
        ast_module.NodeVisitor.__init__(self)
        self._stack = []
        self.on_node = on_node

    def generic_visit(self, node):
        self._stack.append(node)
        self.on_node(self._stack, node)
        ast_module.NodeVisitor.generic_visit(self, node)
        self._stack.pop()


class _PrinterVisitor(ast_module.NodeVisitor):
    def __init__(self, stream):
        ast_module.NodeVisitor.__init__(self)
        self._level = 0
        self._stream = stream

    def _replace_spacing(self, txt):
        curr_len = len(txt)
        delta = 80 - curr_len
        return txt.replace("*SPACING*", " " * delta)

    def generic_visit(self, node):
        # Note: prints line and col offsets 0-based (even if the ast is 1-based for
        # lines and 0-based for columns).
        self._level += 1
        try:
            indent = "  " * self._level
            node_lineno = getattr(node, "lineno", -1)
            if node_lineno != -1:
                # Make 0-based
                node_lineno -= 1
            node_end_lineno = getattr(node, "end_lineno", -1)
            if node_end_lineno != -1:
                # Make 0-based
                node_end_lineno -= 1
            self._stream.write(
                self._replace_spacing(
                    "%s%s *SPACING* (%s, %s) -> (%s, %s)\n"
                    % (
                        indent,
                        node.__class__.__name__,
                        node_lineno,
                        getattr(node, "col_offset", -1),
                        node_end_lineno,
                        getattr(node, "end_col_offset", -1),
                    )
                )
            )
            tokens = getattr(node, "tokens", [])
            for token in tokens:

                token_lineno = token.lineno
                if token_lineno != -1:
                    # Make 0-based
                    token_lineno -= 1

                self._stream.write(
                    self._replace_spacing(
                        "%s- %s, '%s' *SPACING* (%s, %s->%s)\n"
                        % (
                            indent,
                            token.type,
                            token.value.replace("\n", "\\n").replace("\r", "\\r"),
                            token_lineno,
                            token.col_offset,
                            token.end_col_offset,
                        )
                    )
                )

            ast_module.NodeVisitor.generic_visit(self, node)
        finally:
            self._level -= 1


INode = ast_module.AST
T = TypeVar("T")
Y = TypeVar("Y", covariant=True)


class NodeInfo(Generic[Y]):
    stack: Tuple[INode, ...]
    node: Y

    __slots__ = ["stack", "node"]

    def __init__(self, stack, node):
        self.stack = stack
        self.node = node

    def __str__(self):
        return f"NodeInfo({self.node.__class__.__name__})"

    __repr__ = __str__


def print_ast(node, stream=None):
    if stream is None:
        stream = sys.stderr
    errors_visitor = _PrinterVisitor(stream)
    errors_visitor.visit(node)


if typing.TYPE_CHECKING:
    from typing import runtime_checkable, Protocol

    @runtime_checkable
    class _AST_CLASS(INode, Protocol):
        pass

else:
    # We know that the AST we're dealing with is the INode.
    # We can't use runtime_checkable on Python 3.7 though.
    _AST_CLASS = ast_module.AST


def iter_and_replace_nodes(
    node, internal_stack: Optional[List[INode]] = None, recursive=True
) -> Iterator[Tuple[List[INode], INode]]:
    """
    :note: the yielded stack is actually always the same (mutable) list, so,
    clients that want to return it somewhere else should create a copy.
    """
    stack: List[INode]
    if internal_stack is None:
        stack = []
        if node.__class__.__name__ != "File":
            stack.append(node)
    else:
        stack = internal_stack

    if recursive:
        for field, value in ast_module.iter_fields(node):
            if isinstance(value, list):
                new_value = []
                changed = False
                for item in value:
                    if isinstance(item, _AST_CLASS):
                        new = yield stack, item

                        if new is not None:
                            changed = True
                            new_value.extend(new)
                        else:
                            new_value.append(item)

                        stack.append(item)
                        yield from iter_and_replace_nodes(item, stack, recursive=True)
                        stack.pop()

                if changed:
                    setattr(node, field, new_value)

            elif isinstance(value, _AST_CLASS):
                yield stack, value
                stack.append(value)

                yield from iter_and_replace_nodes(value, stack, recursive=True)

                stack.pop()
    else:
        # Not recursive
        for _field, value in ast_module.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, _AST_CLASS):
                        yield stack, item

            elif isinstance(value, _AST_CLASS):
                yield stack, value


def copy_line_and_col(from_node, to_node):
    to_node.lineno = from_node.lineno
    to_node.col_offset = from_node.col_offset


class NodeFactory:
    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset

    def _set_line_col(self, node):
        node.lineno = self.lineno
        node.col_offset = self.col_offset
        return node

    def Call(self):
        call = ast.Call(keywords=[], args=[])
        return self._set_line_col(call)

    def NameLoad(self, name: str):
        return self._set_line_col(ast.Name(name, ast.Load()))

    def Attribute(self, name: ast.AST, attr_name: str) -> ast.Attribute:
        return self._set_line_col(ast.Attribute(name, attr_name, ast.Load()))

    def NameLoadBuiltin(self, builtin_name: str):
        builtin_ref = self.NameLoad("@py_builtins")

        return self._set_line_col(self.Attribute(builtin_ref, builtin_name))

    def NameLoadRewriteCallback(self, builtin_name: str):
        builtin_ref = self.NameLoad("@robocorp_rewrite_callbacks")

        return self._set_line_col(self.Attribute(builtin_ref, builtin_name))

    def Str(self, s):
        return self._set_line_col(ast.Str(s))

    def Expr(self, expr):
        return self._set_line_col(ast.Expr(expr))

    def Try(self):
        try_node = ast.Try(handlers=[], orelse=[])
        return self._set_line_col(try_node)

    def Dict(self):
        return self._set_line_col(ast.Dict())
