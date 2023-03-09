import ast
from typing import Optional
import sys
from ._rewrite_hook import Config


def is_rewrite_disabled(docstring: str) -> bool:
    return "NO_LOG" in docstring


def before_method(s):
    print(s)


def after_method(s):
    print(s)


def rewrite_with_logging(
    mod: ast.Module,
    source: Optional[bytes] = None,
    module_path: Optional[str] = None,
    config: Optional[Config] = None,
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
                "robocorp_logging._rewrite_with_logging",
                "@robocorp_log_rh",
                lineno=lineno,
                col_offset=0,
            ),
        ]
    else:
        aliases = [
            ast.alias("builtins", "@py_builtins"),
            ast.alias("robocorp_logging._rewrite_with_logging", "@robocorp_log_rh"),
        ]

    imports = [ast.Import([alias], lineno=lineno, col_offset=0) for alias in aliases]
    mod.body[pos:pos] = imports

    it = _ast_utils.iter_nodes(mod)
    while True:
        try:
            _stack, node = next(it)
        except StopIteration:
            break

        if node.__class__.__name__ == "Return":
            factory = _ast_utils.NodeFactory(node.lineno, node.col_offset)

            call = factory.Call()
            call.func = factory.NameLoadRewriteMod("after_method")
            call.args.append(factory.Str(f"Leaving with return"))

            it.send([factory.Expr(call), node])

        elif node.__class__.__name__ == "FunctionDef":
            function = node
            if function.body:
                function_body = function.body
                function.body = None  # Proper value will be set later.

                factory = _ast_utils.NodeFactory(
                    function_body[0].lineno, function_body[0].col_offset
                )

                # Only rewrite functions which actually have some content.
                call = factory.Call()
                call.func = factory.NameLoadRewriteMod("before_method")
                call.args.append(factory.Str(f"Entering: {function.name}"))

                try_finally = factory.Try()
                try_finally.body = function_body
                try_finally.body.insert(0, factory.Expr(call))

                factory = _ast_utils.NodeFactory(
                    function_body[-1].lineno, function_body[-1].col_offset
                )
                call = factory.Call()
                call.func = factory.NameLoadRewriteMod("after_method")
                call.args.append(factory.Str(f"Leaving: {function.name}"))

                try_finally.finalbody = [factory.Expr(call)]

                function.body = [try_finally]

    print(ast.unparse(mod))
