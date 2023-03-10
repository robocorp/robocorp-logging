def before_method(event, args):  # @DontTrace
    print(event, args)


def after_method(event):  # @DontTrace
    print(event)
