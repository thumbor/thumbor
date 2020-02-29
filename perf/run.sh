#!/bin/bash
if [[ $PERF_TEST -eq 1 ]]
		then
				k6 run -e P95=8000 -e DURATION=240 -q test_image_transform.js
		else
				k6 run test_image_transform.js
fi
EXITCODE=$?
start-stop-daemon -q --stop --oknodo --remove-pidfile --pidfile /tmp/thumbor-perf.pid > /dev/null 2>&1
exit $EXITCODE
