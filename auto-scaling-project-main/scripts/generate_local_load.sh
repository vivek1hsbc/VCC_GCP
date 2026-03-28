#!/bin/bash
for i in {1..20}; do
  curl http://127.0.0.1:5000/cpu-burn &
done
wait
echo "Local load generation complete"
