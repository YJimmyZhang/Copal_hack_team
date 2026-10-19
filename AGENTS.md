# Instructions for every AI agent in this repo (Claude and Codex)

Team: product team = Semen, Jimmy. Business team = Vikas, Flavian.
Ask your human which team they are on if you don't know.

Shared memory lives in memory/:
- brief.md: case, chosen idea, scope. Written at Sync 1. Don't edit it unless your human says the whole team agreed a change.
- business.md: business team's memory. Only the business team edits it.
- product.md: product team's memory. Only the product team edits it.

Start of every session: run `git pull`, read every file in memory/, then answer.

When your human says "save".
- Use short bullets, newest first, max about one page.
- Replace outdated lines instead of adding new ones.
- Then: git add memory/<file> → git commit → git pull --rebase → git push.

If the other team's file is missing something you need, or contradicts our work,
tell your human and add it under "Questions for the other team" in your own file.

Never edit the other team's file. Never force-push.
Explain things simply: your human is not a programmer.
