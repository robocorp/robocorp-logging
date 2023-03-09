import datetime
import json
from typing import Optional, Any, Iterator, List
import sys
import functools
from io import StringIO
import weakref

__version__ = "0.0.1"
version_info = [int(x) for x in __version__.split(".")]


_convert = {
    "gb": lambda s: s * 1e9,
    "g": lambda s: s * 1e9,
    "mb": lambda s: s * 1e6,
    "m": lambda s: s * 1e6,
    "kb": lambda s: s * 1000,
    "k": lambda s: s * 1000,
    "b": lambda s: s,
    "": lambda s: s,
}


def _convert_to_bytes(s):
    initial = s
    num = []
    while s and (s[0].isdigit() or s[0] == "."):
        num.append(s[0])
        s = s[1:]
    num = float("".join(num))
    unit = s.strip()
    conv = _convert.get(unit.lower())
    if conv is None:
        raise ValueError(f"Cannot get in bytes: {initial}")

    return conv(num)


def _log_error(func):
    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        import traceback

        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            s = StringIO()
            traceback.print_exc(file=s)
            self._robot_output_impl.log_message(
                "ERROR",
                f"_RobocorpLogger internal error: {e}\n{s.getvalue()}",
                self._robot_output_impl.get_time_delta(),
                False,
            )

    return new_func


class _RobocorpLogger:
    def __init__(
        self,
        output_dir: Optional[str] = None,
        max_file_size: Optional[str] = None,
        max_files: int = 0,
        log_html: Optional[str] = None,
        **kwargs,
    ):
        from robocorp_logging._impl import _RobotOutputImpl, _Config

        # Note: expected to be used just when used in-memory (not part of the public API).
        config = _Config(kwargs.get("__uuid__"))

        config.output_dir = output_dir
        config.log_html = log_html

        config.max_file_size_in_bytes = _convert_to_bytes(max_file_size)
        config.max_files = max_files

        if config.max_file_size_in_bytes < 10000:
            raise ValueError(
                f"Cannot generate logs where the max file size in bytes is less that 10000 bytes."
                f" Found: {config.max_file_size_in_bytes}."
                f" Arg: {max_file_size}."
            )

        # Note: expected to be used just when used in-memory (not part of the public API).
        config.write = kwargs.get("__write__")
        config.initial_time = kwargs.get("__initial_time__")
        config.additional_info = kwargs.get("__additional_info__")

        self._robot_output_impl = _RobotOutputImpl(config)
        self._skip_log_methods = 0
        self._skip_log_arguments = 0

    def hide_from_output(self, string_to_hide: str) -> None:
        self._robot_output_impl.hide_from_output(string_to_hide)

    @property
    def robot_output_impl(self):
        return self._robot_output_impl

    @property
    def initial_time(self) -> datetime.datetime:
        return self._robot_output_impl.initial_time

    def _get_time_delta(self) -> float:
        return self._robot_output_impl.get_time_delta()

    def start_logging_methods(self):
        if self._skip_log_methods <= 0:
            self._robot_output_impl.log_message(
                "ERROR",
                f"_RobocorpLogger error: start_logging_methods() called before stop_logging_methods() (call is ignored as logging is already on).",
                self._robot_output_impl.get_time_delta(),
                False,
            )
            return

        self._skip_log_methods -= 1

    def stop_logging_methods(self):
        self._skip_log_methods += 1

    def start_logging_variables(self):
        if self._skip_log_arguments <= 0:
            self._robot_output_impl.log_message(
                "ERROR",
                f"_RobocorpLogger error: start_logging_variables() called before stop_logging_variables() (call is ignored as logging is already on).",
                self._robot_output_impl.get_time_delta(),
                False,
            )
            return

        self._skip_log_arguments -= 1

    def stop_logging_variables(self):
        self._skip_log_arguments += 1

    @_log_error
    def start_suite(self, name: str, suite_id: str, suite_source: str) -> None:
        return self._robot_output_impl.start_suite(
            name,
            suite_id,
            suite_source,
            self._get_time_delta(),
        )

    @_log_error
    def end_suite(self, name: str, suite_id: str, status: str):
        # {
        #     "id": "s1",
        #     "longname": "Robot1",
        #     "doc": "",
        #     "metadata": {},
        #     "starttime": "20221004 09:38:40.271",
        #     "endtime": "20221004 09:38:40.323",
        #     "elapsedtime": 52,
        #     "status": "FAIL",
        #     "message": "",
        #     "tests": ["First task", "Second task"],
        #     "suites": [],
        #     "totaltests": 2,
        #     "source": "C:\\Users\\fabio\\AppData\\Local\\Temp\\pytest-of-fabio\\pytest-184\\test_robot_out_stream0\\test_robot_out_stream\\robot1.robot",
        #     "statistics": "2 tasks, 1 passed, 1 failed",
        # }
        return self._robot_output_impl.end_suite(
            suite_id, status, self._get_time_delta()
        )

    @_log_error
    def start_task(self, name, attributes):
        # {
        #     "id": "s1-t1",
        #     "longname": "Robot1.First task",
        #     "doc": "",
        #     "tags": [],
        #     "lineno": 11,
        #     "source": "C:\\Users\\fabio\\...\\robot1.robot",
        #     "starttime": "20221003 14:20:02.231",
        #     "template": "",
        #     "originalname": "First task",
        # }
        return self._robot_output_impl.start_task(
            name,
            attributes["id"],
            attributes.get(
                "lineno"
            ),  # The source is already given by the suite (no need to repeat)
            self._get_time_delta(),
            attributes.get("tags"),
        )

    @_log_error
    def send_tag(self, tag: str):
        if self._skip_log_methods:
            return

        return self._robot_output_impl.send_tag(tag)

    @_log_error
    def send_info(self, info: str):
        return self._robot_output_impl.send_info(info)

    @_log_error
    def send_start_time_delta(self, time_delta_in_seconds: float):
        if self._skip_log_methods:
            return

        return self._robot_output_impl.send_start_time_delta(time_delta_in_seconds)

    @_log_error
    def end_task(self, name, attributes):
        # {
        #     "id": "s1-t2",
        #     "longname": "Robot1.Second task",
        #     "doc": "",
        #     "tags": [],
        #     "lineno": 15,
        #     "source": "C:\\Users\\fabio\\AppData\\Local\\Temp\\pytest-of-fabio\\pytest-187\\test_robot_out_stream0\\test_robot_out_stream\\robot1.robot",
        #     "starttime": "20221004 16:23:10.403",
        #     "endtime": "20221004 16:23:10.412",
        #     "elapsedtime": 9,
        #     "status": "FAIL",
        #     "message": "Failed execution for some reason...",
        #     "template": "",
        #     "originalname": "Second task",
        # }
        return self._robot_output_impl.end_task(
            attributes["id"],
            attributes["status"],
            attributes["message"],
            self._get_time_delta(),
        )

    class _Sentinel:
        pass

    @_log_error
    def start_keyword(self, name, attributes):
        # print("----start----\n", json.dumps(attributes, indent=4))

        hide_from_logs = False
        tags = attributes.get("tags")
        if tags:
            if "log:ignore-methods" in tags:
                self._skip_log_methods += 1
            if "log:ignore-variables" in tags:
                self._skip_log_arguments += 1

        name = attributes["kwname"]

        normalized_name = name.lower().replace(" ", "")
        if self._skip_log_methods:

            if normalized_name not in (
                "stoploggingmethods",
                "startloggingmethods",
            ):
                hide_from_logs = True

        # {
        #     "doc": "Does absolutely nothing.",
        #     "assign": [],
        #     "tags": [],
        #     "lineno": 7,
        #     "source": "C:\\Users\\fabio\\AppData\\Local\\Temp\\pytest-of-fabio\\pytest-170\\test_robot_out_stream0\\test_robot_out_stream\\robot1.robot",
        #     "type": "KEYWORD",
        #     "status": "NOT SET",
        #     "starttime": "20221003 16:20:21.234",
        #     "kwname": "No Operation",
        #     "libname": "BuiltIn",
        #     "args": [],
        # }
        source: Optional[str] = attributes.get("source", self._Sentinel)
        lineno: Optional[int] = attributes.get("lineno", self._Sentinel)
        if source is self._Sentinel or lineno is self._Sentinel:
            # I.e.: it was not passed at all (if it was passed and None,
            # keep it as None: xml conversion use-case).
            source = None
            lineno = -1

            # HACK for RF 3: try to get the location (since it's not available).
            f: Optional[Any]
            f = sys._getframe()
            while f is not None:
                if f.f_code.co_name == "run_step":
                    step = f.f_locals.get("step")
                    if step is not None:
                        try:
                            source = step.source
                            lineno = step.lineno
                        except AttributeError:
                            pass
                    break  # Break when run_step is found anyways.

                f = f.f_back

        args = attributes.get("args")
        if args:
            if self._skip_log_arguments or normalized_name == "hidefromoutput":
                args = ("<redacted>",)

        kw_type = attributes.get("type")
        kw_doc = attributes.get("doc")
        libname = attributes.get("libname", "")
        if libname is None:
            libname = ""

        kw_assign = attributes.get("assign")
        return self._robot_output_impl.start_keyword(
            name,
            libname,
            kw_type,
            kw_doc,
            source,
            lineno,
            self._get_time_delta(),
            args,
            kw_assign,
            hide_from_logs=hide_from_logs,
        )

    @_log_error
    def end_keyword(self, name, attributes):
        # print("----end----\n", json.dumps(attributes, indent=4))

        try:
            name = attributes["kwname"]
            # {
            #     "doc": "Does absolutely nothing.",
            #     "assign": [],
            #     "tags": [],
            #     "lineno": 7,
            #     "source": "C:\\Users\\fabio\\AppData\\Local\\Temp\\pytest-of-fabio\\pytest-191\\test_robot_out_stream0\\test_robot_out_stream\\robot1.robot",
            #     "type": "KEYWORD",
            #     "status": "PASS",
            #     "starttime": "20221004 16:27:46.959",
            #     "endtime": "20221004 16:27:46.959",
            #     "elapsedtime": 0,
            #     "kwname": "No Operation",
            #     "libname": "BuiltIn",
            #     "args": [],
            # }
            libname = attributes.get("libname", "")
            if libname is None:
                libname = ""

            return self._robot_output_impl.end_keyword(
                name, libname, attributes["status"], self._get_time_delta()
            )
        finally:
            tags = attributes.get("tags")
            if tags:
                if "log:ignore-methods" in tags:
                    self._skip_log_methods -= 1
                if "log:ignore-variables" in tags:
                    self._skip_log_arguments -= 1

    @_log_error
    def log_message(self, message, skip_error=True):
        # {
        #     "timestamp": "20221026 10:00:31.591",
        #     "message": "${dct} = {'a': '1', 'b': '1'}",
        #     "level": "INFO",
        #     "html": "no",
        # }
        level = message["level"]
        if level not in ("ERROR", "FAIL", "WARN", "INFO"):
            # Exclude TRACE/DEBUG/HTML for now (we could make that configurable...)
            return

        if skip_error and level in ("ERROR",):
            # We do this because in RF all the calls to 'log_message'
            # also generate a call to 'message', so, we want to skip
            # one of those (but note that the other way around isn't true
            # and some errors such as import errors are only reported
            # in 'message' and not 'log_message').
            return

        if self._skip_log_methods:
            if level not in ("ERROR", "FAIL", "WARN"):
                return

        html = message.get("html")
        return self._robot_output_impl.log_message(
            level, message["message"], self._get_time_delta(message), html
        )

    @_log_error
    def message(self, message):
        if message["level"] in ("FAIL", "ERROR"):
            return self.log_message(message, skip_error=False)

    @_log_error
    def close(self):
        self.robot_output_impl.close()


def iter_decoded_log_format(stream) -> Iterator[dict]:
    """
    :param stream:
        The stream which should be iterated in (anything with a `readlines()` method).

    :returns:
        An iterator which will decode the messages and provides a dictionary for
        each message found.

        Example of messages provided:

        {'message_type': 'V', 'version': '1'}
        {'message_type': 'T', 'initial_time': '2022-10-31T07:45:57.116'}
        {'message_type': 'ID', 'part': 1, 'id': 'gen-from-output-xml'}
        {'message_type': 'SS', 'name': 'Robot Check', 'suite_id': 's1', 'suite_source': 'x:\\vscode-robot\\local_test\\robot_check', 'time_delta_in_seconds': 0.3}
        {'message_type': 'ST', 'name': 'My task', 'suite_id': 's1-s1-t1', 'lineno': 5, 'time_delta_in_seconds': 0.2}
    """
    from ._decoder import iter_decoded_log_format

    return iter_decoded_log_format(stream)


__all_logger_instances__: "Set[_RobocorpLogger]" = set()


def config_logging_output(
    output_dir: Optional[str] = None,
    max_file_size: Optional[str] = None,
    max_files: int = 0,
    log_html: Optional[str] = None,
):
    logger = _RobocorpLogger(output_dir, max_file_size, max_files, log_html)
    __all_logger_instances__.add(logger)


def config_auto_logging(enable: bool = True) -> None:
    """
    The auto-logging works with a post-import hook where method calls are
    decorated accordingly.
    """


def stop_logging_methods():
    for rf_stream in __all_logger_instances__:
        rf_stream.stop_logging_methods()


def start_logging_methods():
    for rf_stream in __all_logger_instances__:
        rf_stream.start_logging_methods()


def stop_logging_variables():
    for rf_stream in __all_logger_instances__:
        rf_stream.stop_logging_variables()


def start_logging_variables():
    for rf_stream in __all_logger_instances__:
        rf_stream.start_logging_variables()


def hide_from_output(string_to_hide):
    for rf_stream in __all_logger_instances__:
        rf_stream.hide_from_output(string_to_hide)
