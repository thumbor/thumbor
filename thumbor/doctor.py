#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# pylint: disable=no-member

import argparse
import sys
from importlib import import_module
from os.path import abspath
from shutil import which

import colorful as cf

from thumbor import __release_date__, __version__
from thumbor.config import Config
from thumbor.ext import BUILTIN_EXTENSIONS
from thumbor.filters import BUILTIN_FILTERS

CHECK = "✅"
CROSS = "❎ "
WARNING = "⚠️"
ERROR = "⛔"


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


def header(msg, color=cf.yellow):
    print(color(msg))


def subheader(msg, color=cf.bold_coral):
    print(color(msg))
    newline()


def newline():
    print()


def check_filters(cfg):
    newline()
    errors = []

    to_check = BUILTIN_FILTERS
    if cfg is not None:
        to_check = cfg.FILTERS

    if to_check:
        subheader("Verifying thumbor filters...")

    for filter_name in to_check:
        try:
            import_module(filter_name)
            print(cf.bold_green(f"{CHECK} {filter_name}"))
        except ImportError as error:
            print(cf.bold_red(f"{CROSS} {filter_name}"))
            errors.append(
                format_error(
                    filter_name,
                    str(error),
                    "Can't import filter meaning this filter won't work.",
                )
            )

    return errors


def check_extensibility_modules(cfg):
    if cfg is None:
        return

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
        (lambda cfg: True, cfg.RESULT_STORAGE, "ResultStorage could not be imported."),
        (
            lambda cfg: cfg.UPLOAD_ENABLED,
            cfg.UPLOAD_PHOTO_STORAGE,
            "Uploading to thumbor is enabled and the Upload Storage could not be imported.",
        ),
    ]

    if any(c[0](cfg) for c in to_check):
        subheader("Verifying extensibility modules found in your thumbor.conf...")

    for should_check, module, error_message in to_check:
        if not should_check(cfg):
            continue
        try:
            import_module(module)
            print(cf.bold_green(f"{CHECK} {module}"))
        except ImportError as error:
            print(cf.bold_red(f"{CROSS} {module} - {error_message}"))
            errors.append(
                format_error(
                    module,
                    str(error),
                    error_message,
                )
            )

    return errors


def check_compiled_extensions():
    newline()
    subheader("Verifying thumbor compiled extensions...")
    errors = []

    for extension in BUILTIN_EXTENSIONS:
        ext_name = extension.replace("thumbor.ext.filters.", "")
        try:
            import_module(extension)
            print(cf.bold_green(f"{CHECK} {ext_name}"))
        except ImportError as error:
            print(cf.bold_red(f"{CROSS} {ext_name}"))
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
        { formatted_msg }
    """
    return result.strip()


def check_modules(cfg):
    newline()
    errors = []

    modules = [
        (
            "pycurl",
            (
                "Thumbor works much better with PyCurl. "
                "For more information visit http://pycurl.io/."
            ),
        ),
        (
            "cairosvg",
            "Thumbor uses CairoSVG for reading SVG files. "
            "For more information check https://cairosvg.org/.",
        ),
    ]

    if cfg is None or len(cfg.DETECTORS) != 0:
        modules.append(
            (
                "cv2",
                "Thumbor requires OpenCV for smart cropping. "
                "For more information check https://opencv.org/.",
            )
        )

    if modules:
        subheader("Verifying libraries support...")

    for module, error_message in modules:
        try:
            import_module(module)  # NOQA
            print(cf.bold_green(f"{CHECK} {module} is installed correctly."))
        except ImportError as error:
            print(cf.bold_red(f"{CROSS} {module} is not installed."))
            print(error_message)
            newline()
            errors.append(format_error(module, str(error), error_message))

    warn_modules = [
        (
            "pyexiv2",
            (
                "Thumbor uses exiv2 for reading image metadata.\n"
                "Don't worry. If you don't have exiv2 installed, "
                "Thumbor will still work.\nIt just means your images won't "
                "have EXIF metadata stored properly.\n"
                "For more information check "
                "https://python3-exiv2.readthedocs.io/en/latest/."
            ),
        ),
    ]

    warnings = []
    for module, error_message in warn_modules:
        try:
            import_module(module)  # NOQA
            print(cf.bold_green(f"{CHECK} {module} is installed correctly."))
        except ImportError as error:
            print(cf.bold_yellow(f"{CROSS} {module} is not installed."))
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

    if cfg is None or "thumbor.optimizers.gifv" in cfg.OPTIMIZERS:
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
            print(cf.bold_red(f"{CROSS} {program} is not installed."))
            print(error_message)
            newline()
            errors.append(
                format_error(program, f"Could not find {program}.", error_message)
            )
        else:
            print(cf.bold_green(f"{CHECK} {program} is installed correctly."))

    return errors


def main():
    """Converts a given url with the specified arguments."""

    options = get_options()

    cfg = None
    if options["config"] is not None:
        path = abspath(options["config"])
        cfg = Config.load(path, conf_name="thumbor.conf", lookup_paths=[])
        print(f'Using configuration file found at {options["config"]}')

    cf.use_style("solarized")
    if options["nocolor"]:
        cf.disable()

    newline()
    header(f"Thumbor v{__version__} (of {__release_date__})")

    newline()
    print(
        "Thumbor doctor will analyze your install and verify "
        "if everything is working as expected."
    )

    warnings, errors = check_modules(cfg)
    errors += check_compiled_extensions()
    errors += check_filters(cfg)
    errors += check_extensibility_modules(cfg)
    errors += check_extensions(cfg)

    newline()

    if warnings or errors:
        print(cf.bold_red("😞 Oh no! We found some things that could improve... 😞"))
        newline()

        if warnings:
            print(cf.bold_yellow(f"{WARNING}Warnings{WARNING}"))
            print("\n\n".join([f"{str(err)}" for err in warnings]))
            newline()

        if errors:
            print(cf.bold_red(f"{ERROR}Errors{ERROR}"))
            print("\n\n".join([f"{str(err)}" for err in errors]))
            newline()

        newline()
        print(
            cf.cyan(
                "If you don't know how to fix them, please open an issue with thumbor."
            )
        )
        print(
            cf.cyan(
                "Don't forget to copy this log and add it to the description of your issue."
            )
        )
        print("Open an issue at https://github.com/thumbor/thumbor/issues/new")
        sys.exit(1)
        return

    print(cf.bold_green("🎉 Congratulations! No errors found! 🎉"))


if __name__ == "__main__":
    main()
