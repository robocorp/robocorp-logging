def test_ast_utils():
    from robocorp_logging import _ast_utils
    import ast

    node = ast.parse(
        """
print('some string')
""",
        filename="<string>",
    )
    _ast_utils.print_ast(node)


def test_rewrite_hook():
    from robocorp_logging._rewrite_hook import RewriteHook, Config
    import sys

    config = Config()
    hook = RewriteHook(config)
    sys.meta_path.insert(0, hook)

    from robot_out_stream_tests._resources import check

    check.some_method()
