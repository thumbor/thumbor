# Logging

thumbor uses Python's built-in logging system. The `-l` or `--log-level`
command-line option selects the level; see {doc}`running`.

## Logging configuration

Logging settings live in `thumbor.conf` like other configuration keys.

### THUMBOR_LOG_CONFIG

A Python dictionary accepted by `logging.config.dictConfig`. When this setting
is not `None` or an empty string, thumbor applies it and does not call
`logging.basicConfig`; `THUMBOR_LOG_FORMAT`, `THUMBOR_LOG_DATE_FORMAT` and the
command-line log level therefore do not configure the handlers created by this
dictionary.

```python
THUMBOR_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    # Add formatters, handlers, loggers and root here.
}
```

The default is `None`.

### THUMBOR_LOG_FORMAT

Format used when `THUMBOR_LOG_CONFIG` is not set.

```python
THUMBOR_LOG_FORMAT = '%(asctime)s %(name)s:%(levelname)s %(message)s'
```

### THUMBOR_LOG_DATE_FORMAT

Date format used when `THUMBOR_LOG_CONFIG` is not set.

```python
THUMBOR_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
```
