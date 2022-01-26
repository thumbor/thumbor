#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from thumbor.doctor import run_doctor


def test_get_doctor_output(snapshot, capsys):
    run_doctor(
        {
            "nocolor": True,
            "config": "./tests/invalid-thumbor.conf",
        },
        print_version=False,
        exit_with_error=False,
        check_pyexiv=False,
    )
    result = capsys.readouterr()
    snapshot.assert_match(result.out)


def test_get_doctor_output_no_config(snapshot, capsys):
    run_doctor(
        {
            "nocolor": True,
            "config": None,
        },
        print_version=False,
        exit_with_error=False,
        check_pyexiv=False,
    )
    result = capsys.readouterr()
    snapshot.assert_match(result.out)
