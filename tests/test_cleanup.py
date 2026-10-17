# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import os
import time
from pathlib import Path
from unittest import mock

import pytest

from thumbor.cleanup import main
from thumbor.config import Config
from thumbor.context import Context
from thumbor.storages.file_storage import Storage as FileStorage

EXPIRATION = 60 * 60
OLD = EXPIRATION + 3600 + 600
WITHIN_GRACE = EXPIRATION + 600
FRESH = 60
IMAGE = "ab/" + "c" * 38
TEMP_SUFFIX = "." + "f" * 32


def write_config(tmp_path, settings):
    settings.setdefault("FILE_STORAGE_ROOT_PATH", str(tmp_path / "storage"))
    settings.setdefault(
        "RESULT_STORAGE_FILE_STORAGE_ROOT_PATH", str(tmp_path / "result")
    )
    path = tmp_path / "thumbor.conf"
    path.write_text(
        "".join(f"{key} = {value!r}\n" for key, value in settings.items()),
        encoding="utf-8",
    )
    return str(path)


def run(tmp_path, *arguments, **settings):
    return main(["-c", write_config(tmp_path, settings), *arguments])


def make_file(path, age, content=b"x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    mtime = time.time() - age
    os.utime(path, (mtime, mtime))
    return path


def storage_file(tmp_path, name, age):
    return make_file(tmp_path / "storage" / name, age)


def result_file(tmp_path, name, age):
    return make_file(tmp_path / "result" / name, age)


def test_dry_run_reports_expired_file_without_deleting(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(tmp_path, "--storage", STORAGE_EXPIRATION_SECONDS=EXPIRATION)

    assert code == 0
    assert image.exists()
    out = capsys.readouterr().out
    assert "expired: 1 files, 1 bytes" in out
    assert "dry run: nothing was deleted" in out


def test_delete_removes_expired_file(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()
    out = capsys.readouterr().out
    assert "expired: 1 files, 1 bytes" in out
    assert "dry run" not in out


def test_keeps_files_within_the_grace_window(tmp_path):
    image = storage_file(tmp_path, IMAGE, WITHIN_GRACE)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert image.exists()


def test_grace_can_be_shortened(tmp_path):
    image = storage_file(tmp_path, IMAGE, WITHIN_GRACE)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        "--grace",
        "0",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()


@pytest.mark.parametrize("expiration", [None, 0, -1])
def test_storage_without_expiration_deletes_nothing(
    tmp_path, capsys, expiration
):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=expiration,
    )

    assert code == 0
    assert image.exists()
    assert "expiration is disabled" in capsys.readouterr().out


@pytest.mark.parametrize("expiration", [None, 0])
def test_result_storage_without_expiration_deletes_nothing(
    tmp_path, capsys, expiration
):
    image = result_file(tmp_path, "default/ab/cd/" + "e" * 36, OLD)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        RESULT_STORAGE_EXPIRATION_SECONDS=expiration,
    )

    assert code == 0
    assert image.exists()
    assert "expiration is disabled" in capsys.readouterr().out


def test_older_than_overrides_the_configured_expiration(tmp_path):
    expired = storage_file(tmp_path, IMAGE, 60 + 3600 + 60)
    within_grace = storage_file(tmp_path, "ab/" + "d" * 38, 60 + 1800)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        "--older-than",
        "60",
        STORAGE_EXPIRATION_SECONDS=None,
    )

    assert code == 0
    assert not expired.exists()
    assert within_grace.exists()


def test_grace_zero_uses_older_than_as_is(tmp_path):
    image = storage_file(tmp_path, IMAGE, 60 + 1800)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        "--older-than",
        "60",
        "--grace",
        "0",
        STORAGE_EXPIRATION_SECONDS=None,
    )

    assert code == 0
    assert not image.exists()


def test_refuses_storage_with_uploads_in_file_storage(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        UPLOAD_ENABLED=True,
    )

    assert code == 2
    assert image.exists()
    assert "--include-uploads" in capsys.readouterr().err


def test_refuses_storage_with_uploads_in_mixed_file_storage(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        UPLOAD_ENABLED=True,
        UPLOAD_PHOTO_STORAGE="thumbor.storages.mixed_storage",
        MIXED_STORAGE_FILE_STORAGE="thumbor.storages.file_storage",
    )

    assert code == 2
    assert image.exists()
    assert "--include-uploads" in capsys.readouterr().err


def test_mixed_upload_storage_without_file_storage_is_not_refused(tmp_path):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        UPLOAD_ENABLED=True,
        UPLOAD_PHOTO_STORAGE="thumbor.storages.mixed_storage",
        MIXED_STORAGE_FILE_STORAGE="thumbor.storages.no_storage",
    )

    assert code == 0
    assert not image.exists()


def test_include_uploads_allows_storage_cleanup(tmp_path):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        "--include-uploads",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        UPLOAD_ENABLED=True,
    )

    assert code == 0
    assert not image.exists()


def test_uploads_do_not_block_result_storage_cleanup(tmp_path):
    image = result_file(tmp_path, "default/ab/cd/" + "e" * 36, OLD)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        UPLOAD_ENABLED=True,
    )

    assert code == 0
    assert not image.exists()


def test_keeps_the_blacklist(tmp_path):
    config = Config(FILE_STORAGE_ROOT_PATH=str(tmp_path / "storage"))
    storage = FileStorage(Context(config=config))
    blacklist = make_file(
        Path(storage.path_on_filesystem("blacklist.txt")), OLD
    )
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert blacklist.exists()
    assert not image.exists()


def test_deletes_sidecars_with_their_expired_image(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)
    crypto = storage_file(tmp_path, IMAGE + ".txt", FRESH)
    detectors = storage_file(tmp_path, IMAGE + ".detectors.txt", FRESH)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()
    assert not crypto.exists()
    assert not detectors.exists()
    assert "sidecar: 2 files, 2 bytes" in capsys.readouterr().out


def test_keeps_old_sidecars_of_a_fresh_image(tmp_path):
    image = storage_file(tmp_path, IMAGE, FRESH)
    crypto = storage_file(tmp_path, IMAGE + ".txt", OLD)
    detectors = storage_file(tmp_path, IMAGE + ".detectors.txt", OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert image.exists()
    assert crypto.exists()
    assert detectors.exists()


def test_deletes_old_orphan_sidecars_only(tmp_path, capsys):
    old_orphan = storage_file(tmp_path, "ab/" + "1" * 38 + ".txt", OLD)
    fresh_orphan = storage_file(
        tmp_path, "ab/" + "2" * 38 + ".detectors.txt", FRESH
    )

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not old_orphan.exists()
    assert fresh_orphan.exists()
    assert "orphan sidecar: 1 files, 1 bytes" in capsys.readouterr().out


@pytest.mark.parametrize("name", [IMAGE, IMAGE + ".txt"])
def test_deletes_old_temporary_files_only(tmp_path, capsys, name):
    old_temp = storage_file(tmp_path, name + TEMP_SUFFIX, 2 * 3600)
    fresh_temp = storage_file(tmp_path, "cd/" + "d" * 38 + TEMP_SUFFIX, 600)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not old_temp.exists()
    assert fresh_temp.exists()
    assert "temporary: 1 files, 1 bytes" in capsys.readouterr().out


def test_temp_older_than_controls_temporary_files(tmp_path):
    temp = result_file(
        tmp_path, "default/ab/cd/" + "e" * 36 + TEMP_SUFFIX, 600
    )

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        "--temp-older-than",
        "300",
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not temp.exists()


@pytest.mark.parametrize(
    "settings",
    [
        {"STORAGE": "thumbor.storages.no_storage"},
        {
            "STORAGE": "thumbor.storages.mixed_storage",
            "MIXED_STORAGE_FILE_STORAGE": "thumbor.storages.no_storage",
            "MIXED_STORAGE_CRYPTO_STORAGE": "thumbor.storages.file_storage",
            "MIXED_STORAGE_DETECTOR_STORAGE": "thumbor.storages.file_storage",
        },
    ],
)
def test_keeps_orphan_keys_when_images_are_stored_elsewhere(
    tmp_path, settings
):
    key = storage_file(tmp_path, IMAGE + ".txt", OLD)
    detectors = storage_file(tmp_path, IMAGE + ".detectors.txt", OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        **settings,
    )

    assert code == 0
    assert key.exists()
    assert not detectors.exists()


@pytest.mark.parametrize(
    "name",
    [
        "README",
        "originals/2020/photo.jpg",
        "ab/photo.jpg",
        "ab/" + "c" * 38 + ".bak",
        "ab/cd/" + "c" * 38,
        "abc/" + "c" * 38,
    ],
)
def test_keeps_files_the_file_storage_did_not_write(tmp_path, name):
    foreign = storage_file(tmp_path, name, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert foreign.exists()


def test_legacy_result_names_are_not_temporary_files(tmp_path):
    name = "v2/un/sa/unsafe/example.com/logo." + "a" * 32
    cached = result_file(tmp_path, name, WITHIN_GRACE)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert cached.exists()


def test_storage_without_expiration_still_loses_temporary_files(tmp_path):
    image = storage_file(tmp_path, IMAGE, OLD)
    key = storage_file(tmp_path, "cd/" + "d" * 38 + ".txt", OLD)
    temp = storage_file(tmp_path, IMAGE + TEMP_SUFFIX, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=None,
    )

    assert code == 0
    assert image.exists()
    assert key.exists()
    assert not temp.exists()


def test_result_storage_without_expiration_still_loses_temporary_files(
    tmp_path,
):
    name = "default/ab/cd/" + "e" * 36
    image = result_file(tmp_path, name, OLD)
    temp = result_file(tmp_path, name + TEMP_SUFFIX, OLD)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        RESULT_STORAGE_EXPIRATION_SECONDS=0,
    )

    assert code == 0
    assert image.exists()
    assert not temp.exists()


def test_keeps_a_file_stored_again_after_its_directory_was_listed(tmp_path):
    images = [
        storage_file(tmp_path, "ab/" + digit * 38, OLD) for digit in "12"
    ]
    keys = [
        storage_file(tmp_path, "ab/" + digit * 38 + ".txt", OLD)
        for digit in "12"
    ]
    unlink = os.unlink
    unlinked = []

    def unlink_while_thumbor_stores(path):
        if not unlinked:
            for image in images:
                if str(image) != str(path):
                    temporary = image.with_name(image.name + TEMP_SUFFIX)
                    temporary.write_bytes(b"stored again")
                    temporary.replace(image)
        unlinked.append(path)
        unlink(path)

    with mock.patch(
        "thumbor.cleanup.os.unlink", side_effect=unlink_while_thumbor_stores
    ):
        code = run(
            tmp_path,
            "--storage",
            "--delete",
            STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        )

    assert code == 0
    kept = [image for image in images if image.exists()]
    assert [image.read_bytes() for image in kept] == [b"stored again"]
    assert [key.exists() for key in keys] == [
        image.exists() for image in images
    ]


@pytest.mark.parametrize(
    "target, root_name, linked_directory, linked_file",
    [
        ("--storage", "storage", "ef", "ab/" + "e" * 38),
        ("--result-storage", "result", "default", "v2/image.jpg"),
    ],
)
def test_does_not_follow_symlinks(
    tmp_path, target, root_name, linked_directory, linked_file
):
    outside_file = make_file(tmp_path / "outside" / "file", OLD)
    outside_dir_file = make_file(tmp_path / "outside" / "dir" / IMAGE[3:], OLD)
    root = tmp_path / root_name
    file_link = root / linked_file
    dir_link = root / linked_directory
    file_link.parent.mkdir(parents=True)
    file_link.symlink_to(outside_file)
    dir_link.symlink_to(outside_dir_file.parent, target_is_directory=True)
    old = time.time() - OLD
    os.utime(file_link, (old, old), follow_symlinks=False)

    code = run(
        tmp_path,
        target,
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert outside_file.exists()
    assert outside_dir_file.exists()
    assert file_link.is_symlink()
    assert dir_link.is_symlink()


def test_cleans_a_symlinked_root_at_its_target(tmp_path):
    target = tmp_path / "volume"
    image = make_file(target / IMAGE, OLD)
    (tmp_path / "storage").symlink_to(target, target_is_directory=True)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()
    assert (tmp_path / "storage").is_symlink()


def test_cleans_every_result_storage_layout(tmp_path, capsys):
    expired = [
        result_file(tmp_path, "default/ab/cd/" + "e" * 36, OLD),
        result_file(tmp_path, "auto_webp/ab/cd/" + "e" * 36, OLD),
        result_file(tmp_path, "v2/ab/cd/unsafe/300x200/image.jpg", OLD),
    ]
    fresh = result_file(tmp_path, "default/12/34/" + "5" * 36, FRESH)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not any(path.exists() for path in expired)
    assert fresh.exists()
    assert "expired: 3 files, 3 bytes" in capsys.readouterr().out


def test_cleans_storage_and_result_storage_together(tmp_path):
    image = storage_file(tmp_path, IMAGE, OLD)
    result = result_file(tmp_path, "default/ab/cd/" + "e" * 36, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--result-storage",
        "--delete",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()
    assert not result.exists()


def test_files_removed_by_someone_else_are_ignored(tmp_path):
    storage_file(tmp_path, IMAGE, OLD)
    storage_file(tmp_path, "cd/" + "d" * 38, OLD)

    with mock.patch(
        "thumbor.cleanup.os.unlink", side_effect=FileNotFoundError
    ) as unlink:
        code = run(
            tmp_path,
            "--storage",
            "--delete",
            STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        )

    assert code == 0
    assert unlink.call_count == 2


def test_delete_errors_set_the_exit_code_and_continue(tmp_path, capsys):
    storage_file(tmp_path, IMAGE, OLD)
    storage_file(tmp_path, "cd/" + "d" * 38, OLD)

    with mock.patch(
        "thumbor.cleanup.os.unlink",
        side_effect=PermissionError(13, "Permission denied"),
    ) as unlink:
        code = run(
            tmp_path,
            "--storage",
            "--delete",
            STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        )

    assert code == 1
    assert unlink.call_count == 2
    assert "could not delete" in capsys.readouterr().err


def test_unreadable_directories_set_the_exit_code(tmp_path, capsys):
    readable = storage_file(tmp_path, IMAGE, OLD)
    storage_file(tmp_path, "cd/" + "d" * 38, OLD)
    scandir = os.scandir

    def failing_scandir(path):
        if str(path).endswith("cd"):
            raise PermissionError(13, "Permission denied")
        return scandir(path)

    with mock.patch("thumbor.cleanup.os.scandir", side_effect=failing_scandir):
        code = run(
            tmp_path,
            "--storage",
            "--delete",
            STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        )

    assert code == 1
    assert not readable.exists()
    assert "could not read" in capsys.readouterr().err


def test_stat_errors_set_the_exit_code_and_continue(tmp_path, capsys):
    unreadable = storage_file(tmp_path, IMAGE, OLD)
    readable = storage_file(tmp_path, "cd/" + "d" * 38, OLD)
    lstat = os.lstat

    def failing_lstat(path):
        if str(path) == str(unreadable):
            raise PermissionError(13, "Permission denied")
        return lstat(path)

    with mock.patch("thumbor.cleanup.os.lstat", side_effect=failing_lstat):
        code = run(
            tmp_path,
            "--storage",
            "--delete",
            STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        )

    assert code == 1
    assert unreadable.exists()
    assert not readable.exists()
    assert "could not stat" in capsys.readouterr().err


def test_entries_that_vanish_while_listing_are_ignored(tmp_path):
    vanished_file = storage_file(tmp_path, IMAGE, OLD)
    vanished_directory = storage_file(tmp_path, "cd/" + "d" * 38, OLD)
    remaining = storage_file(tmp_path, "ef/" + "f" * 38, OLD)
    lstat = os.lstat
    scandir = os.scandir

    def vanishing_lstat(path):
        if str(path) == str(vanished_file):
            raise FileNotFoundError(2, "No such file or directory")
        return lstat(path)

    def vanishing_scandir(path):
        if str(path) == str(vanished_directory.parent):
            raise FileNotFoundError(2, "No such file or directory")
        return scandir(path)

    with (
        mock.patch("thumbor.cleanup.os.lstat", side_effect=vanishing_lstat),
        mock.patch(
            "thumbor.cleanup.os.scandir", side_effect=vanishing_scandir
        ),
    ):
        code = run(
            tmp_path,
            "--storage",
            "--delete",
            STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        )

    assert code == 0
    assert vanished_file.exists()
    assert vanished_directory.exists()
    assert not remaining.exists()


def test_missing_root_is_not_an_error(tmp_path, capsys):
    code = run(tmp_path, "--storage", STORAGE_EXPIRATION_SECONDS=EXPIRATION)

    assert code == 0
    assert "does not exist" in capsys.readouterr().out


def test_refuses_identical_roots(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
        RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=str(tmp_path / "storage"),
    )

    assert code == 2
    assert image.exists()
    assert "same directory" in capsys.readouterr().err


def test_skips_the_storage_root_nested_in_the_result_root(tmp_path):
    image = make_file(tmp_path / "cache" / "storage" / IMAGE, OLD)
    result = make_file(tmp_path / "cache" / "default" / "ab" / "cd", OLD)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        FILE_STORAGE_ROOT_PATH=str(tmp_path / "cache" / "storage"),
        RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=str(tmp_path / "cache"),
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert image.exists()
    assert not result.exists()


def test_skips_the_result_root_nested_in_the_storage_root(tmp_path):
    image = make_file(tmp_path / "data" / IMAGE, OLD)
    result = make_file(tmp_path / "data" / "cd" / ("d" * 38), OLD)

    code = run(
        tmp_path,
        "--storage",
        "--delete",
        FILE_STORAGE_ROOT_PATH=str(tmp_path / "data"),
        RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=str(tmp_path / "data" / "cd"),
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()
    assert result.exists()


def test_notes_when_the_file_modules_are_not_configured(tmp_path, capsys):
    code = run(
        tmp_path,
        "--storage",
        "--result-storage",
        STORAGE="thumbor.storages.no_storage",
    )

    assert code == 0
    out = capsys.readouterr().out
    assert "not configured to use the file storage" in out
    assert "not configured to use the file result storage" in out


def test_mixed_storage_with_file_storage_needs_no_note(tmp_path, capsys):
    code = run(
        tmp_path,
        "--storage",
        STORAGE="thumbor.storages.mixed_storage",
        MIXED_STORAGE_FILE_STORAGE="thumbor.storages.file_storage",
    )

    assert code == 0
    assert "not configured" not in capsys.readouterr().out


def test_verbose_lists_every_file(tmp_path, capsys):
    image = storage_file(tmp_path, IMAGE, OLD)

    code = run(
        tmp_path,
        "--storage",
        "--verbose",
        STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert f"expired: {image}" in capsys.readouterr().out


def test_verbose_prints_names_that_are_not_utf8(tmp_path, capsys):
    name = os.fsdecode(b"v2/\xff\xfe.jpg")
    image = result_file(tmp_path, name, OLD)

    code = run(
        tmp_path,
        "--result-storage",
        "--delete",
        "--verbose",
        RESULT_STORAGE_EXPIRATION_SECONDS=EXPIRATION,
    )

    assert code == 0
    assert not image.exists()
    out = capsys.readouterr().out
    assert "expired: " in out
    assert "\\xff\\xfe.jpg" in out


def test_invalid_expiration_is_rejected(tmp_path, capsys):
    code = run(tmp_path, "--storage", STORAGE_EXPIRATION_SECONDS="3600")

    assert code == 2
    assert "STORAGE_EXPIRATION_SECONDS" in capsys.readouterr().err


def test_missing_config_file_is_rejected(tmp_path, capsys):
    code = main(["-c", str(tmp_path / "missing.conf"), "--storage"])

    assert code == 2
    assert "missing.conf" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--delete"],
        ["--storage", "--grace", "-1"],
        ["--storage", "--older-than", "0"],
        ["--storage", "--older-than", "soon"],
        ["--storage", "--temp-older-than", "0"],
    ],
)
def test_invalid_arguments_exit_with_usage_error(arguments):
    with pytest.raises(SystemExit) as error:
        main(arguments)

    assert error.value.code == 2
