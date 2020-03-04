#!/bin/bash
if [[ $PERF_TEST -eq 1 ]]
	then
			k6 login cloud -t $K6_API_KEY
			k6 run -o cloud -e P95=8000 -e DURATION=300 -q test_image_transform.js
	else
		if [[ "$K6_API_KEY" -ne "" ]]
		then
				k6 run -o cloud test_image_transform.js
		else
				k6 run test_image_transform.js
		fi
fi
EXITCODE=$?
start-stop-daemon -q --stop --oknodo --remove-pidfile --pidfile /tmp/thumbor-perf.pid > /dev/null 2>&1
exit $EXITCODE
