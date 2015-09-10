#!/usr/bin/env python

import mock

from paasta_tools.utils import PaastaColors
import chronos_serviceinit


def test_format_chronos_job_status_disabled():
    example_job = {
        'disabled': True,
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.red("Disabled") in actual


def test_format_chronos_job_status_enabled():
    example_job = {
        'disabled': False,
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.green("Enabled") in actual


def test_format_chronos_job_status_no_last_run():
    example_job = {
        'lastError': '',
        'lastSuccess': '',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.yellow("New") in actual


def test_format_chronos_job_status_failure_no_success():
    example_job = {
        'lastError': '2015-04-20T23:20:00.420Z',
        'lastSuccess': '',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.red("Fail") in actual


def test_format_chronos_job_status_success_no_failure():
    example_job = {
        'lastError': '',
        'lastSuccess': '2015-04-20T23:20:00.420Z',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.green("OK") in actual


def test_format_chronos_job_status_failure_and_then_success():
    example_job = {
        'lastError': '2015-04-20T23:20:00.420Z',
        'lastSuccess': '2015-04-21T23:20:00.420Z',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.green("OK") in actual


def test_status_chronos_job_is_deployed():
    jobs = [{'name': 'my_service my_instance gityourmom configyourdad'}]
    with mock.patch('chronos_serviceinit.format_chronos_job_status',
                    autospec=True, return_value='job_status_output'):
        actual = chronos_serviceinit.status_chronos_job(
            jobs,
        )
        assert actual == 'job_status_output'


def test_status_chronos_job_is_not_deployed():
    jobs = []
    with mock.patch('chronos_serviceinit.format_chronos_job_status',
                    autospec=True, return_value='job_status_output'):
        actual = chronos_serviceinit.status_chronos_job(
            jobs,
        )
        assert 'not setup' in actual


def test_status_chronos_job_multiple_jobs():
    jobs = [
        {'name': 'my_service my_instance gityourmom configyourdad'},
        {'name': 'my_service my_instance gityourmom configyourbro'},
    ]
    with mock.patch('chronos_serviceinit.format_chronos_job_status',
                    autospec=True, return_value='job_status_output'):
        actual = chronos_serviceinit.status_chronos_job(
            jobs,
        )
        assert actual == 'job_status_output\njob_status_output'
