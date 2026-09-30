# telegram

Talk to a Gas City from Telegram. The adapter long-polls the bot, registers
on the city's external-messaging API, and delivers agent publishes back into
the chat that asked. Project rosters, desks, and approvals ride in the same
process.

The layout follows `slack-mini` in [gascity-packs](https://github.com/gastownhall/gascity-packs):
one `proxy_process` service, a health check at `/healthz`, and an outbound
command that posts through gc's `/svc/telegram` proxy so the bot token never
has to sit in the command's environment.

## What runs

| Piece | Role |
| --- | --- |
| `adapter/bridge.py` | The service. Polls Telegram, serves `/publish`, `/healthz`, and `/post-message`. |
| `adapter/factory_router.py` | Project desks. A person speaks in a topic while an agent is waiting on them. |
| `adapter/factory.py` | Intake client for `POST /projects`. |
| `scripts/reply.sh` | What a session runs to publish into its rig's conversation. |
| `adapter/telegram_bot.py` | The earlier single-bot client. The service does not start it. |

`github_delivery.py` and `weaver_client.py` stay beside the bridge because the
router calls them when a project is published or linked. Both stay idle until
their environment variables are set.

## Install

From the city directory:

```toml
[imports.telegram]
source = "../packs/telegram"
```

Install the adapter's libraries once, next to the interpreter gc will use:

```sh
python3 -m pip install -r adapter/requirements.txt
```

The service environment is the same set the host bridge used. Names only:

| Variable | Required | Purpose |
| --- | :---: | --- |
| `GC_API` | yes | City HTTP base, on this host `http://127.0.0.1:8372`. |
| `GC_CITY_NAME` | yes | City the adapter registers with. |
| `BRIDGE_CALLBACK_URL` | yes | URL Gas City will POST publishes to. Must reach `/publish`. |
| `CONFIG_PATH` | yes | `responsibilities.json`. Each user names `bot_token_env`. |
| `TELEGRAM_BOT_TOKEN` and any other token env the roster names | yes | Bot tokens. One `getUpdates` poll per distinct token. |
| `BRIDGE_PORT` | | TCP listen port. Default `8081`. |
| `GC_ACCOUNT_ID` | | Default `factory`. |
| `GC_CONVERSATION_ID` | | Default `landing-page`, for the city landing conversation. |
| `PROJECT_STATE_DIR` | | Turns on factory desks. Unset keeps the landing-page channel only. |
| `FACTORY_PROJECTS_DIR` | | Where a delivery reads the project checkout. |
| `GITHUB_TOKEN` | | Delivery. Unset, and a delivery says so instead of pushing. |
| `WEAVER_BASE_URL`, `WEAVER_API_KEY` | | Weaver link. Both unset leaves that link off. |
| `PAGE_URL` | | Shown with a landing-page approval. |

gc sets `GC_SERVICE_SOCKET` when it supervises the service. The adapter then
serves `/healthz` and `/post-message` on that socket and keeps the TCP port
open for `/publish`.

## Commands

```sh
gc telegram post-message --user alex --chat-id 123456 --text "build is green"
printf 'APPROVAL_NEEDED: requirements\nShip it?\n' | gc telegram reply
```

`reply` has to run inside a session. It rebinds the rig's conversation to
that session, then publishes. The bridge routes the tagged lines.

## What this pack does not contain

Bot tokens, `bridge.env`, and the live `responsibilities.json` stay on the
host that runs the city. This directory is the code that used to live only
in `/opt/gascity/bot` and `factory/scripts/reply.sh`.
