# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import argparse
import os
import re
import sys
import time
from collections import namedtuple
from os.path import join, realpath

from derpconf.config import ConfigurationError

from thumbor.context import Context
from thumbor.server import get_config
from thumbor.storages.file_storage import Storage as FileStorage

FILE_STORAGE = "thumbor.storages.file_storage"
MIXED_STORAGE = "thumbor.storages.mixed_storage"
FILE_RESULT_STORAGE = "thumbor.result_storages.file_storage"
BLACKLIST_KEY = "blacklist.txt"

# The file storage keeps an image at "<2 hex>/<38 hex>", its security key and
# detector data next to it, and put() writes to "<final name>.<uuid4 hex>"
# before renaming. Anything else under the root was not written by thumbor.
STORAGE_DIRECTORY_RE = re.compile(r"[0-9a-f]{2}")
STORAGE_FILE_RE = re.compile(
    r"(?P<image>[0-9a-f]{38})"
    r"(?P<sidecar>\.detectors\.txt|\.txt)?"
    r"(?P<temporary>\.[0-9a-f]{32})?"
)
KEY_SUFFIX = ".txt"
RESULT_TEMPORARY_RE = re.compile(r"[0-9a-f]{36}\.[0-9a-f]{32}")


def printable(path):
    return os.fsencode(path).decode("utf-8", "backslashreplace")


Target = namedtuple(
    "Target", ["name", "root", "expiration", "other_root", "unused"]
)


class Cleaner:
    def __init__(self, options, config):
        self.delete = options.delete
        self.verbose = options.verbose
        self.now = time.time()
        self.temporary_cutoff = self.now - options.temp_older_than
        self.blacklist = realpath(
            FileStorage(Context(config=config)).path_on_filesystem(
                BLACKLIST_KEY
            )
        )
        self.keeps_orphan_keys = not stores_images_in_file_storage(config)
        self.totals = {}
        self.errors = 0

    def report(self, action, path, error):
        self.errors += 1
        print(
            f"error: could not {action} {path}: {error.strerror}",
            file=sys.stderr,
        )

    def lstat(self, path):
        try:
            return os.lstat(path)
        except FileNotFoundError:
            return None
        except OSError as error:
            self.report("stat", path, error)
            return None

    def scan(self, directory):
        directories = []
        files = []

        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        directories.append(entry)
                    elif entry.is_file(follow_symlinks=False):
                        files.append((entry, self.lstat(entry.path)))
        except FileNotFoundError:
            return [], []
        except OSError as error:
            self.report("read", directory, error)
            return [], []

        return directories, [file for file in files if file[1] is not None]

    def remove(self, entry, stat_result, category):
        if self.delete:
            try:
                if has_changed(entry.path, stat_result):
                    return False
                os.unlink(entry.path)
            except FileNotFoundError:
                return True
            except OSError as error:
                self.report("delete", entry.path, error)
                return False

        count, total = self.totals.get(category, (0, 0))
        self.totals[category] = (count + 1, total + stat_result.st_size)

        if self.verbose:
            print(f"  {category}: {printable(entry.path)}")

        return True

    def remove_temporary(self, entry, stat_result):
        if stat_result.st_mtime < self.temporary_cutoff:
            self.remove(entry, stat_result, "temporary")

    def clean_storage(self, root, limit, excluded):
        cutoff = self.get_cutoff(limit)
        real_root = realpath(root)
        directories, _ = self.scan(root)

        for directory in directories:
            real_directory = join(real_root, directory.name)
            if (
                STORAGE_DIRECTORY_RE.fullmatch(directory.name)
                and real_directory != excluded
            ):
                _, files = self.scan(directory.path)
                self.clean_storage_directory(files, real_directory, cutoff)

    def clean_storage_directory(self, files, real_directory, cutoff):
        images = set()
        removed_images = set()
        sidecars = []

        for entry, stat_result in files:
            match = STORAGE_FILE_RE.fullmatch(entry.name)
            if match is None:
                continue
            if match["temporary"]:
                self.remove_temporary(entry, stat_result)
            elif match["sidecar"]:
                sidecars.append((entry, stat_result, match))
            else:
                images.add(entry.name)
                is_blacklist = (
                    join(real_directory, entry.name) == self.blacklist
                )
                if (
                    not is_blacklist
                    and is_older_than(stat_result, cutoff)
                    and self.remove(entry, stat_result, "expired")
                ):
                    removed_images.add(entry.name)

        self.clean_sidecars(sidecars, images, removed_images, cutoff)

    def clean_sidecars(self, sidecars, images, removed_images, cutoff):
        for entry, stat_result, match in sidecars:
            if match["image"] in removed_images:
                self.remove(entry, stat_result, "sidecar")
            elif (
                match["image"] not in images
                and is_older_than(stat_result, cutoff)
                and self.deletes_orphan(match["sidecar"])
            ):
                self.remove(entry, stat_result, "orphan sidecar")

    def deletes_orphan(self, suffix):
        # thumbor never expires a security key, so when the images live in
        # another storage there is no telling whether one is still needed.
        return suffix != KEY_SUFFIX or not self.keeps_orphan_keys

    def clean_result_storage(self, root, limit, excluded):
        cutoff = self.get_cutoff(limit)
        pending = [(root, realpath(root))]

        while pending:
            directory, real_directory = pending.pop()
            directories, files = self.scan(directory)

            for entry in directories:
                real_path = join(real_directory, entry.name)
                if real_path != excluded:
                    pending.append((entry.path, real_path))

            for entry, stat_result in files:
                if RESULT_TEMPORARY_RE.fullmatch(entry.name):
                    self.remove_temporary(entry, stat_result)
                elif is_older_than(stat_result, cutoff):
                    self.remove(entry, stat_result, "expired")

    def get_cutoff(self, limit):
        return None if limit is None else self.now - limit

    def print_totals(self):
        if not self.totals:
            print("  nothing to delete")
        for category, (count, total) in sorted(self.totals.items()):
            print(f"  {category}: {count} files, {total} bytes")
        self.totals = {}


def is_older_than(stat_result, cutoff):
    return cutoff is not None and stat_result.st_mtime < cutoff


def has_changed(path, stat_result):
    # A whole directory is listed before anything in it is deleted, so a file
    # may have been stored again since it was measured.
    current = os.lstat(path)
    return (current.st_ino, current.st_mtime_ns) != (
        stat_result.st_ino,
        stat_result.st_mtime_ns,
    )


def positive_seconds(value):
    seconds = int(value)
    if seconds <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return seconds


def non_negative_seconds(value):
    seconds = int(value)
    if seconds < 0:
        raise argparse.ArgumentTypeError("must not be negative")
    return seconds


def get_options(arguments):
    parser = argparse.ArgumentParser(
        description=(
            "Delete expired files from thumbor's file storage and file "
            "result storage. Without --delete it only reports what it would "
            "delete."
        )
    )
    parser.add_argument(
        "-c",
        "--conf",
        default=None,
        help="The path of the thumbor configuration file "
        "[default: the same lookup as the thumbor server].",
    )
    parser.add_argument(
        "--storage",
        action="store_true",
        help="Clean FILE_STORAGE_ROOT_PATH.",
    )
    parser.add_argument(
        "--result-storage",
        action="store_true",
        help="Clean RESULT_STORAGE_FILE_STORAGE_ROOT_PATH.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the files instead of only reporting them.",
    )
    parser.add_argument(
        "--include-uploads",
        action="store_true",
        help="Allow --storage when uploaded images share "
        "FILE_STORAGE_ROOT_PATH. Uploads older than the expiration are "
        "deleted too.",
    )
    parser.add_argument(
        "--older-than",
        metavar="SECONDS",
        type=positive_seconds,
        default=None,
        help="Use this age in seconds instead of the configured expiration. "
        "--grace is still added to it.",
    )
    parser.add_argument(
        "--grace",
        metavar="SECONDS",
        type=non_negative_seconds,
        default=3600,
        help="Seconds added to the expiration before a file is deleted "
        "[default: %(default)s].",
    )
    parser.add_argument(
        "--temp-older-than",
        metavar="SECONDS",
        type=positive_seconds,
        default=3600,
        help="Age in seconds after which leftover temporary files are "
        "deleted [default: %(default)s].",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print every file that is deleted or would be deleted.",
    )

    options = parser.parse_args(arguments)

    if not options.storage and not options.result_storage:
        parser.error(
            "at least one of --storage and --result-storage is required"
        )

    return options


def get_expiration(config, name):
    value = getattr(config, name)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number of seconds or None")
    if value <= 0:
        return None
    return value


def stores_uploads_in_file_storage(config):
    if not config.UPLOAD_ENABLED:
        return False
    if config.UPLOAD_PHOTO_STORAGE == MIXED_STORAGE:
        return config.MIXED_STORAGE_FILE_STORAGE == FILE_STORAGE
    return config.UPLOAD_PHOTO_STORAGE == FILE_STORAGE


def stores_images_in_file_storage(config):
    if config.STORAGE == MIXED_STORAGE:
        return config.MIXED_STORAGE_FILE_STORAGE == FILE_STORAGE
    return config.STORAGE == FILE_STORAGE


def uses_file_storage(config):
    modules = {config.STORAGE}
    if config.STORAGE == MIXED_STORAGE:
        modules.update(
            (
                config.MIXED_STORAGE_FILE_STORAGE,
                config.MIXED_STORAGE_CRYPTO_STORAGE,
                config.MIXED_STORAGE_DETECTOR_STORAGE,
            )
        )
    return FILE_STORAGE in modules or stores_uploads_in_file_storage(config)


def get_targets(config, options):
    storage_root = config.FILE_STORAGE_ROOT_PATH
    result_root = config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH
    targets = []

    if realpath(storage_root) == realpath(result_root):
        raise ValueError(
            "FILE_STORAGE_ROOT_PATH and RESULT_STORAGE_FILE_STORAGE_ROOT_PATH "
            "are the same directory, so their files cannot be told apart"
        )

    if options.storage:
        if (
            stores_uploads_in_file_storage(config)
            and not options.include_uploads
        ):
            raise ValueError(
                "uploaded images are stored in FILE_STORAGE_ROOT_PATH and "
                "expire with STORAGE_EXPIRATION_SECONDS like any other file "
                "there; pass --include-uploads to delete them as well"
            )
        targets.append(
            Target(
                "storage",
                storage_root,
                get_expiration(config, "STORAGE_EXPIRATION_SECONDS"),
                result_root,
                not uses_file_storage(config),
            )
        )

    if options.result_storage:
        targets.append(
            Target(
                "result storage",
                result_root,
                get_expiration(config, "RESULT_STORAGE_EXPIRATION_SECONDS"),
                storage_root,
                config.RESULT_STORAGE != FILE_RESULT_STORAGE,
            )
        )

    return targets


def main(arguments=None):
    options = get_options(arguments)

    try:
        config = get_config(options.conf)
        targets = get_targets(config, options)
    except (ConfigurationError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    cleaner = Cleaner(options, config)

    for target in targets:
        print(f"{target.name}: {target.root}")

        if target.unused:
            print(
                f"  note: thumbor is not configured to use the file {target.name}"
            )

        if not os.path.isdir(target.root):
            print("  directory does not exist, nothing to clean")
            continue

        max_age = options.older_than or target.expiration
        if max_age is None:
            limit = None
            print(
                "  expiration is disabled in the configuration, only "
                "temporary files are cleaned"
            )
        else:
            limit = max_age + options.grace
            print(f"  files older than {limit} seconds are expired")

        excluded = realpath(target.other_root)

        if target.name == "storage":
            cleaner.clean_storage(target.root, limit, excluded)
        else:
            cleaner.clean_result_storage(target.root, limit, excluded)

        cleaner.print_totals()

    if not options.delete:
        print("dry run: nothing was deleted, pass --delete to delete")

    return 1 if cleaner.errors else 0


if __name__ == "__main__":
    sys.exit(main())
