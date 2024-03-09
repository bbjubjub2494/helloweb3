#!/bin/sh
geth "$@" &
sleep 1440
kill %1
