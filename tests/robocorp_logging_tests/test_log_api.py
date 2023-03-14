def test_log_api(datadir, data_regression, tmpdir):
    import robocorp_logging

    with robocorp_logging.add_logging_output(
        tmpdir, max_file_size="30kb", max_files=1, log_html=tmpdir.join("log.html")
    ):

        robocorp_logging.log_start_suite("Root Suite", "root", str(tmpdir))
        robocorp_logging.log_end_suite("Root Suite", "root", str(tmpdir))
