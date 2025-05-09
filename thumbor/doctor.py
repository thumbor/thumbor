#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# pylint: disable=no-member,line-too-long

import argparse
import sys
from importlib import import_module
from os.path import abspath
from shutil import which
from typing import List

from colorama import Fore, init

from thumbor import __release_date__, __version__
from thumbor.config import Config
from thumbor.ext import BUILTIN_EXTENSIONS

CHECK = "✅"
CROSS = "❎"
WARNING = "⚠️"
ERROR = "⛔"
QUESTION = "❓"


def get_options():
    parser = argparse.ArgumentParser(description="thumbor doctor")

    parser.add_argument(
        "-n",
        "--nocolor",
        action="store_true",
        help="Disables coloring of thumbor doctor",
    )

    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help=(
            "thumbor configuration file. If specified "
            "thumbor-doctor can be fine tuned."
        ),
    )

    options = parser.parse_args()

    return {
        "nocolor": options.nocolor,
        "config": options.config,
    }


def header(msg):
    print(f"{Fore.YELLOW}{msg}")


def subheader(msg):
    print(f"{Fore.MAGENTA}{msg}")
    newline()


def print_error(msg):
    print(f"{Fore.RED}{msg}")


def print_success(msg):
    print(f"{Fore.GREEN}{msg}")


def print_warning(msg):
    print(f"{Fore.YELLOW}{msg}")


def print_info(msg):
    print(f"{Fore.CYAN}{msg}")


def newline():
    print()


def check_extensibility_modules(cfg):
    if cfg is None:
        return []

    newline()
    errors = []

    to_check = [
        (
            lambda cfg: True,
            cfg.STORAGE,
            "Storage for source images could not be imported.",
        ),
        (
            lambda cfg: True,
            cfg.LOADER,
            "Loader for source images could not be imported.",
        ),
        (
            lambda cfg: True,
            cfg.RESULT_STORAGE,
            "ResultStorage could not be imported.",
        ),
        (
            lambda cfg: True,
            cfg.ENGINE,
            "Engine for transforming images could not be imported.",
        ),
        (
            lambda cfg: cfg.UPLOAD_ENABLED,
            cfg.UPLOAD_PHOTO_STORAGE,
            "Uploading to thumbor is enabled and the Upload Storage could not be imported.",
        ),
        (
            lambda cfg: True,
            sorted(cfg.DETECTORS),
            "Detector could not be imported.",
        ),
        (
            lambda cfg: True,
            sorted(cfg.FILTERS),
            "Filter could not be imported.",
        ),
        (
            lambda cfg: True,
            sorted(cfg.OPTIMIZERS),
            "Optimizer could not be imported.",
        ),
        (
            lambda cfg: cfg.USE_CUSTOM_ERROR_HANDLING,
            cfg.ERROR_HANDLER_MODULE,
            "Custom error handling is enabled and the "
            "error handler module could not be imported.",
        ),
        (
            lambda cfg: True,
            sorted(cfg.HANDLER_LISTS),
            "Custom http handler could not be imported.",
        ),
    ]

    if any(c[0](cfg) for c in to_check):
        subheader(
            "Verifying extensibility modules found in your thumbor.conf..."
        )

    for should_check, modules, error_message in to_check:
        if not should_check(cfg):
            continue

        if not isinstance(modules, (list, tuple)):
            modules = [modules]

        for module in modules:
            if not module:
                continue

            try:
                import_module(module)
                print_success(f"{CHECK} {module}")
            except ImportError as error:
                print_error(f"{CROSS} {module} - {error_message}")
                errors.append(
                    format_error(
                        module,
                        str(error),
                        error_message,
                    )
                )

    if cfg and (
        has_cv_detector(cfg.DETECTORS) or has_redeye_filter(cfg.FILTERS)
    ):
        try:
            import cv2  # noqa pylint: disable=unused-import,import-outside-toplevel
            import numpy  # noqa pylint: disable=unused-import,import-outside-toplevel
        except ImportError as error:
            print_error(
                f"{CROSS} OpenCV Detectors and Filters - {error_message}"
            )
            errors.append(
                format_error(
                    "Could not import OpenCV, so detectors and filters "
                    "that depend on it will not work",
                    str(error),
                    error_message,
                )
            )

    return errors


def has_redeye_filter(filters: List[str]):
    return any(filter_module.endswith("redeye") for filter_module in filters)


def has_cv_detector(detectors: List[str]):
    cv_detectors = [
        "face_detector",
        "feature_detector",
        "glasses_detector",
        "local_detector",
        "profile_detector",
    ]

    for detector in detectors:
        if any(cv_detector.endswith(detector) for cv_detector in cv_detectors):
            return True

    return False


def check_compiled_extensions():
    newline()
    subheader("Verifying thumbor compiled extensions...")
    errors = []

    for extension in BUILTIN_EXTENSIONS:
        ext_name = extension.replace("thumbor.ext.filters.", "")
        try:
            import_module(extension)
            print_success(f"{CHECK} {ext_name}")
        except ImportError as error:
            print_error(f"{CROSS} {ext_name}")
            errors.append(
                format_error(
                    f"Extension {extension}",
                    str(error),
                    (
                        "Extension could not be compiled. "
                        "This will lead to filter being disabled."
                    ),
                )
            )

    return errors


def format_error(dependency, err, msg):
    formatted_msg = "\n\t".join(msg.split("\n"))
    result = f"""
* {dependency}
    Error Message:
        {err}

    Error Description:
        {formatted_msg}
    """
    return result.strip()


def check_modules():
    newline()
    errors = []

    modules = [
        (
            "pycurl",
            "Thumbor works much better with PyCurl. "
            "For more information visit http://pycurl.io/.",
        ),
        (
            "cairosvg",
            "Thumbor uses CairoSVG for reading SVG files. "
            "For more information check https://cairosvg.org/.",
        ),
    ]

    if modules:
        subheader("Verifying libraries support...")

    for module, error_message in modules:
        try:
            import_module(module)  # NOQA
            print_success(f"{CHECK} {module} is installed correctly.")
        except ImportError as error:
            print_error(f"{CROSS} {module} is not installed.")
            print(error_message)
            newline()
            errors.append(format_error(module, str(error), error_message))

    warn_modules = []

    warnings = []
    for module, error_message in warn_modules:
        try:
            import_module(module)  # NOQA
            print_success(f"{CHECK} {module} is installed correctly.")
        except ImportError as error:
            print_warning(f"{CROSS} {module} is not installed.")
            print(error_message)
            newline()
            warnings.append(format_error(module, str(error), error_message))

    return warnings, errors


def check_extensions(cfg):
    newline()

    errors = []
    programs = []

    if cfg is None or "thumbor.optimizers.jpegtran" in cfg.OPTIMIZERS:
        programs.append(
            (
                "jpegtran",
                (
                    "Thumbor uses jpegtran for optimizing JPEG images. "
                    "For more information visit "
                    "https://linux.die.net/man/1/jpegtran."
                ),
            )
        )

    if cfg is None or "thumbor_plugins.optimizers.gifv" in cfg.OPTIMIZERS:
        programs.append(
            (
                "ffmpeg",
                "Thumbor uses ffmpeg for rendering animated images as GIFV. "
                "For more information visit https://www.ffmpeg.org/.",
            )
        )

    if cfg is None or cfg.USE_GIFSICLE_ENGINE:
        programs.append(
            (
                "gifsicle",
                "Thumbor uses gifsicle for better processing of GIF images. "
                "For more information visit https://www.lcdf.org/gifsicle/.",
            )
        )

    if programs:
        subheader("Verifying extension programs...")

    for program, error_message in programs:
        path = which(program)
        if path is None:
            print_error(f"{CROSS} {program} is not installed.")
            print(error_message)
            newline()
            errors.append(
                format_error(
                    program, f"Could not find {program}.", error_message
                )
            )
        else:
            print_success(f"{CHECK} {program} is installed correctly.")

    return errors


def check_security(cfg):
    subheader("Verifying security...")
    errors = []
    warnings = []

    if cfg is None:
        return errors, warnings

    if cfg.SECURITY_KEY == "MY_SECURE_KEY":
        print_error(f"{CROSS} Using default security key.")

        warnings.append(
            format_error(
                "Security",
                "Using default security key configuration in thumbor.conf.",
                "You should specify a unique security key for thumbor or "
                "use a command line param to specify a security key.\n"
                "For more information visit "
                "https://thumbor.readthedocs.io/en/latest/running.html",
            )
        )

    if cfg.ALLOW_UNSAFE_URL:
        print_error(f"{CROSS} Allowing unsafe URLs.")

        errors.append(
            format_error(
                "Security",
                "Unsafe URLs are enabled.",
                "It is STRONGLY recommended that you turn off "
                "ALLOW_UNSAFE_URLS flag in production environments "
                "as this can lead to DDoS attacks against thumbor.\n"
                "For more information visit "
                "https://thumbor.readthedocs.io/en/latest/security.html",
            )
        )

    return errors, warnings


def load_config(config_path):
    cfg = None
    if config_path is not None:
        path = abspath(config_path)
        cfg = Config.load(path, conf_name="thumbor.conf", lookup_paths=[])
        print(f"Using configuration file found at {config_path}")
    return cfg


def configure_colors(nocolor):
    if nocolor:
        init(strip=True, convert=False)
    else:
        init(autoreset=True)


def print_header(print_version=True):
    if print_version:
        newline()
        header(f"Thumbor v{__version__} (of {__release_date__})")
    newline()
    print(
        "Thumbor doctor will analyze your install and verify "
        "if everything is working as expected."
    )


def check_everything(cfg):
    warnings, errors = check_modules()
    errors += check_compiled_extensions()
    errors += check_extensibility_modules(cfg)
    errors += check_extensions(cfg)

    sec_err, sec_warn = check_security(cfg)
    errors += sec_err
    warnings += sec_warn

    newline()
    return warnings, errors


def print_results(warnings, errors):
    if not warnings and not errors:
        print_success("🎉 Congratulations! No errors found! 🎉")
        return

    print_error("😞 Oh no! We found some things that could improve... 😞")
    newline()

    if warnings:
        print_warning(f"{WARNING}Warnings{WARNING}")
        print("\n\n".join([f"{str(err)}" for err in warnings]))
        newline()

    if errors:
        print_error(f"{ERROR}Errors{ERROR}")
        print("\n\n".join([f"{str(err)}" for err in errors]))
        newline()

    subheader(f"{QUESTION}Need Help{QUESTION}")
    print_info(
        "If you don't know how to fix the above problems, please open an issue with thumbor."
    )
    print_info("Don't forget to copy this log and add it to the description.")
    print("Open an issue at https://github.com/thumbor/thumbor/issues/new")


def run_doctor(options, print_version=True, exit_with_error=True):
    cfg = load_config(options["config"])
    configure_colors(options["nocolor"])

    print_header(print_version)
    warnings, errors = check_everything(cfg)
    print_results(warnings, errors)

    if exit_with_error and errors:
        sys.exit(1)


def main():
    """Verifies the current environment for problems with thumbor"""

    options = get_options()
    run_doctor(options, print_version=True, exit_with_error=True)


if __name__ == "__main__":
    main()
