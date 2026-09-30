# gc telegram reply

Publish the message on stdin into the rig's conversation. Run this inside a
gc session. The bridge fans QUESTIONS and APPROVAL_NEEDED lines out to the
roster.

```sh
printf 'QUESTIONS: requirements\n1. Who signs off?\n' | gc telegram reply
```
