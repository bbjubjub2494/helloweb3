#!/bin/sh
command "$@" &
sleep $TIMEOUT
kill $!
