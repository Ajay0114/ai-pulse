#!/usr/bin/env bash
# Entry point for the scheduled daily run: incremental RSS ingestion,
# then classification and enrichment of whatever is newly pending.
# Intended to be invoked once a day (e.g. from Windows Task Scheduler
# via wsl.exe) rather than run manually.
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate

mkdir -p logs
LOG_FILE="logs/daily_pipeline_$(TZ='Asia/Kolkata' date +%Y%m%d_%H%M%S)_IST.log"

python -m app.pipeline.daily_pipeline >> "$LOG_FILE" 2>&1
