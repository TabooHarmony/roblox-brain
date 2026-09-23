# Roblox Player Psychology — Full Reference

The behavioral heuristics here are not official Roblox guidance. The paid-random-items rules link to the platform policy.

## 1. The platform and who pays

<!-- temporal: 2026-08 -->
Q2 2026 snapshot (practitioner read of public Roblox reporting): 123M DAU (up 10%, below the 152M Q3 2025 peak), 29B hours engaged (up 5% YoY), 27M monthly unique payers (up 15%), bookings up 8% — spending per hour is falling. Roblox retuned recommendations toward long-term retention; attention is spreading out (top ten games hold only ~⅕ of all playtime). Grow a Garden peaked at 22.3M concurrent players — the ceiling is huge.

Who plays and pays:

- Only 45% of users have age checked; treat demographic splits as a best-available read.
- Adults pay more: US 18+ users monetize >50% higher than under-18s.
- Gender roughly balanced (about half male, close to half female).
- Asia is the biggest growth region: Japan +67% and India +64% in a year.

<!-- temporal: 2026-08 -->
The four dashboards: Acquisition (impressions, qualified play-through rate — does your tile convert?), Engagement (session length, playtime per user), Retention (D1/D7/D30), Monetization (payer conversion, ARPPU).

## 2. The first minute

50% of new players never come back for a second day. This minute is the highest-leverage 60 seconds in the game.

### Six effects that govern it

| Effect | Rule | Design translation |
|---|---|---|
| Zeigarnik effect | Unfinished tasks stay in mind | Hand out an incomplete goal in the first ten seconds |
| Endowed progress | A bar starting partly full beats one at zero | Never begin at level zero |
| Peak-end rule | People remember the best moment and the last one | Put your best effect in minute one |
| Cognitive load | Every extra element costs retention | One mechanic, one button, one goal |
| Isolation effect | The distinct thing gets remembered | Whatever you want clicked should be the only thing glowing |
| Reciprocity | Give before you ask | A free item beats a shop popup every time |

### The timeline

| Time | What happens | Example |
|---|---|---|
| 0–5s | Spawn inside the world | No logo, no cutscene, no dialogue |
| 5–10s | Do the core verb | Steal a Brainrot lets you steal on first spawn |
| 10–30s | First reward lands | Grow a Garden hands you seeds before you decide if you like it |
| 30–45s | Open a loop | Show the next milestone, make it look close |
| 45–60s | Taste of premium | Grant a boost that expires — loss aversion sells it later (e.g. a "crazy OP" wheel spin) |

### What quietly kills Day 1

1. Unskippable intros — taking control triggers resistance before the game starts.
2. A shop in the first 30 seconds — reverses reciprocity; asking before giving.
3. Walls of tutorial text — teach by constraint instead; a corridor teaches direction better than a sentence.
4. A long walk to the fun — goal gradient only pulls when the goal is visible.
5. Lag on join — players don't diagnose performance, they decide the game is bad. (Test by joining cold on the worst device you can find, not your gaming PC; loads in seconds on a 2018 phone.)
6. Asking for a like first — reads as a toll booth; ask after the first reward lands.

### Six-layer player-needs ladder

Each layer maps to a signal; debug from the bottom. Layer 1 "It works and I'm in the game" (first minute; bounce under 60s) → Layer 2 "I know what I'm doing" (first minute; first-session retention, onboarding funnels — the first objective is obvious in seconds; watch five strangers play, don't help) → Layer 3 "This feels good to do" (first session; playtime, D1 — the 30-second loop is fun on its own) → Layer 4 "I'm getting somewhere" (first week; D2–D7, spend days — the next unlock is always visible) → Layer 5 "I matter here" (first month; co-play days — status other players can see; for every reward ask "who sees this?") → Layer 6 "This is mine" (forever; D8–D28, Robux per user — players set their own goals; give depth, then get out of the way).

Note: FTUE/tutorial *structure* lives in `roblox-game-design`; the ladder here is the psychological needs framing and its metric mapping. Measurement used to be a few minutes; now it's 28 days (play days per user tracked at D1, D2–D7, D8–D28). Your first minute still counts, but so does your fourth week. Players tell you what they want. The algorithm tells you where they left.

## 3. Staying rewarding

### Four reward schedules — layer them, don't pick one

1. **Fixed ratio** — reward every Nth action. Predictable and calm; good for drip currency.
2. **Variable ratio** — reward after an unknown count. The strongest schedule there is; this is what crates run on.
3. **Fixed interval** — reward after a set time. Creates appointments: daily chests, timed crops.
4. **Variable interval** — reward after an unknown time. Steady background checking: random events.

Grow a Garden runs all four at once: crops mature on a clock (fixed interval), sales pay per harvest (fixed ratio), mutations are random (variable ratio), weather arrives unannounced (variable interval).

### Why players return on day seven

- **Goal gradient** — effort speeds up near a goal; always show the next milestone as nearly reached.
- **IKEA effect** — people overvalue what they built: bases, gardens, loadouts create attachment.
- **Interrupted tasks** — offline growth timers are an unfinished job you handed the player on exit.
- **Sunk effort** — show total playtime and total collected; visible investment makes leaving feel like loss.

### Hooks between sessions

1. **Appointments** — a reward that matures on a clock turns vague intent into a scheduled return.
2. **Streaks with a safety valve** — always allow one forgiven day. A broken streak produces a quit, not guilt.
3. **Rotation and scarcity** — retire items permanently; it rewards the players who were there.
4. **Clans and shared goals** — if your absence costs someone else, you come back. Cheapest D30 lever there is.
5. **The hook model** — trigger → action → variable reward → investment. Whatever they leave behind loads the next trigger.
6. **Be specific** — "Back in 4h 32m" beats "come back soon".

### Cadence and habit (practitioner)

- Ship weekly — players calibrate to your rhythm; an irregular one teaches them not to check.
- Announce first — anticipation is bigger than delivery; a short teaser ramp beats a surprise drop.
- Rotate, don't only add — rotation brings lapsed players back; additions serve people already there.
- Habits take about 66 days to settle — the D30–D90 window is where a player stops deciding and starts just playing.
- Watch the school calendar — Roblox attributes much of its player swing to seasonality.

## 4. Multiplayer vs solo

What an audience changes:

- **Social facilitation** — people grind harder and longer when someone is watching.
- **Conspicuous consumption** — rare items are bought to be seen; their value is recognition.
- **Social proof** — a shop is an argument; another player wearing the item is evidence.
- **Group identity** — once a player joins a clan, the clan's status becomes personal.
- **Relative deprivation** — a leaderboard makes a good result feel urgent; that keeps a grind alive.
- **FOMO** — you cannot fear missing what you cannot see other people having.

Designing for solo play (self-determination framing):

- **Autonomy** — real choice over what to do; Brookhaven supplies props and lets players supply the purpose.
- **Competence** — difficulty just above skill; Tower of Hell works because failing is instant and cheap.
- **Relatedness** — pets, companions, ghosts, leaderboards: show that other humans exist somewhere.

### What each mode does to your numbers (practitioner)

| Metric | Solo-leaning | Social-leaning |
|---|---|---|
| D1 retention | Strong at any population | Fragile if servers look empty |
| Session length | Shorter | Much longer |
| D30 retention | Weaker | Much stronger |
| ARPPU | Lower | Higher |
| Growth from players | Near zero | Real |
| Risk | Low | High — decline spirals |

Template: Pet Simulator 99 / Grow a Garden — farm privately where pacing is yours, then carry the result to a shared plaza where the whole point is being seen.

## 5. Monetization psychology

### What you are pricing against

Roblox takes 30%: a 799 R$ pass nets ~559 R$ before cashing out (DevEx pays less per Robux than players paid to buy it). Approximate US spend tiers:

| Spend | On web | In app |
|---|---|---|
| $4.99 | 500 R$ | 400 R$ |
| $9.99 | 1,000 R$ | 800 R$ |
| $19.99 | 2,000 R$ | 1,700 R$ |
| $49.99 | 5,250 R$ | 4,500 R$ |

Verify pricing before building a model on it (regional pricing: see `roblox-monetization`). Everyone holds an odd Robux balance; bundles are fixed, so price items just under common leftovers. Few players ever pay — you are designing for a small minority, which is why the **first purchase matters most**.

### Pricing principles (practitioner)

- **Charm pricing / left digit** — price is read left to right: 499 files as "four hundred something"; 500 does not. Decades of retail taught people that a nine means a deal, even with nothing to compare.
- **Precision reads as fair, round reads as premium** — 349 looks calculated; 350 looks arbitrary and invites questions. For status buys, round numbers feel considered. Luxury does not price at 999.
- **Anchoring** — the first price seen sets the scale; show the most expensive bundle first.
- **The decoy** — add an option clearly worse than your target; it doesn't need to sell.
- **Price signals quality** — too cheap reads as useless; underpricing your best pass costs more than overpricing it.
- **Bundling** — combining items blocks comparison, which is why bundles hold margin.

### The 4-band gamepass ladder

| Band | What you sell | Notes |
|---|---|---|
| 49–99 R$ | Break the threshold | Small cosmetic or starter boost. Exists to create a first purchase, not profit. |
| 199–399 R$ | Convenience | Auto-collect, storage, speed — selling time causes the least resentment. |
| 499–799 R$ | Luck and power | Multipliers and boosts; in most simulators the top-earning band. |
| 999 R$ and up | Identity | VIP tags, exclusive areas, unique cosmetics. Price it round, describe it plainly. |

Never sell raw victory — sell time, luck, expression, and access.

### The infinite pack (ladder monetization, practitioner)

- A ladder of rewards with rising prices, roughly 50 R$ at the bottom to 2,400 R$ near the top.
- Refreshes weekly — each update brings a new themed ladder with new exclusive pets.
- Rungs improve as they cost more — payoff grows as fast as the price.
- There is no last purchase — no single decision ever feels large.

## 6. RNG, crates, and pity

### What happens when a crate opens

- **Variable reward** — unpredictable payouts produce the highest, most persistent effort of any schedule.
- **Anticipation, not payout** — the response peaks during the wait; the opening animation is part of the reward.
- **Uncertainty adds value** — randomising a reward you were giving anyway increases how much it feels worth.
- **Near miss** — one tier below the top reads as "almost", which is why escalating reveals work.
- **Feeling due** — players believe a bad run means a good result is coming; a pity counter makes that true.
- **Illusion of control** — letting people pick which crate raises satisfaction with identical odds.

### Pity systems

- **Hard pity** — guaranteed top-tier at N opens; removes the worst case entirely.
- **Soft pity** — odds climb after a threshold; players feel it heating up.
- **Rising odds** — chance grows on each failure and resets on a win; same average, no brutal streaks.

Rules of thumb (practitioner):

- **Show the counter.** "34 of 50" turns open-ended frustration into a goal.
- **One counter per rarity** — then no session ever feels like pure loss.
- **Never reset it quietly.** Players forgive bad odds; they do not forgive numbers that move.

### Rarity that carries meaning

Five tiers is the sweet spot: more dilutes meaning, fewer flattens the chase.

| Tier | Chance |
|---|---|
| Common | 55% |
| Rare | 27% |
| Epic | 12% |
| Legendary | 5% |
| Mythic | 1% |

- Lock one colour to one tier; reuse it elsewhere and you've spent the signal.
- Scale spectacle steeply — a Mythic should look ten times bigger than a Legendary, not slightly bigger.
- **Show the whole pool** — knowing what's inside creates specific wanting; a mystery pool creates none.
- Sets drive more opens than items — an incomplete collection pulls harder than any single reward.
- Quick test: would a player post a clip of your top tier?

### Paid RNG implementation note

If Robux can buy an item directly or fund the currency used for a random outcome, check [Roblox's current guidance](https://create.roblox.com/docs/production/monetization/paid-random-items) when implementing the purchase. It covers numerical odds, paid luck boosts, and user-specific restrictions. Restricted users can still have options such as an earnable path, a disclosed non-random sequence, or a direct purchase. These are implementation choices, not a reason to avoid RNG design. For purchase and `PolicyService` code, use `roblox-monetization`.

Ethics note: about a third of age-checked daily users are under thirteen. Use these mechanics to make *earning* feel good, not to make *stopping* feel impossible.

## 7. Community

### The loop you are building

01 A moment worth sharing happens → 02 Somewhere exists to share it → 03 Sharing earns status in the group → 04 The post reaches new people → 05 New arrivals make new moments → (back to 01).

- Your job is steps one and two; the rest runs itself.
- Grow a Garden grew on word of mouth, not advertising.
- Members churn far less than players — they have more reasons to return than the game supplies.
- Rivalries are free marketing: a staged feud between two games pushed Roblox to 47M players at once. <!-- temporal: 2026-08 -->

### Channels you own

**Discord:**
- Pay for the join — attach an in-game reward; never post a bare invite.
- Roles as a ladder — verified roles for rare owners cost you nothing to mint.
- Give people jobs — testers, bug hunters, event mods; contributors don't quietly leave.
- Run a wins channel — player-posted rare pulls are free proof for everyone else.

**Clips and fan work:**
- Give them a reason to record — rare pulls, huge numbers, dramatic failures.
- Be recognisable in a thumbnail — a distinct visual signature is worth more than fidelity.
- Feature clips in game — recognition motivates creators more reliably than currency.
- Support the fan wikis — community value lists make your items feel like real assets.

**Creators, giveaways, teasers:**
- Give first — send codes and exclusives before asking for coverage.
- Smaller creators convert better — 10k–100k subscribers beats the biggest channels per view.
- Name an item after them — coverage becomes self-interested, and it keeps happening.
- Make entry cost effort — a small task raises how much the prize feels worth.
- Always show the winners — one unverified giveaway destroys trust in every future one.
- Reveal one thing at a time — a silhouette beats a full reveal; five days, five reasons to check back.

## 8. Order of work and review

Build in this order (practitioner):

1. **Fix Day 1** — instrument everything, no dead ends; first reward inside 30 seconds; one mechanic in minute one; fix load times; aim for 20% D1.
2. **Build Day 7** — a milestone ladder with no dead ends; a collection to complete; a daily hook with a safety valve; one social feature; aim for 8% D7.
3. **Add pricing** — a 49 R$ first purchase; a 4-band ladder; convenience before power; RNG last, with odds and pity; track conversion and ARPPU apart.
4. **Community** — a weekly rhythm first; Discord with a rewarded join; a teaser ramp before each drop; creator relationships early; aim for 3% D30.

### Mini summary

1. Give before you ask — reward in the first thirty seconds.
2. Leave something unfinished — an open loop beats a satisfying ending.
3. Make ownership visible — value comes from being seen.
4. Show odds and counters — transparency makes a 1% drop rate survivable.
5. Build the community early — it is the audience no algorithm can take.
6. Remember who is playing — a third of the platform is under thirteen.

### Deliberate scope boundaries (see SKILL.md)

- Core loop, FTUE/tutorial structure, level design, economy sources/sinks, retention phases, juice, Bartle types → `roblox-game-design`.
- Dashboard diagnosis, discovery/packaging, algorithm mechanics, experiments, LiveOps cadence → `roblox-growth-design`.
- Purchase implementation, PolicyService code, regional pricing, price optimization → `roblox-monetization`.
