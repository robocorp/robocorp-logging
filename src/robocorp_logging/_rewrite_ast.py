import ast
from typing import Optional
import sys
from ._rewrite_hook import BaseConfig

DEBUG = False


def is_rewrite_disabled(docstring: str) -> bool:
    return "NO_LOG" in docstring


def rewrite_ast_add_callbacks(
    mod: ast.Module,
    source: Optional[bytes] = None,
    module_path: Optional[str] = None,
    config: Optional[BaseConfig] = None,
) -> None:
    """Rewrite the module as needed so that the logging is done automatically."""
    from robocorp_logging import _ast_utils

    if not mod.body:
        # Nothing to do.
        return

    # We'll insert some special imports at the top of the module, but after any
    # docstrings and __future__ imports, so first figure out where that is.
    doc = getattr(mod, "docstring", None)
    expect_docstring = doc is None
    if doc is not None and is_rewrite_disabled(doc):
        return
    pos = 0
    lineno = 1
    for item in mod.body:
        if (
            expect_docstring
            and isinstance(item, ast.Expr)
            and isinstance(item.value, ast.Str)
        ):
            doc = item.value.s
            if is_rewrite_disabled(doc):
                return
            expect_docstring = False
        elif (
            isinstance(item, ast.ImportFrom)
            and item.level == 0
            and item.module == "__future__"
        ):
            pass
        else:
            break
        pos += 1
    # Special case: for a decorated function, set the lineno to that of the
    # first decorator, not the `def`. Issue #4984.
    if isinstance(item, ast.FunctionDef) and item.decorator_list:
        lineno = item.decorator_list[0].lineno
    else:
        lineno = item.lineno
    # Now actually insert the special imports.
    if sys.version_info >= (3, 10):
        aliases = [
            ast.alias("builtins", "@py_builtins", lineno=lineno, col_offset=0),
            ast.alias(
                "robocorp_logging.rewrite_callbacks",
                "@robocorp_rewrite_callbacks",
                lineno=lineno,
                col_offset=0,
            ),
        ]
    else:
        aliases = [
            ast.alias("builtins", "@py_builtins"),
            ast.alias(
                "robocorp_logging.rewrite_callbacks", "@robocorp_rewrite_callbacks"
            ),
        ]

    imports = [ast.Import([alias], lineno=lineno, col_offset=0) for alias in aliases]
    mod.body[pos:pos] = imports

    it = _ast_utils.iter_and_replace_nodes(mod)
    while True:
        try:
            stack, node = next(it)
        except StopIteration:
            break

        if node.__class__.__name__ == "Return":

            if not stack:
                continue
            stack_it = reversed(stack)
            for function in stack_it:
                if function.__class__.__name__ != "FunctionDef":
                    continue
                break

            class_name = ""
            try:
                parent = next(stack_it)
                if parent.__class__.__name__ == "ClassDef":
                    class_name = parent.name + "."
            except StopIteration:
                pass

            factory = _ast_utils.NodeFactory(node.lineno, node.col_offset)

            result = []

            call = factory.Call()
            call.func = factory.NameLoadRewriteCallback("method_return")
            call.args.append(factory.Str(f"{class_name}{function.name}"))

            if node.value:
                assign = factory.Assign()
                store_name = factory.NameTempStore()
                assign.targets = [store_name]
                assign.value = node.value

                node.value = factory.NameLoad(store_name.id)

                result.append(assign)
                call.args.append(factory.NameLoad(store_name.id))
            else:
                call.args.append(factory.NameLoad("None"))

            result.append(factory.Expr(call))
            result.append(node)

            it.send(result)

        elif node.__class__.__name__ == "FunctionDef":
            function = node
            if function.body:
                class_name = ""
                if stack:
                    parent = stack[-1]
                    if parent.__class__.__name__ == "ClassDef":
                        class_name = parent.name + "."

                function_body = function.body
                function.body = None  # Proper value will be set later.

                factory = _ast_utils.NodeFactory(
                    function_body[0].lineno, function_body[0].col_offset
                )

                # Only rewrite functions which actually have some content.
                call = factory.Call()
                call.func = factory.NameLoadRewriteCallback("before_method")
                call.args.append(factory.Str(f"{class_name}{function.name}"))

                dct = factory.Dict()
                keys = []
                values = []
                for arg in function.args.args:
                    if class_name and arg.arg == "self":
                        continue
                    keys.append(factory.Str(arg.arg))
                    values.append(factory.NameLoad(arg.arg))

                if function.args.vararg:
                    keys.append(factory.Str(function.args.vararg.arg))
                    values.append(factory.NameLoad(function.args.vararg.arg))

                if function.args.kwarg:
                    keys.append(factory.Str(function.args.kwarg.arg))
                    values.append(factory.NameLoad(function.args.kwarg.arg))
                dct.keys = keys
                dct.values = values
                call.args.append(dct)

                function_body.insert(0, factory.Expr(call))

                try_finally = factory.Try()
                try_finally.body = function_body

                factory = _ast_utils.NodeFactory(
                    function_body[-1].lineno, function_body[-1].col_offset
                )
                call = factory.Call()
                call.func = factory.NameLoadRewriteCallback("after_method")
                call.args.append(factory.Str(f"{class_name}{function.name}"))

                try_finally.finalbody = [factory.Expr(call)]

                function.body = [try_finally]

    if DEBUG:
        print("\n============ New AST (with hooks in place) ==============\n")
        print(ast.unparse(mod))
