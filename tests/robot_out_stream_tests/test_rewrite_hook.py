def test_ast_utils():
    from robocorp_logging import _ast_utils
    import ast

    node = ast.parse(
        """
print({'a': c, 1: d})
""",
        filename="<string>",
    )
    _ast_utils.print_ast(node)


def test_rewrite_hook():
    from robocorp_logging._rewrite_hook import RewriteHook, Config
    import sys
    from robocorp_logging import rewrite_callbacks

    config = Config()
    hook = RewriteHook(config)
    sys.meta_path.insert(0, hook)

    from robot_out_stream_tests._resources import check

    print("\n============== Output from hooks ==============\n")

    def before_method(name, args_dict):
        print("before", name, args_dict)

    def after_method(name):
        print("after", name)

    def method_return(name, return_value):
        if return_value is not None:
            print("return", name, return_value)

    rewrite_callbacks.before_method.register(before_method)
    rewrite_callbacks.after_method.register(after_method)
    rewrite_callbacks.method_return.register(method_return)

    check.some_method()
    check.SomeClass(1, 2)
