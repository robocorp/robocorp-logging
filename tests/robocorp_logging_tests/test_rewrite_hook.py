from robocorp_logging._rewrite_hook import BaseConfig, ConfigFilesFiltering
import pytest
from io import StringIO


def test_ast_utils():
    from robocorp_logging import _ast_utils
    import ast

    node = ast.parse(
        """
print({'a': c, 1: d})
""",
        filename="<string>",
    )
    s = StringIO()
    _ast_utils.print_ast(node, stream=s)
    assert "Name" in s.getvalue()


class ConfigForTest(BaseConfig):
    def can_rewrite_module_name(self, module_name: str) -> bool:
        if module_name.startswith("robocorp_logging."):
            # We don't want to rewrite internal modules.
            return True

        return False

    def can_rewrite_module(self, module_name: str, filename: str) -> bool:
        return "check" in module_name


@pytest.mark.parametrize("config", [ConfigForTest(), ConfigFilesFiltering()])
def test_rewrite_hook_basic(config):
    from robocorp_logging._rewrite_hook import RewriteHook
    import sys
    from robocorp_logging import rewrite_callbacks
    from imp import reload

    hook = RewriteHook(config)
    sys.meta_path.insert(0, hook)

    from robocorp_logging_tests._resources import check

    check = reload(check)

    found = []

    def before_method(name, args_dict):
        found.append(("before", name, args_dict))

    def after_method(name):
        found.append(("after", name))

    def method_return(name, return_value):
        found.append(("return", name, return_value))

    rewrite_callbacks.before_method.register(before_method)
    rewrite_callbacks.after_method.register(after_method)
    rewrite_callbacks.method_return.register(method_return)

    check.some_method()
    check.SomeClass(1, 2)
    assert found == [
        ("before", "some_method", {}),
        (
            "before",
            "call_another_method",
            {"param0": 1, "param1": "arg", "args": (["a", "b"],), "kwargs": {"c": 3}},
        ),
        ("after", "call_another_method"),
        ("return", "some_method", 22),
        ("after", "some_method"),
        ("before", "SomeClass.__init__", {"arg1": 1, "arg2": 2}),
        ("after", "SomeClass.__init__"),
    ]
