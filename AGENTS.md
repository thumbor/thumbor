# AGENTS.md

thumbor is a smart imaging HTTP service built with Python/Tornado. It resizes,
crops, and applies filters to images on demand via URL parameters. The image
processing pipeline is pluggable: loaders, storages, engines, detectors, and
filters are all swappable.

## Dev environment setup

- **Prerequisites:** Python 3.9+, Redis, a C compiler (for native extensions)
- Install all dependencies (creates an editable install with test extras):

  ```
  make setup
  ```

  Equivalent to: `pip install -e .[tests]`

- Install pre-commit hooks (run once after setup):

  ```
  pre-commit install
  ```

- Compile C extensions (required before running the server or tests locally):

  ```
  make compile_ext
  ```

## Running the server

```
make run        # debug mode: thumbor -l debug -d -c thumbor/thumbor.conf
make run-prod   # production mode: thumbor -l error -c thumbor/thumbor.conf
```

Other CLI entry points registered by the package:

- `thumbor-url` — compose and sign URLs
- `thumbor-config` — generate a config file
- `thumbor-doctor` — diagnose the local installation

## Running tests

- Full suite (builds extensions, starts Redis, runs unit + integration + lint,
  stops Redis):

  ```
  make test
  ```

- Unit tests only (parallel, uses all CPUs):

  ```
  make unit
  ```

- Integration tests only:

  ```
  make integration_run
  ```

- Coverage report:

  ```
  make coverage
  ```

- Tests require a local Redis on port **6668** (sentinel on **26379**, password
  `hey_you`). Start it with:

  ```
  make redis
  ```

  If you hit "Too many open files", run `ulimit -S -n 2048` first.

- In CI, everything runs inside Docker across a Python 3.10–3.13 matrix via
  GitHub Actions.

## Code style

- **Formatter:** `black` (line length 79, target Python 3.10). Run with `make format`.
- **Linter:** `flake8` (max complexity 20). Run with `make flake`.
- **Imports:** `isort` (multi-line style 3, compatible with black).
- **Static analysis:** `pylint`. Run with `make pylint`.
- **Type checking:** `mypy` (strict: `disallow_untyped_defs`,
  `warn_return_any`). Config in `mypy.ini`.
- Pre-commit enforces all of the above plus trailing whitespace, end-of-file
  newlines, and YAML validity.
- CI runs `black --check`, `flake8`, and `isort` as separate jobs on every push/PR.

## Project structure

```
thumbor/              ← main Python package
  app.py              ← Tornado application
  server.py           ← CLI entry point
  config.py           ← all configuration knobs
  transformer.py      ← image transformation pipeline
  handlers/           ← HTTP handlers (imaging, upload, healthcheck)
  engines/            ← image processing engines (Pillow, GIF, JSON)
  filters/            ← built-in filters (blur, brightness, watermark…)
  detectors/          ← face/feature detectors (OpenCV Haar cascades)
  loaders/            ← image source loaders (http, file, strict)
  storages/           ← image storages (file, mixed, no-op)
  result_storages/    ← result caching
  url_signers/        ← HMAC URL signing
  ext/filters/        ← C extension modules for performance-critical filters
tests/                ← unit tests (pytest + pytest-xdist)
integration_tests/    ← integration tests
docs/                 ← Sphinx documentation
docker/               ← Docker files
.github/workflows/    ← CI: build, lint, release, CodeQL, dependabot
Makefile              ← primary task runner (use this for all common tasks)
```

## Contribution guidelines

- Bug fixes for the v6 stable branch go to `fixes/6.7.x`; new features go to `master`.
- Merge `master` into your branch before opening a PR.
- Every change must include tests. Run `make unit` to verify.
- Run `make flake pylint` before committing (or rely on the pre-commit hooks).
- Do not add a `thumbor.key` file with real secrets; the repo-root `thumbor.key`
  is for development only.

## Security considerations

- **`SECURITY_KEY`** defaults to `"MY_SECURE_KEY"`. Always override this in production.
- **`ALLOW_UNSAFE_URL`** defaults to `True` (bypasses URL signing). Set to
  `False` in production.
- **`ALLOWED_SOURCES`** defaults to `[]` (all sources allowed). Restrict to
  known domains in production using regex patterns.
- **`MAX_PIXELS`** defaults to 75 megapixels; keep it set to guard against
  decompression bombs.
- CodeQL scans Python and C/C++ code on every push to `master` and weekly via
  GitHub Actions.
