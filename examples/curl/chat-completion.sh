#!/usr/bin/env bash
set -euo pipefail

: "${OPENAI_API_KEY:?Set OPENAI_API_KEY first}"
BASE_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
MODEL="${OPENAI_MODEL:?Set OPENAI_MODEL to a model shown by your endpoint}"

curl --fail-with-body "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(MODEL="$MODEL" python -c 'import json, os; print(json.dumps({"model": os.environ["MODEL"], "messages": [{"role": "user", "content": "Reply with one short sentence: what is a token?"}]}))')"
