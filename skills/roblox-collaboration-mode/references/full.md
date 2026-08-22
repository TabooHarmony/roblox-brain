# Collaboration Mode: Worked Examples

Illustrative scenarios for calibrating peer vs autonomous mode and bravery
calls. Adapt to the actual conversation; the skill's rules win over these
examples if they conflict.

## Mode inference

| User says | Mode | Why |
|-----------|------|-----|
| "let's redesign the shop economy together" | Peer | Co-creation phrasing; wants judgment, not output |
| "add a double-jump ability" | Autonomous | Task phrasing; review happens after |
| "can you look at my DataStore code?" | Peer (review) | Asking for assessment; do not rewrite unasked |
| "fix the bugs then push the update" | Autonomous + approval gate | Implementation is autonomous; publishing stays gated |

Mixed requests ("build the leaderboard, and I want to discuss the reward
curve"): split explicitly. Build autonomously, discuss in peer mode.

## Bravery calls

**Low risk, just do it:** renaming `part1` to `LobbyDoor`, rewording a tooltip,
moving parts into a folder. Mention in the summary; no pre-approval.

**Medium risk, do and show:** swapping a `while true do` poll for
`CollectionService` signals. Implement, show the diff, note what changed
behaviorally, invite correction.

**High risk, propose first:** changing a player-data schema version, touching
`ProcessReceipt`, deleting a DataStore key family, enabling StreamingEnabled on
a shipped place. Write a short proposal with the rollback story and wait.

## Process examples

**Asking once, early:** the user says "make saves faster" but the game has two
competing save paths. One concrete question up front ("which path should own
saves: A or B?") beats three silent assumptions or five questions.

**Stating assumptions:** "I assumed coins are the only persisted currency."
One line; the user corrects cheaply if wrong.

**Unverifiable facts:** the user asks to wire a purchase flow against "the live
catalog". If you cannot inspect it, say what was not verified instead of
asserting product IDs exist.
