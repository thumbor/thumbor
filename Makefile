PYTHON ?= python3
UV_VERSION ?= 0.11.19
UV_BOOTSTRAP_DIR ?= .uv-venv
UV = $(shell command -v uv 2>/dev/null || printf '%s' "$(UV_BOOTSTRAP_DIR)/bin/uv")
UV_RUN = $(UV) run --locked
UV_RUN_DEV = $(UV_RUN) --extra tests
UV_RUN_TESTS = $(UV_RUN_DEV) --extra all

.PHONY: \
	bootstrap-uv build build_docs ci_test compile_ext coverage docs flake \
	format isort integration integration_run int lcov pint pintegration \
	pre-commit publish pylint run run-prod sequential-unit setup setup-ci \
	setup_docs test unit

OS := $(shell uname)

run: compile_ext
	@$(UV_RUN) --extra all thumbor -l debug -d -c thumbor/thumbor.conf

run-prod: compile_ext
	@$(UV_RUN) --extra all thumbor -l error -c thumbor/thumbor.conf

bootstrap-uv:
	@if ! "$(UV)" --version >/dev/null 2>&1; then \
		echo "Installing uv $(UV_VERSION) into $(UV_BOOTSTRAP_DIR)"; \
		$(PYTHON) -m pip install --disable-pip-version-check --upgrade \
			--target "$(UV_BOOTSTRAP_DIR)" "uv==$(UV_VERSION)"; \
	fi

setup: bootstrap-uv
	@$(UV) sync --locked --extra tests --extra all
	@echo  "\n\nYou are strongly recommended to run 'make pre-commit'\n"

setup-ci:
	@$(UV) sync --locked --extra tests --extra all

compile_ext build:
	@$(UV) run --locked --group build python setup.py build_ext -i

pre-commit:
	@$(UV) run --locked --extra tests pre-commit install

test: build redis
	@$(MAKE) unit coverage
	@$(MAKE) integration_run
	@$(MAKE) flake
	@$(MAKE) kill_redis

ci_test: build
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@echo "TORNADO IS `$(UV_RUN_TESTS) python -c 'import tornado; import inspect; print(inspect.getfile(tornado))'`"
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; elif [ -z "$$INTEGRATION_TEST" ]; then $(MAKE) unit coverage; else $(MAKE) integration_run; fi

integration_run integration int:
	@$(UV_RUN_TESTS) pytest -sv integration_tests/ -p no:tldr

pint pintegration:
	@$(UV_RUN_TESTS) pytest -sv integration_tests/ -p no:tldr -n auto

coverage:
	@$(UV_RUN_TESTS) coverage report -m --fail-under=10

lcov:
	@$(UV_RUN_TESTS) coverage lcov

unit:
	@$(UV_RUN_TESTS) pytest -n auto --cov=thumbor tests/

sequential-unit:
	@$(UV_RUN_TESTS) pytest -sv --junit-xml=test-results/unit/results.xml --cov=thumbor tests/

kill_redis:
	@-redis-cli -p 6668 -a hey_you shutdown
	@-redis-cli -p 26379 -a hey_you shutdown
	@-rm /tmp/redis-sentinel.conf 2>/dev/null

redis: kill_redis
	@cp redis-sentinel.conf /tmp/redis-sentinel.conf
	@redis-server redis.conf ; sleep 1
	@redis-server /tmp/redis-sentinel.conf --sentinel ; sleep 1
	@redis-cli -p 6668 -a hey_you info

format:
	@$(UV_RUN_DEV) isort --profile black thumbor tests integration_tests setup.py
	@$(UV_RUN_DEV) black .

flake:
	@$(UV_RUN_DEV) flake8 --config .flake8 thumbor tests integration_tests setup.py

isort:
	@$(UV_RUN_DEV) isort --profile black --check-only --diff thumbor tests integration_tests setup.py

pylint: compile_ext
	@$(UV_RUN_TESTS) pylint --load-plugins=pylint.extensions.no_self_use thumbor tests

setup_docs:
	@$(UV) sync --locked --inexact --group docs

build_docs:
	@$(UV) run --locked --group docs make -C docs html

docs:
	@$(UV) run --locked --group docs sphinx-reload --host 0.0.0.0 --port 5555 docs/

sample_images:
	convert -delay 100 -size 100x100 gradient:blue gradient:red -loop 0 integration_tests/imgs/animated.gif
	convert -size 100x100 gradient:blue integration_tests/imgs/gradient.jpg
	convert -size 100x100 gradient:blue integration_tests/imgs/gradient.gif
	convert -size 100x100 gradient:blue integration_tests/imgs/gradient.webp
	convert -size 100x100 gradient:gray -colorspace gray integration_tests/imgs/grayscale.jpg
	convert -size 100x100 gradient:blue -depth 16 integration_tests/imgs/16bit.png
	convert -size 100x100 gradient:blue -colorspace CMYK integration_tests/imgs/cmyk.jpg
	convert -size 100x100 xc:none -fill gradient:blue -draw "circle 50,50 50,1" -depth 8 integration_tests/imgs/rgba.png
	convert -size 100x100 xc:none -fill gradient:blue -draw "circle 50,50 50,1" -interlace PNG -depth 8 integration_tests/imgs/rgba-interlaced.png
	convert -size 16383x16383 canvas:blue tests/fixtures/images/16383x16383.png
	convert -size 16384x16384 canvas:blue tests/fixtures/images/16384x16384.png
	convert -size 9643x10328 canvas:blue tests/fixtures/images/9643x10328.jpg
	convert -size 1x1 canvas:white png24:tests/fixtures/images/1x1.png
	cp integration_tests/imgs/animated.gif tests/fixtures/images/animated.gif
	convert -size 20x20 gradient:blue tests/fixtures/images/20x20.jpg
	echo "" > tests/fixtures/images/image_invalid.jpg
	convert -size 300x400 gradient:blue tests/fixtures/images/image.jpg
	convert -delay 100 -size 100x100 gradient:blue tests/fixtures/images/animated-one-frame.gif
	cp integration_tests/imgs/grayscale.jpg tests/fixtures/images/grayscale.jpg
	cp integration_tests/imgs/cmyk.jpg tests/fixtures/images/cmyk.jpg
	convert -size 100x100 gradient:blue -depth 8 tests/fixtures/images/gradient_8bit.tif
	convert -size 100x100 gradient:blue tests/fixtures/images/gradient_lsb_16bperchannel.tif
	convert -size 100x100 gradient:blue -define tiff:endian=msb tests/fixtures/images/gradient_msb_16bperchannel.tif
	curl -s https://upload.wikimedia.org/wikipedia/en/4/4a/Commons-logo.svg -o tests/fixtures/images/Commons-logo.svg
	sed 's/width="1024" height="1376"/width="10in" height="13in"/g' tests/fixtures/images/Commons-logo.svg > tests/fixtures/images/Commons-logo-inches.svg
	curl -s https://upload.wikimedia.org/wikipedia/commons/3/3e/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg -o tests/fixtures/images/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg
	convert tests/fixtures/images/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg -orient LeftBottom tests/fixtures/images/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/6/6d/Christophe_Henner_-_June_2016.jpg -o tests/fixtures/images/Christophe_Henner_-_June_2016.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/3/31/Giunchedi%2C_Filippo_January_2015_01.jpg -o tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif -o tests/fixtures/images/Rotating_earth_\(large\).gif
	convert tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg -colorspace CMYK tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01-cmyk.jpg
	convert tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.png
	convert tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg -colorspace gray tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01-grayscale.jpg
	convert tests/fixtures/images/image.jpg -define jpeg:q-table=tests/fixtures/images/qtables.xml tests/fixtures/images/invalid_quantization.jpg
	convert tests/fixtures/images/image.jpg tests/fixtures/images/image.webp
	convert logo: tests/fixtures/images/no_face.jpg
	cp tests/fixtures/images/image.jpg tests/fixtures/images/image.jpg%3Fts%3D1
	cp tests/fixtures/images/image.jpg tests/fixtures/images/image
	cp tests/fixtures/images/image.jpg tests/fixtures/images/image.jpg%23something
	cp tests/fixtures/images/image.jpg tests/fixtures/images/image%20space.jpg
	cp tests/fixtures/images/image.jpg tests/fixtures/images/15967251_212831_19242645_%D0%90%D0%B3%D0%B0%D1%82%D0%B0%D0%B2%D0%97%D0%BE%D0%BE%D0%BF%D0%B0%D1%80%D0%BA%D0%B5.jpg
	cp tests/fixtures/images/image.jpg tests/fixtures/images/15967251_212831_19242645_АгатавЗоопарке.jpg
	cp tests/fixtures/images/image.jpg tests/fixtures/images/maracujá.jpg
	cp tests/fixtures/images/image.jpg tests/fixtures/images/alabama1_ap620%C3%A9.jpg
	cp tests/fixtures/images/image.jpg tests/fixtures/images/alabama1_ap620é.jpg
	mkdir -p tests/fixtures/result_storages/v2/im/ag/
	cp tests/fixtures/images/image.jpg tests/fixtures/result_storages/v2/im/ag/image.jpg
	mkdir -p tests/fixtures/filters
	curl -s https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Katherine_Maher.jpg/800px-Katherine_Maher.jpg -o tests/fixtures/filters/source.jpg
	convert tests/fixtures/filters/source.jpg -quality 10 tests/fixtures/filters/quality-10%.jpg
	convert tests/fixtures/filters/source.jpg -rotate 180 tests/fixtures/filters/rotate.jpg
	convert tests/fixtures/filters/source.jpg -blur 4x2 tests/fixtures/filters/blur.jpg
	convert tests/fixtures/filters/source.jpg -blur 8x8 tests/fixtures/filters/blur2.jpg
	convert tests/fixtures/filters/source.jpg -blur 150x150 tests/fixtures/filters/blur3.jpg
	convert tests/fixtures/filters/source.jpg -brightness-contrast 20x0 tests/fixtures/filters/brightness.jpg
	convert tests/fixtures/filters/source.jpg -brightness-contrast 0x20 tests/fixtures/filters/contrast.jpg
	convert tests/fixtures/filters/source.jpg -gamma 1.1,1.02,1.04 tests/fixtures/filters/rgb.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/8/81/Wikimedia-logo.svg -o tests/fixtures/filters/watermark.svg
	convert tests/fixtures/filters/watermark.svg -transparent white -resize 30x30 tests/fixtures/filters/watermark.png
	curl -s https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Guido-portrait-2014.jpg/800px-Guido-portrait-2014.jpg -o tests/fixtures/filters/800px-Guido-portrait-2014.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Christophe_Henner_-_June_2016.jpg/800px-Christophe_Henner_-_June_2016.jpg -o tests/fixtures/filters/800px-Christophe_Henner_-_June_2016.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/archive/4/47/20161122122708%21PNG_transparency_demonstration_1.png | convert - -resize 300x225 tests/fixtures/filters/PNG_transparency_demonstration_1.png
	convert tests/fixtures/filters/PNG_transparency_demonstration_1.png -background blue -flatten tests/fixtures/filters/PNG_transparency_demonstration_1_blue.png
	convert tests/fixtures/filters/PNG_transparency_demonstration_1.png -dither None -colors 256 tests/fixtures/images/paletted-transparent.png
	cp tests/fixtures/filters/source.jpg tests/fixtures/filters/800px-Katherine_Maher.jpg
	cp tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg tests/fixtures/filters/Giunchedi%2C_Filippo_January_2015_01.jpg
	cp tests/fixtures/filters/watermark.png tests/fixtures/images/watermark.png
	# the watermark filter's logic is too complicated to reproduce with IM, the watermark test images can't be generated here
	# similarly, the noise, colorize, redeye and fill filters generate output too unique to be reproduce with IM and can't be generated here

test-docker-build: test-docker-310-build test-docker-311-build test-docker-312-build test-docker-313-build test-docker-314-build

test-docker-run: test-docker-310-run test-docker-311-run test-docker-312-run test-docker-313-run test-docker-314-run

test-docker-publish: test-docker-310-publish test-docker-311-publish test-docker-312-publish test-docker-313-publish test-docker-314-publish

test-docker-310-build:
	@docker build -f TestDockerfile --build-arg PYTHON_VERSION=3.10 -t thumbor-test-310 .

test-docker-310-run: test-docker-310-build
	@docker run --rm -v "$$(pwd):/app" thumbor-test-310 make setup-ci compile_ext redis sequential-unit integration flake

test-docker-310-publish:
	@docker image tag thumbor-test-310:latest thumbororg/thumbor-test:310
	@docker push thumbororg/thumbor-test:310

test-docker-311-build:
	@docker build -f TestDockerfile --build-arg PYTHON_VERSION=3.11 -t thumbor-test-311 .

test-docker-311-run: test-docker-311-build
	@docker run --rm -v "$$(pwd):/app" thumbor-test-311 make setup-ci compile_ext redis sequential-unit integration flake

test-docker-311-publish:
	@docker image tag thumbor-test-311:latest thumbororg/thumbor-test:311
	@docker push thumbororg/thumbor-test:311

test-docker-312-build:
	@docker build -f TestDockerfile --build-arg PYTHON_VERSION=3.12 -t thumbor-test-312 .

test-docker-312-run: test-docker-312-build
	@docker run --rm -v "$$(pwd):/app" thumbor-test-312 make setup-ci compile_ext redis sequential-unit integration flake

test-docker-312-publish:
	@docker image tag thumbor-test-312:latest thumbororg/thumbor-test:312
	@docker push thumbororg/thumbor-test:312

test-docker-313-build:
	@docker build -f TestDockerfile --build-arg PYTHON_VERSION=3.13 -t thumbor-test-313 .

test-docker-313-run: test-docker-313-build
	@docker run --rm -v "$$(pwd):/app" thumbor-test-313 make setup-ci compile_ext redis sequential-unit integration flake

test-docker-313-publish:
	@docker image tag thumbor-test-313:latest thumbororg/thumbor-test:313
	@docker push thumbororg/thumbor-test:313

test-docker-314-build:
	@docker build -f TestDockerfile --build-arg PYTHON_VERSION=3.14 -t thumbor-test-314 .

test-docker-314-run: test-docker-314-build
	@docker run --rm -v "$$(pwd):/app" thumbor-test-314 make setup-ci compile_ext redis sequential-unit integration flake

test-docker-314-publish:
	@docker image tag thumbor-test-314:latest thumbororg/thumbor-test:314
	@docker push thumbororg/thumbor-test:314

publish:
	@$(UV_RUN) --only-group release --only-group build python -m build --sdist --no-isolation
	@$(UV_RUN) --only-group release python -m twine upload dist/*
	@rm -rf dist/
