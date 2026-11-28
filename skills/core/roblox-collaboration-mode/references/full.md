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

**Accepted risk vs mandatory policy:** "I accept the risk; ship it anyway"
works for otherwise permitted actions and is noted in one line. It never
overrides a mandatory platform policy or a failed or unverified gate. When the
user's choice conflicts with policy (for example, shipping paid random items
unchanged for a restricted user), do not implement it: restate the compliant
alternatives once and proceed with a compliant treatment or stop and report.

## Checkable collaboration rules

### Start from the current brief and state

- Load the collaboration skill and applicable domain skills before planning or editing. Extract their task-specific acceptance checks; record the evidence for each applicable check before reporting completion. Loading a skill alone does not satisfy it.
- Read the current source, installed state, and latest owner decisions before reopening a task from memory. Distinguish implemented, tested, approved, deferred, rejected, and live work.
- Convert observations into a persistent numbered log before fixes begin. Include positive feedback and approved elements, each deferred item's next action, and any evidence still missing. Reconcile the log with current state at handoff and after context recovery.
- Separate the owner's authority, the agent's current credentials, and the scope of granted authorization. Check authorized project configuration and documented credential stores before asking for a key again; report presence and usability without printing secret values. Carry forward explicit authorization within its actual scope.

### Ground recommendations in evidence

- Label observations, hypotheses, confidence, and the evidence that could change the recommendation. When advice changes, identify the new evidence or the premise that was corrected. Push back on unsupported conclusions; do not increase confidence merely because the owner agrees or disagrees.
- Treat earlier AI analyses as leads. Recheck their source, date, metric definition, and causal interpretation before reusing them.
- Identify whether a reference is a live observation, historical place, partial client/shared code, template, or reconstruction. Cite the actual inspected material; do not infer undocumented server behavior or commercial success from source structure.
- Inspect a named visual reference before claiming fidelity. Compare the result with it; describe intentional departures as interpretation. Access to a reference does not establish permission to reuse its assets.

### Preserve approval while correcting defects

- For a narrow correction, identify the approved baseline and change only the properties needed to fix the defect. Compare before and after on the actual requested surface; preserve accepted layout, composition, effects, and unrelated work.
- After repeated subjective misses, validate one representative implementation against the owner's references before spreading it to related screens or rooms. Record the approved pattern and then check every adapted flow.
- Honor a requested preview checkpoint before upload or replacement. Stop editing a design surface when the owner disapproves it; resume that surface when new direction authorizes work. Continue independently authorized tasks.
- Verify delegated work against the brief and actual installed result. A worker's report or a clean diff cannot establish that the right screen, state, device, or behavior was tested. Keep unmet checks visible instead of reopening approved work or silently dropping observations.

### Shared Studio etiquette

The Studio an agent reaches is often the user's own, in use. These rules apply on any bridge (`roblox-studio-mcp`).

- **Ask before taking over the machine.** Bringing Studio to the front, sending simulated keys or clicks, and starting or stopping Play take over the user's computer. Ask for that specific run and say how long it takes; a one-line heads-up is not consent. Without a yes, measure what focus doesn't affect (script time, profiler data, logs), state that frame times are capped in the background, or hand the test to the user with what to look for.
- **Read the session before acting.** Check play state before running scripts, moving the character or starting a test. A playtest you didn't start belongs to the user; stopping it or sending input interrupts them. The user may also start playing inside a session you started: before and between scripted runs, look for input you didn't send (an equipped tool, position changes, logs from places you never went) and read odd numbers with that in mind.
- **Hand back clean.** Stop debug sessions you started, zero network simulation, restore time scales, cameras and device simulation, and say if anything was left in a debug state.
- **Verify by looking, then say fixed.** A passing test that skips the real client path proves little: one runtime error early in a client action can drop every later effect while server-side tests pass. After any change (yours or a worker's), run one action of each affected kind through the real client, read the client error log grouped by message, and look at the result before calling it done.
- **Test from the state a real player reaches.** A change on a shared path broke a slow weapon's refire only after stowing, and fresh-state tests missed it. Script the real sequence (use, stow, return, use), and list which approved items a shared-path change touches before shipping it.
- **Batch playtests.** Playtests and captures are the most expensive part of a session and often answer nothing. Before starting one, name the question it answers that reading the code can't; batch every runtime check for a change set into one session; read code first for feel bugs (in one project about 15 scripted playtests failed to reproduce a bug that reading the code found in minutes); when the user already reports a system as weak, build the fix instead of gathering evidence of how bad it is.

### Design decisions stay with the owner

- "Make a fresh HUD" or "redo the shop" is still a design decision: what is always on screen, where currency lives, the phone layout. Bring the open questions with two rough layouts and a recommendation, get answers, then build.
- Before a plan goes for approval, check that its numbers can produce the picture it promises (counts and sizes against the approved concept). If a budget can't reach it, say so first. When the owner pushes back twice on the same thing, stop, measure the cause, and lead with what the numbers say.
- When asked to analyze or "think it through", deliver the real questions, the strongest case each way, the unknowns and what would resolve them, and the questions only the owner can answer. Don't end with a verdict unless asked.

