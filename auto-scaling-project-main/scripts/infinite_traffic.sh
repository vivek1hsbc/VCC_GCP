#!/bin/bash

while true; do
  for i in {1..50}; do
    curl -s http://127.0.0.1/cpu-burn > /dev/null &
  done
  wait
  sleep 1
done
