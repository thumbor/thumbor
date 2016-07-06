run: compile_ext
	@thumbor -l debug

setup:
	@pip install -e .[tests]
	@echo
	@echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	@echo ">>>>>>>>>>>>>>> MAKE SURE GIFSICLE IS INSTALLED IF RUNNING TESTS <<<<<<<<<<<<<<"
	@echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	@echo

compile_ext:
	@python setup.py build_ext -i

test: compile_ext redis
	@$(MAKE) unit coverage
	@nosetests -sv thumbor/integration_tests/
	@$(MAKE) static
	$(MAKE) kill_redis

ci_test: compile_ext
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@echo "TORNADO IS `python -c 'import tornado; import inspect; print(inspect.getfile(tornado))'`"
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@if [ -z "$$INTEGRATION_TEST" ]; then $(MAKE) unit static coverage; else $(MAKE) integration_run; fi

integration_run:
	@nosetests -sv thumbor/integration_tests/

coverage:
	@coverage report -m --fail-under=10

unit:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/

unit-parallel:
	@`which nosetests` -v --with-yanc --processes=4 -s tests/

focus:
	@coverage run --branch `which nosetests` -vv --with-yanc --logging-level=WARNING --with-focus -i -s tests/


mysql_test: pretest
	PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py

kill_redis:
	@-redis-cli -p 6668 -a hey_you shutdown

redis: kill_redis
	@redis-server redis.conf ; sleep 1
	@redis-cli -p 6668 -a hey_you info

flake:
	@flake8 . --ignore=W801,E501

setup_docs:
	pip install -r docs/requirements.txt

build_docs:
	cd docs && make html

docs: setup_docs build_docs
	python -mwebbrowser file:///`pwd`/docs/_build/html/index.html

static:
	@flake8 --config=./flake8 .

sample_images:
	convert -delay 100 -size 100x100 gradient:blue gradient:red -loop 0 thumbor/integration_tests/imgs/animated.gif
	convert -size 100x100 gradient:blue thumbor/integration_tests/imgs/gradient.jpg
	convert -size 100x100 gradient:blue thumbor/integration_tests/imgs/gradient.gif
	convert -size 100x100 gradient:blue thumbor/integration_tests/imgs/gradient.webp
	convert -size 100x100 gradient:gray -colorspace gray thumbor/integration_tests/imgs/grayscale.jpg
	convert -size 100x100 gradient:blue -depth 16 thumbor/integration_tests/imgs/16bit.png
	convert -size 100x100 gradient:blue -colorspace CMYK thumbor/integration_tests/imgs/cmyk.jpg
	convert -size 100x100 xc:none -fill gradient:blue -draw "circle 50,50 50,1" -depth 8 thumbor/integration_tests/imgs/rgba.png
	convert -size 100x100 xc:none -fill gradient:blue -draw "circle 50,50 50,1" -interlace PNG -depth 8 thumbor/integration_tests/imgs/rgba-interlaced.png
	convert -size 16383x16383 canvas:blue tests/fixtures/images/16383x16383.png
	convert -size 16384x16384 canvas:blue tests/fixtures/images/16384x16384.png
	convert -size 9643x10328 canvas:blue tests/fixtures/images/9643x10328.jpg
	convert -size 1x1 canvas:white png24:tests/fixtures/images/1x1.png
	cp thumbor/integration_tests/imgs/animated.gif tests/fixtures/images/animated.gif
	convert -size 20x20 gradient:blue tests/fixtures/images/20x20.jpg
	echo "" > tests/fixtures/images/image_invalid.jpg
	convert -size 300x400 gradient:blue tests/fixtures/images/image.jpg
	convert -delay 100 -size 100x100 gradient:blue tests/fixtures/images/animated-one-frame.gif
	cp thumbor/integration_tests/imgs/grayscale.jpg tests/fixtures/images/grayscale.jpg
	cp thumbor/integration_tests/imgs/cmyk.jpg tests/fixtures/images/cmyk.jpg
	convert -size 100x100 gradient:blue -depth 8 tests/fixtures/images/gradient_8bit.tif
	convert -size 100x100 gradient:blue tests/fixtures/images/gradient_lsb_16bperchannel.tif
	convert -size 100x100 gradient:blue -define tiff:endian=msb tests/fixtures/images/gradient_msb_16bperchannel.tif
	curl -s https://upload.wikimedia.org/wikipedia/en/4/4a/Commons-logo.svg -o tests/fixtures/images/Commons-logo.svg
	sed 's/width="1024" height="1376"/width="10in" height="13in"/g' tests/fixtures/images/Commons-logo.svg > tests/fixtures/images/Commons-logo-inches.svg
	curl -s https://upload.wikimedia.org/wikipedia/commons/3/3e/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg -o tests/fixtures/images/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg
	convert tests/fixtures/images/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg -orient LeftBottom tests/fixtures/images/10_years_of_Wikipedia_by_Guillaume_Paumier.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/6/6d/Christophe_Henner_-_June_2016.jpg -o tests/fixtures/images/Christophe_Henner_-_June_2016.jpg
	curl -s https://upload.wikimedia.org/wikipedia/commons/3/31/Giunchedi%2C_Filippo_January_2015_01.jpg -o tests/fixtures/images/Giunchedi%2C_Filippo_January_2015_01.jpg
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
	cp tests/fixtures/images/image.jpg tests/fixtures/result_storages/v2/im/ag/image.jpg
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
	# the watermark filter's logic is too complicated to reproduce with IM, the watermark test images can't be generated here
	# similarly, the noise, colorize and fill filters generate output too unique to be reproduce with IM and can't be generated here