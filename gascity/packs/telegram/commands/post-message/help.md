# gc telegram post-message

Send one message as a roster user's bot. The adapter holds the bot token.

```sh
gc telegram post-message --user alex --chat-id 123456 --text "build is green"
gc telegram post-message --user alex --chat-id -100123 --thread-id 42 --text "in the topic"
```

`--user` is the name in responsibilities.json. `--chat-id` is the Telegram chat.
`--thread-id` is a forum topic, and is optional.
