def test_basic(datadir, data_regression, tmpdir):
    import robocorp_logging
    from imp import reload

    robocorp_logging.config_logging_output(
        tmpdir, max_file_size="30kb", max_files=1, log_html=tmpdir.join("log.html")
    )

    robocorp_logging.config_auto_logging()

    from robot_out_stream_tests._resources import check

    check = reload(check)
    check.some_method()
