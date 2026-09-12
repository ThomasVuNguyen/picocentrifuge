# friday

A queue that arrives. Not a board I have to go look at.

Every Friday 9am a GitHub Action reads what changed in each project this week, drafts
the writeup, and opens a PR. I comment on the PR, the agent picks up my comments, and
I merge or close. Merge means it publishes. Close means it is dead and the slot is free.

Rules:

- one item per project per week, max. no commits that week means no draft.
- friday always sends, even when nothing happened. silence must only ever mean the job
  broke, never "quiet week", or I will stop trusting the channel.
- snooze is a normal outcome, not a failure. design for the weeks I am fried.
- deadlines must be owed to someone else. a date I set for myself is an intention.
- done means the writeup shipped, not that the experiment worked. the failure post is
  usually the better post.
- kill dates get enforced. projects die on purpose here, they do not zombie.

Each project folder has GOAL.md as its contract. Friday reads that.

## Projects

- `PicoCentrifuge/` - printed swinging-bucket centrifuge for PBMC separation
