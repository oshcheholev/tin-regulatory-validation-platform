#!/bin/bash
killall celery
kill -9 $(pgrep -f celery)
echo "Killed"
