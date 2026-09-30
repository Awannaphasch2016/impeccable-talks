#!/bin/sh
# gc telegram post-message — post plain text through the supervised adapter.
#
# The adapter holds the bot token. This wrapper only relays JSON to
# /svc/telegram/post-message, the same split slack-mini uses for Slack.
set -eu

user=""
text=""
chat_id=""
thread_id=""

require_value() {
  if [ "$2" -lt 2 ]; then
    echo "gc telegram post-message: $1 requires a value" >&2
    exit 2
  fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    --user)       require_value "$1" "$#"; user="$2"; shift 2 ;;
    --text)       require_value "$1" "$#"; text="$2"; shift 2 ;;
    --chat-id)    require_value "$1" "$#"; chat_id="$2"; shift 2 ;;
    --thread-id)  require_value "$1" "$#"; thread_id="$2"; shift 2 ;;
    --user=*)      user="${1#*=}"; shift ;;
    --text=*)      text="${1#*=}"; shift ;;
    --chat-id=*)   chat_id="${1#*=}"; shift ;;
    --thread-id=*) thread_id="${1#*=}"; shift ;;
    -h|--help)
      cat "$(dirname "$0")/post-message/help.md"
      exit 0
      ;;
    *)
      echo "gc telegram post-message: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ -z "$user" ] || [ -z "$text" ] || [ -z "$chat_id" ]; then
  echo "gc telegram post-message: --user, --chat-id, and --text are required" >&2
  exit 2
fi

api_base="${GC_API:-${GC_API_BASE_URL:-http://127.0.0.1:8372}}"
api_base="${api_base%/}"
city="${GC_CITY_NAME:-}"
if [ -z "$city" ]; then
  echo "gc telegram post-message: GC_CITY_NAME is not set" >&2
  exit 1
fi

url="${TELEGRAM_ADAPTER_URL:-${api_base}/v0/city/${city}/svc/telegram/post-message}"

body=$(USER_NAME="$user" CHAT_ID="$chat_id" TEXT="$text" THREAD_ID="$thread_id" python3 -c '
import json, os
payload = {
    "user": os.environ["USER_NAME"],
    "chat_id": int(os.environ["CHAT_ID"]),
    "text": os.environ["TEXT"],
}
thread = os.environ.get("THREAD_ID", "")
if thread:
    payload["thread_id"] = int(thread)
print(json.dumps(payload))
')

response=$(curl -sS -X POST "$url" \
  -H 'Content-Type: application/json' \
  -H 'X-GC-Request: gc-telegram' \
  --data-binary "$body" \
  -w $'\n%{http_code}') || {
  echo "gc telegram post-message: request to $url failed" >&2
  exit 1
}

status=$(printf '%s\n' "$response" | tail -n 1)
payload=$(printf '%s\n' "$response" | sed '$d')
printf '%s\n' "$payload"
case "$status" in
  2*) exit 0 ;;
  *) exit 1 ;;
esac
