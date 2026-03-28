#!/bin/bash
for i in {1..50}; do
  curl http://127.0.0.1/cpu-burn &
done
wait
echo "Traffic generation complete"
