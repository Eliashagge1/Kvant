#!/bin/sh
set -eu
kvant-init
uvicorn kvant_console.api:app --host 127.0.0.1 --port 8765
