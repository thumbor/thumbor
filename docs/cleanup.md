# Cleaning expired files

The file storage and the file result storage never delete expired files. An
expired file is ignored, and it is only replaced when the same image is
requested again, so files that are not requested anymore stay on disk forever.

`thumbor-cleanup` deletes them. Run it periodically from the same machine, or
the same volumes, as thumbor:

```bash
# Report what would be deleted
thumbor-cleanup -c /etc/thumbor.conf --result-storage

# Delete it
thumbor-cleanup -c /etc/thumbor.conf --result-storage --delete
```

Without `--delete` it only reports the files it would delete. It reads the
same configuration file as the server; when `-c` is omitted it looks for
`thumbor.conf` the same way the server does. Environment overrides
(`--use-environment`) are not supported, so read environment variables inside
the configuration file as described in {ref}`converting-environment-values`.

## Options

- `-c`, `--conf`: the thumbor configuration file.
- `--storage`: clean `FILE_STORAGE_ROOT_PATH` using
  `STORAGE_EXPIRATION_SECONDS`.
- `--result-storage`: clean `RESULT_STORAGE_FILE_STORAGE_ROOT_PATH` using
  `RESULT_STORAGE_EXPIRATION_SECONDS`.
- `--delete`: delete the files instead of only reporting them.
- `--include-uploads`: allow `--storage` when uploads are stored in the file
  storage. See below.
- `--older-than SECONDS`: use this age instead of the configured expiration.
- `--grace SECONDS`: extra age added to the expiration before a file is
  deleted. Defaults to 3600.
- `--temp-older-than SECONDS`: age after which leftover temporary files are
  deleted. Defaults to 3600.
- `-v`, `--verbose`: print every file that is deleted or would be deleted.

At least one of `--storage` and `--result-storage` is required. The command
exits with 0 on success, 1 when a file or directory could not be read or
deleted, and 2 for invalid arguments or a configuration it refuses to clean.

## What is deleted

A file is deleted when it is older than the expiration plus the grace period.
thumbor already treats such a file as expired and does not read it, so the
grace period keeps the command from removing a file that a running server has
just checked and is about to read. The file storage and the file result
storage also treat a file that disappears while they read it as missing, so a
request that races the command (for example with an `--older-than` shorter
than the configured expiration) gets a cache miss instead of an error.

When the expiration is `None`, zero or negative, nothing is deleted from that
root unless `--older-than` is given. Note that thumbor itself treats a
`STORAGE_EXPIRATION_SECONDS` of zero as "every file is expired", while
`RESULT_STORAGE_EXPIRATION_SECONDS` of zero means "never expires"; the cleanup
command never reads a zero as a reason to delete everything.

In the storage root, the security key (`.txt`) and detector
(`.detectors.txt`) files of an image are deleted together with it, and those
whose image no longer exists are deleted once they are old enough on their
own. The blacklist file is never deleted, since it is configuration, not
cache. In both roots, temporary files left behind by an interrupted write are
deleted after `--temp-older-than` seconds.

The command does not follow symbolic links found inside a root, only deletes
regular files, never leaves the configured root and keeps every directory. A
root that is itself a symbolic link is cleaned at its target, which is where
thumbor reads and writes those files. When one root is inside the other,
cleaning the outer one skips the inner one. Files that disappear while it runs
are ignored.

## Uploaded images

When `UPLOAD_ENABLED` is on and `UPLOAD_PHOTO_STORAGE` is
`thumbor.storages.file_storage`, or `thumbor.storages.mixed_storage` with
`MIXED_STORAGE_FILE_STORAGE` set to the file storage, uploaded images live in
`FILE_STORAGE_ROOT_PATH` next to the cached original images and expire with
the same `STORAGE_EXPIRATION_SECONDS`. They cannot be told apart on disk, so
`--storage` refuses to run unless `--include-uploads` is given. With it, every
uploaded image older than the expiration is deleted for good. Raise
`STORAGE_EXPIRATION_SECONDS` or leave the storage root alone if uploads must
be kept.

## Scheduling

With cron, for example in `/etc/cron.d/thumbor-cleanup`:

```text
17 3 * * * thumbor thumbor-cleanup -c /etc/thumbor.conf --result-storage --delete
```

With a systemd timer, `/etc/systemd/system/thumbor-cleanup.service`:

```ini
[Unit]
Description=Delete expired thumbor files

[Service]
Type=oneshot
User=thumbor
ExecStart=/usr/local/bin/thumbor-cleanup -c /etc/thumbor.conf --result-storage --delete
```

and `/etc/systemd/system/thumbor-cleanup.timer`:

```ini
[Unit]
Description=Run thumbor-cleanup daily

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

Then enable it with `systemctl enable --now thumbor-cleanup.timer`.

With a Kubernetes CronJob that mounts the same configuration and volume as the
thumbor deployment:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: thumbor-cleanup
spec:
  schedule: "17 3 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: thumbor-cleanup
              image: ghcr.io/thumbor/thumbor:latest
              command:
                - thumbor-cleanup
                - -c
                - /etc/thumbor.conf
                - --result-storage
                - --delete
              volumeMounts:
                - name: config
                  mountPath: /etc/thumbor.conf
                  subPath: thumbor.conf
                - name: result-storage
                  mountPath: /data/result_storage
          volumes:
            - name: config
              configMap:
                name: thumbor-config
            - name: result-storage
              persistentVolumeClaim:
                claimName: thumbor-result-storage
```

## Without thumbor-cleanup

The result storage holds nothing but generated images, so `find` is enough
there. For a one day expiration plus one hour of grace (1500 minutes):

```bash
find /data/result_storage -type f -mmin +1500 -delete
```

Do not use this on the storage root: it also holds uploads, security key and
detector files, and the blacklist.
