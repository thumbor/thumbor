# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import importlib
from unittest import mock

import pytest

from thumbor.doctor import check_modules, run_doctor


@pytest.mark.parametrize("module_name", ["pycurl", "cairosvg"])
@pytest.mark.parametrize("error_type", [ImportError, OSError])
def test_reports_module_load_failure(capsys, module_name, error_type):
    message = f"Cannot load a dependency of {module_name}"

    def import_module(name):
        if name == module_name:
            raise error_type(message)
        return mock.Mock()

    with mock.patch(
        "thumbor.doctor.import_module", side_effect=import_module
    ) as importer:
        warnings, errors = check_modules()

    assert not warnings
    assert len(errors) == 1
    assert module_name in errors[0]
    assert message in errors[0]
    assert f"{module_name} could not be loaded." in capsys.readouterr().out
    assert importer.call_args_list == [
        mock.call("pycurl"),
        mock.call("cairosvg"),
    ]


def test_doctor_finishes_when_cairo_library_is_missing(capsys):
    message = "cannot load library libcairo-2.dll: error 0x7e"

    def import_module(name):
        if name == "cairosvg":
            raise OSError(message)
        return importlib.import_module(name)

    with mock.patch("thumbor.doctor.import_module", side_effect=import_module):
        with pytest.raises(SystemExit) as error:
            run_doctor({"nocolor": True, "config": None}, print_version=False)

    output = capsys.readouterr().out
    assert error.value.code == 1
    assert "Verifying thumbor compiled extensions..." in output
    assert "Error Message:" in output
    assert message in output
    assert (
        "Thumbor uses CairoSVG for reading SVG files. "
        "For more information check https://cairosvg.org/."
    ) in output.splitlines()
    assert "Need Help" in output


def test_get_doctor_output(capsys, doctor_output):
    run_doctor(
        {
            "nocolor": True,
            "config": "./tests/invalid-thumbor.conf",
        },
        print_version=False,
        exit_with_error=False,
    )
    assert capsys.readouterr().out == doctor_output


def test_get_doctor_output_no_config(capsys, doctor_output_no_config):
    run_doctor(
        {
            "nocolor": True,
            "config": None,
        },
        print_version=False,
        exit_with_error=False,
    )
    assert capsys.readouterr().out == doctor_output_no_config
