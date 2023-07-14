#!/bin/bash

cd calculations

python3 manage_runs.py &>> ./iterboltz-container/calculations/run.logs
