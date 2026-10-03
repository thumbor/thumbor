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

# put() writes to "<final name>.<uuid4 hex>" and then renames it.
TEMP_FILE_RE = re.compile(r"\.[0-9a-f]{32}\Z")
SIDECAR_SUFFIXES = (".detectors.txt", ".txt")

Target = namedtuple(
    "Target", ["name", "root", "expiration", "other_root", "unused"]
)


class Cleaner:
    def __init__(self, options):
        self.delete = options.delete
        self.verbose = options.verbose
        self.temp_limit = options.temp_older_than
        self.totals = {}
        self.errors = 0

    def remove(self, path, size, category):
        if self.delete:
            try:
                os.unlink(path)
            except FileNotFoundError:
                return True
            except OSError as error:
                self.errors += 1
                print(
                    f"error: could not delete {path}: {error.strerror}",
                    file=sys.stderr,
                )
                return False

        count, total = self.totals.get(category, (0, 0))
        self.totals[category] = (count + 1, total + size)

        if self.verbose:
            print(f"  {category}: {path}")

        return True

    def walk(self, root, excluded):
        pending = [(root, realpath(root))]

        while pending:
            directory, real_directory = pending.pop()
            files = []

            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        real_path = join(real_directory, entry.name)
                        if entry.is_dir(follow_symlinks=False):
                            if real_path != excluded:
                                pending.append((entry.path, real_path))
                        elif entry.is_file(follow_symlinks=False):
                            files.append((entry, real_path, self.lstat(entry)))
            except FileNotFoundError:
                continue
            except OSError as error:
                self.errors += 1
                print(
                    f"error: could not read {directory}: {error.strerror}",
                    file=sys.stderr,
                )
                continue

            yield [file for file in files if file[2] is not None]

    def lstat(self, entry):
        try:
            return entry.stat(follow_symlinks=False)
        except FileNotFoundError:
            return None
        except OSError as error:
            self.errors += 1
            print(
                f"error: could not stat {entry.path}: {error.strerror}",
                file=sys.stderr,
            )
            return None

    def remove_temporary(self, entry, stat_result, now):
        if now - stat_result.st_mtime > self.temp_limit:
            self.remove(entry.path, stat_result.st_size, "temporary")

    def clean_storage(self, root, limit, excluded, protected):
        now = time.time()

        for files in self.walk(root, excluded):
            self.clean_storage_directory(files, limit, protected, now)

    def clean_storage_directory(self, files, limit, protected, now):
        removed_images = set()
        sidecars = []

        for entry, real_path, stat_result in files:
            if real_path == protected:
                continue
            if TEMP_FILE_RE.search(entry.name):
                self.remove_temporary(entry, stat_result, now)
            elif sidecar_owner(entry.name) is not None:
                sidecars.append((entry, stat_result))
            elif now - stat_result.st_mtime > limit:
                if self.remove(entry.path, stat_result.st_size, "expired"):
                    removed_images.add(entry.name)

        present = {entry.name for entry, _, _ in files}
        self.clean_sidecars(sidecars, removed_images, present, now - limit)

    def clean_sidecars(self, sidecars, removed_images, present, cutoff):
        for entry, stat_result in sidecars:
            owner = sidecar_owner(entry.name)
            if owner in removed_images:
                self.remove(entry.path, stat_result.st_size, "sidecar")
            elif owner not in present and stat_result.st_mtime < cutoff:
                self.remove(entry.path, stat_result.st_size, "orphan sidecar")

    def clean_result_storage(self, root, limit, excluded):
        now = time.time()

        for files in self.walk(root, excluded):
            for entry, _, stat_result in files:
                if TEMP_FILE_RE.search(entry.name):
                    self.remove_temporary(entry, stat_result, now)
                elif now - stat_result.st_mtime > limit:
                    self.remove(entry.path, stat_result.st_size, "expired")

    def print_totals(self):
        if not self.totals:
            print("  nothing to delete")
        for category, (count, total) in sorted(self.totals.items()):
            print(f"  {category}: {count} files, {total} bytes")
        self.totals = {}


def sidecar_owner(name):
    for suffix in SIDECAR_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return None


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
        help="Use this age in seconds instead of the configured expiration.",
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

    cleaner = Cleaner(options)

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
            print("  expiration is disabled in the configuration, skipping")
            continue

        limit = max_age + options.grace
        print(f"  files older than {limit} seconds are expired")
        excluded = realpath(target.other_root)

        if target.name == "storage":
            protected = realpath(
                FileStorage(Context(config=config)).path_on_filesystem(
                    BLACKLIST_KEY
                )
            )
            cleaner.clean_storage(target.root, limit, excluded, protected)
        else:
            cleaner.clean_result_storage(target.root, limit, excluded)

        cleaner.print_totals()

    if not options.delete:
        print("dry run: nothing was deleted, pass --delete to delete")

    return 1 if cleaner.errors else 0


if __name__ == "__main__":
    sys.exit(main())
