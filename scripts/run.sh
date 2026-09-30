#!/bin/sh
set -e
dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ -f "$dir/.env" ]; then
	set -a
	. "$dir/.env"
	set +a
fi
exec python3 "$dir/scripts/new-visitor-notify.py"
