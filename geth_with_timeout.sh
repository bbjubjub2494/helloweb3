#!/bin/sh
geth "$@" &
sleep 1440
kill $!
