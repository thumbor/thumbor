# https://github.com/python-poetry/poetry/issues/11

import glob
import os
from distutils.command.build_ext import build_ext
from distutils.core import Extension
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError


def filter_extension_module(name, lib_objs, lib_headers):
    return Extension(
        "thumbor.ext.filters.%s" % name,
        ["thumbor/ext/filters/%s.c" % name] + lib_objs,
        libraries=["m"],
        include_dirs=["thumbor/ext/filters/lib"],
        depends=["setup.py"] + lib_objs + lib_headers,
        extra_compile_args=["-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter"],
    )


def gather_filter_extensions():
    files = glob.glob("thumbor/ext/filters/_*.c")
    lib_objs = glob.glob("thumbor/ext/filters/lib/*.c")
    lib_headers = glob.glob("thumbor/ext/filters/lib/*.h")

    return [
        filter_extension_module(f[0:-2].split("/")[-1], lib_objs, lib_headers)
        for f in files
    ]


class BuildFailed(Exception):
    pass


class ExtBuilder(build_ext):
    # This class allows C extension building to fail.

    def run(self):
        try:
            build_ext.run(self)
        except (DistutilsPlatformError, FileNotFoundError):
            pass

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (
            CCompilerError,
            DistutilsExecError,
            DistutilsPlatformError,
            ValueError,
        ):
            pass


def build(setup_kwargs):
    """Needed for the poetry building interface."""
    if "CFLAGS" not in os.environ:
        os.environ["CFLAGS"] = ""

    setup_kwargs.update(
        dict(
            ext_modules=gather_filter_extensions(),
            cmdclass={"build_ext": ExtBuilder},
            packages=["thumbor"],
            package_dir={"thumbor": "thumbor"},
            include_package_data=True,
            package_data={"": ["*.xml"]},
        )
    )
