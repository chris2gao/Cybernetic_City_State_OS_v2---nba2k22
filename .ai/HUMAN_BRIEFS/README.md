# Human Brief Archive

This directory stores optional archived human-facing briefs.

## Policy

- `.ai/HUMAN_BRIEF.md` is the latest human-facing brief.
- `.ai/HUMAN_BRIEFS/*.md` is for durable archived briefs.
- Archive only material human events: conflict, blocked state, permission escalation, source-branch publication, major phase transition, safety/privacy risk, model disagreement, or stage completion.
- Normal handoff turns should update only `.ai/HUMAN_BRIEF.md` and include `brief_ref` in the pointer message.
- Model-to-model chat should not paste the full brief unless the human explicitly asks.
- ChatGPT may place a compact Codex execution recommendation in human-facing chat when advising the Human to start a task; GitHub Human Briefs are not required to carry that recommendation.
- An execution recommendation is not part of the machine handoff unless a signal, task, or packet explicitly references it, and it never authorizes a future stage by itself.
