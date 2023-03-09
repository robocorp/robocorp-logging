def call_another_method(param0, param1, param2):
    assert 1 == 1


def some_method():
    call_another_method(1, "arg", ["a", "b"])
    return 22
    a = 10
