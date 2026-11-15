#!/bin/bash
# OMF health probe: API-level checks, not process liveness (ghost-bind lesson).
ok=1
curl -sf --max-time 5 http://127.0.0.1:11499/api/version >/dev/null || { echo "omf-health: scratch :11499 NOT answering"; ok=0; }
curl -sf --max-time 5 http://127.0.0.1:11500/omf/health >/dev/null || { echo "omf-health: layer :11500 NOT answering"; ok=0; }
[ $ok -eq 1 ] && echo "omf-health: OK scratch+layer answering" || exit 1
