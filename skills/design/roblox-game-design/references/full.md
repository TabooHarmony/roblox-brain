# Roblox Game Design Fundamentals: Full Reference

Structural craft: core loops, tutorials/FTUE, level design, economies, retention phases, juice, player-type balance, grind avoidance, curation readiness.

Sections 1–8 are design guidance; sections 9 and 10 link to Roblox's Today's Picks and Moments posts.

**Scope boundaries (cross-references):**
- Funnel metrics, discovery algorithms, experiments, LiveOps cadence, monetization packaging → `roblox-growth-design`
- Persuasion mechanics: first-minute timelines, cognitive effects, reward-schedule detail, pricing psychology, RNG/pity, community loops → `roblox-player-psychology` (reinforcement schedules are covered there; one-line summary in §6 here)
- Juice/particle implementation in Luau → `roblox-animation-vfx`
- Economy telemetry and dashboards → `roblox-analytics`

---

## 1. Core Loop and the 3-Layer Retention Stack

A game must function at three time scales **simultaneously**; each layer only works if the one beneath it works:

| Layer | Time scale | Focus | What it must deliver | Typical metric |
|---|---|---|---|---|
| 1. Core loop | Moment-to-moment | Intrinsic fun of the raw actions | Movement, combat, interaction feel satisfying *on their own* | Session length |
| 2. Meta-game | Hour-to-hour | Short-term goals | Clear a level, upgrade a character, afford the next item; the "just one more round" engine | D1 retention |
| 3. Long-term progression | Day-to-day/month-to-month | Social identity, mastery, investment | Ranks, leagues, guilds, collections; sunk cost + belonging make quitting expensive | D30 retention |

**Design rules of thumb:**
- Diagnose upward, build downward. If D1 is bad, the problem is almost always layer 1 or 2, never layer 3.
- The core loop is the *rational* contract ("is this functional and fair?"); juice and emotional design (§7) are what make it *felt*. Players join for mechanics and stay for the emotions those mechanics evoke.
- Every action in the core loop needs immediate, clear feedback; without feedback the psychological loop breaks (sense of control collapses).
- Shorten the time to the first emotional peak (the "aha!" moment). Everything in the first session should drive toward it.

**Emotional vs. rational design:** rational design = rules, math, UI, controls ("is it functional and fair?"); emotional design = narrative, status, juiciness ("how does the player feel?"). Retention lives in the emotional layer: feedback loops, juice, endowment (let players own/customize their identity early), anticipation, and near-miss displays. But a game that becomes "too rational" (chores for a pass) kills the emotional connection and burns players out.

---

## 2. Retention Phases ([Department of Play framework](https://departmentofplay.net/retention-framework-keep-your-players-forever/))

Published by Department of Play on Unity LevelUp. Core thesis: as a game matures, what keeps players shifts from **mechanics and novelty** toward **social connection and community**.

### Short-term (D0–D7)
- **Understandability**: the FTUE must make the game immediately graspable; players who don't understand how to play leave.
- **Novelty**: a unique or fun hook that makes the game memorable and shareable.
- **Technicality**: stability. Crashes, long loads, and heavy battery/data use kill week-one retention.

### Mid-term (D7–D30)
- **Progression vectors**: clear goals and visible advancement (XP, level maps, unlocks).
- **Mastery**: opportunities to improve skill or strategy once novelty wears off.
- **Return triggers & nudges**: timed rewards, daily login bonuses, notifications that build a habit. (Use with restraint: weaponized habit-building is the burnout path; see §8 guardrails.)

### Long-term (D30–D90)
- **Social comparison**: players stay to see how they stack up: PvP, leaderboards, power rankings.
- **LiveOps**: fresh content, timed events, seasons to prevent boredom. (Cadence and planning → `roblox-growth-design`.)

### Terminal (D90+)
- **Meaningful social interaction**: friendships, clan allegiance, rivalries, not gameplay.
- **External presence**: community spaces, content ecosystems, identity outside the app.

**The Chess analogy:** Chess has had no "content update" in centuries yet retains players for decades, because its value is entirely mastery + community. Terminal retention means the game has transitioned from software to **social platform**.

**Roblox mapping:** D0–7 is your FTUE and first-session loop; D7–30 is your progression/meta-game; D30–90 needs leaderboards/groups/updates; D90+ is served by Roblox groups, community Discords, and social features. Session count, session length, and retention are the three metrics that feed both ad-style and purchase-style revenue; steady revenue needs players returning over months, not a launch spike.

---

## 3. Tutorial & FTUE Structure

### 3.1 Teach through experience ([Berbece, GDC: "This is a Talk About Tutorials, Press A to Skip"](https://gdcvault.com/play/1023845/This-is-a-Talk-About))

Tutorials fail when the developer "holds the player's hand" or slaps information on at the last minute. The best tutorial is one the player doesn't realize they're playing.

**Avoid:**
- **Popups**: they break gameplay and immersion. Embed information in the game world.
- **Information overload**: full control schemes or walls of text before play begins; players can't memorize any of it.
- **Static prompts**: prompts should be dynamic: show the right glyphs for the player's actual device (touch vs. gamepad vs. keyboard).

**Practices:**
- **Teach gradually**: one mechanic at a time, in context.
- **Environmental teaching**: introduce threats in safe conditions. Classic example: in *Half-Life 2* the player watches a ceiling creature catch a bird, learning the danger without experiencing it.
- **Leverage standards**: universal conventions ("red is bad," WASD to move, analog-stick to walk) let intuition do the teaching. On Roblox, that means default controls players already know and standard UI patterns from other Roblox games.

### 3.2 Teaching complex systems ([Game Maker's Toolkit](https://www.youtube.com/watch?v=-GV814cWiAw))

- **The investment gap:** tutorials dumped on players *before* they're invested fail. Delay each lesson until the moment it becomes relevant; invested players *want* to learn.
- **The inverted pyramid:** start with very few decisions (e.g., *Civilization* begins with one settler and one city) and let complexity balloon naturally.
- **Dynamic UI:** hide complex UI until needed (*Mini Metro*'s interface grows as the city grows).
- **Kinesthetic learning:** players learn by *doing*: small performable puzzles beat "click here" arrows.
- **Show, don't tell:** short animations/images explaining mechanics beat text.
- **Familiarity:** map systems onto real-world logic (fire is hot; icons that look like map apps mean location).
- **Feedback loops:** for slow-feedback genres, use advisor characters or sped-up scenarios so players see consequences of decisions quickly.
- **Why it matters:** better onboarding is how complex genres grow their audience instead of staying niche.

**Failure case: Artifact (2018, Valve/Richard Garfield):** front-loaded complexity (three lanes at once), a tutorial that taught mechanics but not strategy (players never learned *which lane to lose*), and no safe way to learn the economy (pay to buy the game, buy packs, *and* pay a ticket to compete). Result: players felt they were losing to chaos rather than learning; ~95% churn in month one. Lesson: famous designers and good math don't survive a broken confidence-building loop.

**Success case: Hades:** death is both the Ketsu (conclusion) and Ki (introduction) of the next loop; complexity is gradual (one weapon first, one Boon layer at a time); dying *advances the story*, so failure produces progress. Because players *expect* to die, frustration is defused, and adaptive options (God Mode quietly raising resistance per death) adjust difficulty for strugglers.

### 3.3 First-session craft

Three pillars: **Learning** (teach controls in context; actions should have meaning, e.g., placing the final puzzle piece), **Discovery** (remove friction; let players explore; use delight so they feel they chose well), **Motivation** (early rewards; tease future content; show the level's end at its start).

Six tactics:
1. **Expression of personality**: let players pick character/color/name immediately; instant agency and investment.
2. **Highlight your best asset**: show your unique selling point in the first level, not level 15 (most players never reach it). Quality loading screen with logo.
3. **Narrative & open loops**: a short, *skippable* animated setup (the *Subway Surfers* guard chase) gives context.
4. **Juicy rewards**: "nerf" the player's default state in the tutorial, then hand back their standard power as an upgrade. Feels powerful instantly.
5. **Balanced pacing**: no "homework" tutorials full of arrows; stagger lessons.
6. **Peek curiosity**: show short-, medium-, and long-term objectives; display locked items/areas players can look forward to.

Supporting rules: lead the player to the "aha" moment stripped of secondary features (cognitive load is the enemy); progressive disclosure: introduce mechanics only when relevant; the **empty-state problem**: if the experience depends on other players/data to look alive, fill the first minutes with bots/sample data/NPCs; **friction vs. reward**: every bit of required effort must be met with an immediate micro-reward; **zero-death onboarding**: the first session should be a frictionless run of successes; **fake choice**: small path choices (even cosmetically equal) build agency.

Mobile-gamer survey (~23,000 respondents). Top quit reasons: not fun (39%), too many ads, bugs, progress takes too long (29%). Top stay reasons: fun gameplay (51%), engaging story (40%), right level of challenge (38%), lots to collect/level up.

---

## 4. Level Design

### 4.1 Kishōtenketsu: the 4-step structure ([Mark Brown on Super Mario 3D World](https://www.youtube.com/watch?v=dBmIkEvEBtA))

A four-beat structure from East Asian narrative tradition, applied to teaching a mechanic; the player is constantly learning and surprised without being overwhelmed:

1. **Ki (Introduction)**: the mechanic appears in a **safe environment**. The player must use it to progress, but failure punishes nothing (no enemies, no pits).
2. **Shō (Development)**: stakes rise. The mechanic combines with basic platforming or minor threats; the player demonstrates they understood step 1.
3. **Ten (Twist)**: the "aha!" moment. The mechanic is used in an unexpected way, inverted, or combined with itself in a new context. This is the fresh challenge.
4. **Ketsu (Conclusion/Bonus)**: a final, safe "victory lap" using the mechanic once more on the way to the goal, ending on a feeling of mastery.

Use it per-mechanic within a level, or as the whole level arc. It answers "how do I pace teaching?"; never introduce and test a mechanic in the same beat.

### 4.2 The invisible hand & fairness (Super Mario Maker)

- **Design for the player, not the creator.** A level that is hard just for hardness's sake fails because it ignores the player's learning curve.
- **The invisible hand:** guide with coins, arrows, lighting, enemy placement, and level geometry instead of text boxes. The player should feel they found the path themselves.
- **Fairness ≠ easiness:** the best challenges are fair; death should feel like the player's fault, never the designer's prank ("troll" design breaks trust). When RNG decides outcomes, *explain its logic* or deaths will feel like the designer's fault (the Artifact lesson).
- **Iterate by watching:** playtest by observing someone else play. It is the fastest way to find broken visual cues and flow breaks. (A Kishōtenketsu read on live ops: the twist is where players are challenged; the conclusion is where they consolidate; ship content with both.)

---

## 5. Economy Architecture

Game economy design:

### 5.1 Sources and sinks: the plumbing

Every economy is a pipe system:
- **Sources (inflow):** kills, quests, dailies, real-money purchases.
- **Sinks (outflow):** gear, upgrades, entry fees, repairs, cosmetics.
- **Balance:** sources too strong → **inflation** (money loses meaning; boredom). Sinks too strong → **deflation / choke points** (players can't progress without paying; frustration/churn).

The shop is not just a storefront; it is a **necessary soft-currency sink** that keeps players "hungry" for more gameplay.

### 5.2 Three currency types

| Type | Earned by | Spent on | Purpose |
|---|---|---|---|
| **Soft** | Gameplay (e.g., gold) | Frequent, low-value upgrades | Keeps the core loop moving |
| **Hard** | Rarely; usually bought (e.g., gems) | Skips, premium cosmetics, timer bypasses | Monetization + long-horizon goals |
| **Social / energy** | Social interaction or time (e.g., hearts) | Session-bound actions | Controls session length, drives retention |

### 5.3 The power curve: progression vs. inflation

Players earn more per minute as they progress. A sword costing 100 gold at level 1 is worthless to a level-50 player earning 10,000/minute. Fixes:
- **Scale prices alongside earning potential**, and/or
- **Introduce higher-tier (or prestige) currencies** that reset the economy for advanced players.

### 5.4 Being the economic governor

- Tune the "faucet" (reward drip rate) with tests, not vibes: if players quit at level 5, the faucet may be too tight.
- The designer-economist's job: find the point where players feel they get value while the game stays sustainable; like a central bank managing currency in circulation. Too much money → boredom (inflation); too little → quitting (deflation).
- Balance is monetization-adjacent: too easy → nothing worth buying; too hard → churn before spending.

### 5.5 Economic health indicators

| Indicator | Meaning | Action |
|---|---|---|
| **High hoarding** | Players save currency instead of spending | Introduce a limited-time sink or a new upgrade tier |
| **High churn at choke points** | Players quit where costs spike | Increase soft-currency sources, or offer a one-time bridge discount |
| **Currency devaluation** | Items feel too cheap for veterans | Add a second hard/prestige currency |

**Case studies:** *Artifact* died partly of economic design; a pure marketplace model let card prices crash within days (a $20 hero card → $0.50), and with no free path to play, churn was near-total. *Hades* runs multiple scarce currencies (Darkness, Keys, Gems, Nectar) and uses "Prophecies" (quests) to nudge players toward untried playstyles before boredom sets in.

Cross-reference: instrument these flows → `roblox-analytics`; monetization packaging and pricing → `roblox-growth-design` and `roblox-player-psychology`.

---

## 6. Juice & Game Feel

**What it is:** tactile, satisfying audio-visual feedback layered on core actions (as in Nuclear Throne): screen shake, hit-stop, particles, sound layers, punchy animation. Juice distracts the brain from repetition and keeps endorphins flowing; it turns a rational action (clicking a button) into an emotional reward.

**Where it applies:**
- Every core-loop action the player repeats most often (jump, shoot, collect, place); juice investment should be proportional to repetition frequency.
- Reward moments (level-up, gacha pull, purchase confirmation, rare drop): the highest-visibility surfaces.
- UI reactions (button presses, toasts): cheap wins that make the whole game feel alive.
- FTUE: the "nerf-then-restore" trick (§3.3) only works if the restore *feels* powerful; that's juice.

**On Roblox:** 3D ParticleEmitters don't render over UI; community tools like Emitter2D convert them to 2D UI particles, which are also cheaper on mobile. For implementation patterns (particles, screen shake, sound design in Luau) → `roblox-animation-vfx`.

**Caution:** juice amplifies whatever loop it decorates. It makes good loops irresistible and bad loops visibly hollow. Juice is *not* a substitute for a fun core action.

---

## 7. Bartle Player Types & Ecosystem Balance

[Bartle's player taxonomy](https://mud.co.uk/richard/hcds.htm) classifies players on two axes: **Action (acting vs. interacting)** × **Focus (players vs. world)**.

| Type | Suit | Motivation | Design elements that serve them |
|---|---|---|---|
| **Achievers** | ♦ Diamonds | Mastery and status: level up, complete, top leaderboards | Levels, badges, completion bars, achievements |
| **Explorers** | ♠ Spades | Discovery: hidden areas, secret mechanics, lore | Secrets, rare loot, deep/interlocking systems |
| **Socializers** | ♥ Hearts | Connection: the game is a backdrop for people | Chat, guilds/groups, emotes, team tasks |
| **Killers** | ♣ Clubs | Dominance: win against others, show superiority | PvP, global rankings, rare cosmetics as status |

**The ecosystem logic:** the four types feed each other:
- Achievers need Explorers (who find the equipment and secrets Achievers use to level).
- Killers need Achievers (high-value targets to prove dominance against).
- Socializers keep the community alive and are the audience for everyone else.
- If one group (usually Killers) becomes dominant, it drives out Socializers and Explorers, and the population collapses (the "MUD logic").

**Practical Roblox rules of thumb:**
- Build content for all four, in proportions matching your game's premise (a PvP arena over-serves Killers by design; make sure Socializers have a reason to stay anyway: teams, chat, cosmetics).
- Feature mapping: leaderboards/quests → Achievers/Killers; secrets/unlockables → Explorers; groups/community spaces → Socializers.
- Watch your player mix in telemetry; a shift toward one type often precedes a decline in the others.

---

## 8. Grind Avoidance

**Grinding is not a mechanic; it's a state of mind.** It sets in when a player stops enjoying the immediate experience and continues only for the promise of future fun. The same repetitive mechanics can be engaging or a chore depending on three fixes:

1. **Juice (game feel)**: satisfying feedback on every repetition (see §6). *Stardew Valley*: watering crops is a "chore," but the sound effects and soundtrack make it feel rewarding.
2. **Challenge (skill ceilings)**: constant opportunities to improve skill and understanding so play never becomes routine. *Into the Breach* stays engaging because it's nearly impossible to fully optimize. *Stardew*: Community Center bundles push players to explore every facet of the game within time limits.
3. **Division (measurable chunks)**: break gameplay into small chunks with immediate, measurable rewards. *Minit* resets progress every 60 seconds, but each run yields new items or knowledge. *Stardew*: every in-game day offers short-term goals that feed long-term progress; players always end a session having achieved something. (Duolingo-style XP bars do the same for mundane tasks.)

**Dark-side guardrail:** some games deliberately make progression unsatisfying so players buy loot boxes or skips to bypass the tedium. That is grind-as-monetization, and it trades LTV for resentment (regulatory heat included). Roblox-relevant version: if your game's "wait" exists only to sell the skip, players feel disrespected and churn; the churn data shows up at exactly your choke points (§5.5).

Ethics line: behavioral design that accelerates the "aha!" and mastery is legitimate; design that *manufactures frustration to sell relief* is the dark pattern. When in doubt, ask "would this still be fun if nothing were for sale?"

**Reinforcement schedules** (fixed/variable ratio, fixed/variable interval, the Skinner-box material underpinning reward pacing) are covered in detail in `roblox-player-psychology`; the one-line version: *variable* schedules produce the strongest repetition and are the mechanism behind loot boxes; handle with the ethics line above.

---

## 9. Today's Picks: Roblox Curation Criteria (official)

Summarizes Roblox's official DevForum guidance on **Today's Picks**, the human-curated section of the Home page highlighting high-quality, innovative, safe experiences. This *is* official Roblox material, unlike the sections above.

**What curators look for:**
1. **Quality & polish**: not raw graphical fidelity but *consistency*: intuitive UI, seamless FTUE, no major bugs.
2. **Engagement & retention**: data showing players come back (evidence the core loop and meta-game work).
3. **Originality**: something new for the platform: a unique mechanic, a fresh genre take, or an underrepresented art style. Soulless clones don't get picked.

**Baseline requirements:**
- Full compliance with Roblox Community Standards and Terms of Use.
- **Mobile must work**: a large share of Today's Picks traffic is mobile; a broken mobile UI is an automatic disqualifier. Play well on phone, PC, and console.
- Localization (multi-language support) strengthens the case for global curation.
- Accurate, high-quality store metadata: icon, thumbnails, description that honestly represent gameplay.

**Process:** a mix of algorithmic discovery and manual applications/nominations via Roblox-provided survey links; curators are humans looking at your store page and your game.

**Design implications:** the curation checklist is essentially this skill in audit form: FTUE (§3), polish/juice (§6), working core loop (§1), originality, and honest packaging.

---

## 10. Roblox Moments: Clip-Based Discovery (official)

Summarizes the official Roblox Newsroom post **"Roblox Moments: User-Generated Discovery."** Moments is a social, clip-based discovery feed: short vertical video clips captured by players (or developers) surface in Discovery, and viewers can teleport directly into the experience from the clip. It replaces static thumbnails with player-vouched proof of fun and cuts the friction between seeing a game and playing it. This *is* official Roblox material.

**Design for the camera: make your game clippable:**
- **Design clippable peak events**: visually distinct, dramatic moments (a massive boss explosion, a synergy buff firing, a rare pull) that read at a glance in a vertical crop.
- **Vertical compatibility**: the UI must not look cluttered when cropped or viewed in the Moments vertical interface; keep the frame's center readable.
- **High-intensity visuals pay off**: juice (§6) is now a discovery surface, not just polish: clips of juicy moments vouch for your game better than studio trailers, because a real player laughing/achieving carries trust.
- **Capture & share tools**: make it easy for players to record and share peak moments; every share is an organic acquisition loop.

**Strategic stack:** Moments clips create desire → teleport button satisfies it → Today's Picks badge (§9) seals trust → the retention stack (§1–2) keeps players there.

---

## Quick Diagnostic Checklists

**Core loop audit:** Is the base action fun with no rewards attached? Does every action give immediate feedback? Is there a short-term goal always visible (meta-game)? A long-term identity goal (progression layer)?

**FTUE audit:** Zero deaths in the first session? One mechanic at a time, in context? No popups (info in-world)? Skippable narrative? Personality choice in the first minute? Best asset shown in the first level? Locked content teased? Aha-moment reached in the first session?

**Level audit (Kishōtenketsu):** Safe intro before any test? Development before the twist? A genuine twist? A conclusion beat that feels like mastery? Does death always feel the player's fault? Do coins/geometry/lighting guide without text?

**Economy audit:** Listed all sources and sinks with rates? Sinks balance sources at every progression band? Prices scale with the power curve (or a tier-2 currency resets it)? Watching hoarding, churn-at-choke-point, and devaluation indicators? Shop doubles as a soft-currency sink?

**Ecosystem audit:** Content exists for all four Bartle types? No group (usually Killers) able to dominate the experience for others? Socializers have a home even in competitive games?

**Grind audit:** For each repetitive task: is it juicy? Is there a skill ceiling to push? Is it chunked with measurable reward per chunk? Would a player answer "why am I doing this?" with fun rather than "for later"? Does any wait exist *only* to sell the skip?

**Curation readiness (official criteria):** Mobile-first polish? Stable, bug-free FTUE? Retention data to show? An original hook? Honest, high-quality store page? Standards-compliant?

---

## Field data: design and playtest observations

<!-- temporal: 2026-09 -->

These are experience-based observations, not controlled experiments. Numbers describe individual cases, not platform benchmarks. **CONFLICT** marks disagreement between reports.

### Onboarding and tutorial craft

**Measured teardown** (lucky-block/roll game, adopted wholesale by its dev): show interactables only when relevant; make first-collection moments effect-laden; tutorial waits ≤1s for anything; cheap x2/x3/x4 boosts at 2/5/9 Robux (PCR matters for the algo, ARPPU doesn't); support click AND E-prompt; roll fast, slow-down only for big rolls; seed guaranteed early rares as the hook; celebrate rares with confetti + notification.

**Length benchmarks:** sub-1-minute ideal; ~1 min already too long; recent hits run 15–20s tutorials; a 30-step tutorial destroys funnel completion; a 7-minute follow-steps tutorial was "way too long"; target each earn-step ≤3s and temporarily boost gain rates during the tutorial (players won't notice the change afterward).

**Tutorial guidance:** cut text (~5 words max), get interactive, move guidance off UI paragraphs into highlights/arrows, show-not-tell, explain WHY not just HOW ("hatch a bee so you can have a larger swarm").

**Measured friction killers:** requiring tool equip (players think the game is broken); objectives needing unaffordable currency; uncompletable steps (rebirth locked during tutorial = "I left at this point"); spawning far from the first objective; 15 jumps where 5 would do; forced multi-minute onboarding (one TD's funnel data: most players quit within 5 minutes of a 3-minute forced tutorial). Fix friction by removing the step, not adding UI: "open inventory to equip your reward" bounced players → auto-equip, teach inventory later; moving a tutorial target next to spawn cut first-step failure 22% → 12%; teleport the player to each objective.

**UX rules from repeated feedback:** hide all UI except what the tutorial needs (full HUDs overstimulate), reveal progressively; give each action a visual ghost/demonstration; make the tutorial mandatory (players skip optional ones without noticing); end exactly where the core loop closes (teach rebirth last, as the loop's endpoint); design so a non-English-speaking kid understands from what's on screen alone; "comprehensible without text" is the gold standard for kid-facing games; grab focus in the first 5 seconds; the first 90 seconds make or break the game.

**Edge cases:** a kick mid-tutorial-step must reset to the correct step or the state machine breaks; give new players a safe zone during the tutorial and disable purchases they shouldn't make yet (one player dumped his money into the wrong shop and quit). Players leave right after the tutorial when there's no post-tutorial income loop; diagnose drop-offs there and add a passive-income mechanic.

**Dopamine overload is a real failure mode:** a VFX-drowning game had a long first session but burned players out; effects stopped meaning anything and they never returned. Restraint preserves the reward system; cut visual noise (excessive particles, cursor popups, click clutter); save spectacle for upgraded states. A follow-up game succeeded under this hypothesis.

**Pacing mechanics delivery:** don't dump all mechanics in the first 5 seconds; introduce one at a time; hide the rest of the map during onboarding; keep a persistent navigation arrow (not tutorial-only); onboarding text huge white-with-black-outline; UIStroke highlighting to make target buttons pulse.

**Onboarding timing:** guarantee the first upgrade purchase within 30s–5min; first upgrade within ~30 seconds ("start with one spinning axis so players learn there's more"); balance so the money-boost upgrade is affordable immediately. No pop-ups at spawn; daily rewards only after the tutorial. Tutorial beats trigger on player state (cash thresholds), not a fixed script: teach → let them do it → resume at a threshold.

**Funnel analytics granularity:** splitting "shop" into opened/buying/closing reveals *where* players get confused; Roblox's built-in funnel-events analytics (create.roblox.com/docs/production/analytics/funnel-events) surfaces exact drop-off steps (devs who set funnels up immediately find them; e.g. a step where 20% leave in minutes 1–2); pair with watching a real fresh player session.

### Monetization design

**Two reasons to spend:** players spend to accomplish a goal faster or to show off; "if you're not giving them either of those two things, they won't spend no matter what you do"; monetization problems are usually progression/social problems. A ~9-Robux genuinely-useful early item hooks first purchase; missing skip-for-robux = "you just hate money." **501-Robux trick:** price just above the cheapest Robux bundle (501 vs the 500 pack); buyers either have leftover Robux to spend or must buy the next bundle up. Dev products > gamepasses ("people like when things are consumable... cheaper amounts, more often"); repeatable multiplier chains / consumable currency are the top revenue driver; one whale self-reported 700k+ Robux on one tycoon.

**Ladders and pricing: CONFLICT, both poles supported:** avoid 3–4-Robux microtransactions (feels like shovelware, burns players out); 50–70 Robux passes keep the economy healthy; one "big thing actually worth it" outsells many cheap passes; a few whales > a crowd of tiny purchases (one shop made 1.1M Robux largely off high-value items). Opposite pole, also supported: cheap items maximize conversion, not revenue; a ~9-Robux genuinely-useful early item hooks first purchase and lifts PCR, ~80-Robux mid-game passes, ~199-Robux gamepasses with a real advantage ("cheaper things = higher conversion"; 2x speed for 3 Robux in +1 games). Cheap packs raise payer conversion but destroy ARPPU: a 9-Robux pack lifted PCR to ~3% but ARPPU went negative; fixes: raise the entry pack to ~19, add visible 800+ Robux whale items so 100+ gamepasses don't feel expensive, offer a pricier "pro pack" upsell right after first purchase; whales: 1k–5k Robux bundles, an "All Gamepasses" bundle works. Monetization ladder by wallet size: no-robux players pay with time, low-robux buy cheap dev products, mid buy gamepasses + starter bundles, whales buy huge bundles; cheap dev products drive ~70%+ of monetization volume but drag ARPPU down; plan for both. Offer consumables AND a gamepass for the same benefit; players who won't pay 15 Robux/day for VIP will one-time a 500-Robux gamepass. **CONFLICT:** "few whales beat many tiny purchases" vs "cheap dev products drive ~70% of volume; thousands of small purchases beat a few big spenders"; the pattern is that *volume* comes from cheap items, *profit* from anchoring + whale tiers.

**Placement = intercept points-of-interest:** put purchases where players already look and at moments of need (visible revives + starter pack early; 600–800 Robux characters and 200+ skins for engaged players later); most purchases happen in-match or via on-screen prompts, not the shop page; an 11k-visit game sold nothing from the shop but sold in-match; key offers (2x cash) belong on the main screen, not buried in the shop; dev products for repeatables, gamepasses for permanents (make the starter pack a dev product so it doesn't clutter the store page); purchases convert when *required to keep progressing* ("do they feel the need to spend to progress" test), not as optional bolt-on cosmetics. The game MUST be fun without spending.

**Placement failures run both ways:** purchases hidden in corners or UI that doesn't "pop" sell nothing (good game, zero P2W/popups, 800 CCU → only 6k Robux; dev regretted zero monetization presence), but popups for every gamepass read as pushy and hurt the experience.

**Skip-the-wait ladder:** a 9-Robux dev-product ladder (skips of rising timers, nukes, "kill all") drives PCR so high that chat purchase-spam ("user bought X for 9 rbx") becomes social proof and self-reinforces.

**Reroll/gacha as monetization:** cheap rolls (5/3 Robux), extreme rarities (0.1% outfits), and a social game make cosmetics a flex necessity; a hit analysis: "simple, great mobile UX, the rolling mechanic creates FOMO, every roll is a Robux cash sink." Crates with drop rates out-earn fixed-price skins for cosmetics. Roblox policy: every paid-random outcome must still benefit the player; a max-level player buying a paid spin must receive something of value (cap rewards separately or lock paid spins past a level).

**Don't publicize "most Robux spent" leaderboards**: exposing spenders makes the game look p2w, and p2w perception hurts the non-paying majority's experience.

**Genre-level playbooks:** shooters/combat: robux-purchasable premium crates (gamble Robux → premium skins/effects/exclusive weapons) as the primary driver; round-based co-op horror: consumables and classes.

**UGC collaboration channel:** partner with a UGC group, sell their items in-game, grant buffs to buyers; both earn, and the item doubles as a flex.

### Retention mechanics

**Offline earnings + a welcome-back screen** ("you earned X while away") is the highest-leverage D1/D7 fix in sim-likes; most players don't notice offline accrual unless the game announces it (ESC popup + sound). Tuning: a returning player must visibly progress after 12–24h away or they churn, but overly generous offline earnings create a "log in 5 seconds, collect, quit" loop; cap it (~1 day's worth) and keep active play strictly better. **Counterpoint:** offline rewards prop up D1 but true D7 comes from attachment to the core loop. Offline income only fits games whose earning method is itself passive (plot/garden/base games), not active-earning games

**D7 comes from a loop worth repeating, not rewards:** day-7 logins/swords are a boost, not the reason; games with great D7 are genuinely fun to replay. D2 retention benefits from the "initial commitment + final reward" structure of daily streaks. D7 reward design: make it a gamepass/dev product of the player's choice, exclusive to D7, and make sure players *know* it's exclusive; the boost is worth more than the Robux you'd charge, and Roblox reportedly weights D7 heavily right now.

**Standard retention kit (circulating checklist):** daily login rewards, daily/weekly quests, streak rewards with multipliers, timed free rewards (chests/spins), limited-time events, long-term progression, collection/index systems, achievements, comeback rewards; a purchasable *streak recovery* is more enticing than a plain daily reward. "Time to beat" systems + quests + daily rewards + weekly updates; make the first world maxable in 1–2h; make the very first interaction shorter than later ones; rebirths should visibly notify the player; playtime up, retention follows.

**Event spikes:** admin-abuse events boost D7 and are a proven CCU spike mechanic (a Split-or-Steal squishy game peaked 7k CCU and 1M+ Robux in 72 hours on one; works for non-round games too, with "BALL 2X SPEED" style announcements). But one game ("Greedy Growers") performs strongly without them; long-term retention without artificial event spikes is achievable and possibly more durable.

**Design the comeback interval around real free time:** a major game set a ~24h cooldown/reward cycle deliberately to boost D1; any shorter interval can't guarantee the player has time to return.

**PvP matchmaking psychology:** pair fresh joiners with longer-tenured lower-MMR players so nobody's first match of the day is a ragequit loss; opportunistic design that lifts average playtime.

**Multiplayer lobby tuning:** teleport immediately when the lobby requirement is 1 player; speed up the countdown when nearly full; make guidance visible in first-person (arrows must be visible when the player turns around). If the core loop needs multiple players, low-population servers corrupt retention stats; support solo play from minute one, or launch multiplayer-critical games with higher ad spend + AI/bot fillers for dead servers, plus a friend-invite button with a reward boost.

**Social proof gates retention at low CCU:** with 1–5 players online (ad spend too low), new players see an empty lobby and leave immediately, never to return; don't open ads until you can sustain enough concurrency to not look dead.

**Content-release cadence is life-or-death for anime RPGs:** launching with too little content starts a death spiral (players leave → update too small → players leave again), launch with enough content or not at all.

### Economy and progression

**Playtest every reward's downstream effects:** a new daily-reward system granted a bag-filling item on D1 that made players unable to collect the core resource. Economy hygiene: keep an economy sheet updated with every balance change; playtest on two alts (one pay-to-progress, one free-to-progress); devs now literally ask AI to "mathematically advise prices based on the game's economy."

**Incremental/idle depth = strategic decisions** ("what do I invest in next to maximize profit?"), not just bigger numbers; weave reset layers into the core loop without making it boring or complicated; copying proven mobile-idle loops (AdVenture Capitalist style) still works a decade later. Pacing formula: very fast early progress, then a cap for an hour or two, all while big numbers are visible on screen. Danger case: 1,000/sec → 215M/sec in 1–2 minutes let a tester earn 5 trillion coins and buy every stage.

**Stat hierarchy devs optimize in order:** playtime → D1/D7 retention → bounce rate (or: playthrough rate → first-play bounce → play days per user → playtime per user). Incremental-genre note: D1–D7 runs "orange" naturally because replayability is structurally weak in the genre.

**The feeling of progression beats actual progression speed:** a player who improves slowly but *feels* fast engages; fast-but-feels-slow churns; early semi-rare drops/quick level-ups pull players back the next day; speeding up *early-game* progression specifically fixed a bad bounce rate; the issue wasn't late-game balance but how long new players waited for their first satisfying moment.

**Theme/fantasy is a first-class design decision, not a skin:** two merge games, one about dumplings, one about black holes; the black-hole one has the CCU because "merging black holes" is exciting.

**+1 games work on minimal complexity with maximum depth:** the same action stacked with multipliers/rebirths is disproportionately retentive for Roblox's kid demographic; regurgitated +1 clones still pull 5k CCU.

**3-task framework:** Task A = the main loop, identifiable from title/thumbnail alone; Task B = something that makes Task A easier (the upgrade/funnel layer); Task C = a long-term goal that requires Task A. If a player can't name A from the store page, the store page is broken.

**Ship an infinitely repeatable core loop, add content weekly**: you don't need 20 hours of content at release. A flawed core loop cannot be fixed by updates; a good loop with weak individual systems can.

**"Low-effort clone" is defined by the loop, not the assets:** Oil Empire vs Hack a Business had the same loop, but Hack a Business added a genuinely fun new sell mechanic; that's the flop-clone/success line. Copying itself can be a legitimate first step for *learning* design.

**Trading systems = inflation risk + earnings sink:** the biggest earners (Fortnite; Rivals, the #1 earning game on Roblox) all skip trading entirely.

### UI affordance details

- **Afford errors, don't upsell:** show red error text + error sound instead of a gamepass prompt when the player can't afford something (prevents "am I forced to pay?" confusion and dislikes).
- **Icon dominance:** hotbar/tutorial icons must be visually dominant; players abandoned a game because they never saw they had to press "1" to equip; keep money amounts visible during onboarding.
- **Recurring legibility fixes:** bigger text stroke, fewer simultaneous notifications, one accent gradient per tier, condense overlapping HUD, place merge/action buttons away from walk paths so players don't trigger prompts accidentally.
- **Scaling:** use UI Scale (not Offset) plus UIAspectRatioConstraint so UI scales across devices; mobile-oversized UI is the single most common playtest complaint in the batch.
- **Lighting as psychology:** warm bright lighting reads "safe," darkness reads "danger" (technique from Doors), a cheap way to steer emotion without content changes.

### Positioning, launch, and misc field notes

**Recurring playtest critiques:**
- **Invisible progression is the #1 repeated failure (6+ games):** deep progression exists but is never surfaced (rebirths, workers, unlockable areas the reviewer only found in someone else's base; "99% of your players are not gonna go look at somebody else's base"). Show the cool end-state from the start.
- **Core-verb juice is non-negotiable:** "everything else in the game could suck, but as long as the slingshot feels good... it would do well." If the thing you do 500 times lacks sound/VFX/physical feedback, nothing else matters; money moments especially must be juiced (walk-over pickup with VFX/SFX, not a letdown proximity prompt).
- **The 7-year-old test:** "I'm seven years old, my mom's calling me for dinner": any confusion, unreachable goal, invisible threat, or physics surprise = instant quit ("why can't I jump over this? The game must be bugged. I'm leaving."). Damage sources must be readable at FTUE.
- **One clear input, one clear win condition, high skill ceiling** (Rocket League: drive car, hit ball); multiple simultaneous skill checks + unclear multipliers = "I can't figure out what the strategy is." Best games ~50% luck / 50% skill.
- **Day-30 depth doctrine:** D30 measures genuine fans; "it's hard for people to become fans of something that never demands anything of them." The ultra-simple meta is bad for D30; depth must be baked in (Blade Ball; Creatures of Sonaria has some of the best D30 on the platform), not bolted on.
- **"One more round" is the golden phrase**: hear it from playtesters and you have a hook.
- **Tease-then-payoff / curiosity architecture:** locked boards, visible rares ("you can see somebody next to you with some insane aura, one in a million" = free motivation), "next event in X minutes" in the HUD; loading screens pan the map as ad space for your own game. Anticipation is the named ingredient of sticky loops.
- **Remove, don't restyle:** fix friction by removing the step, not adding UI (rolling-for-crate before opening adds friction without fun; proven pattern is crates rolling by on a conveyor you grab); auto-collects beat per-item E-presses; AFK time accumulates rewards, collection is one juicy sweep.
- **Plot proximity = social proof:** plots spread far apart kill the social feel ("you can't see anybody else's stuff... it really hurts the social element"); visible others' progress is a recommendation in almost every review.

- **Thumbnail→game congruence:** whatever your highest-CTR thumbnail shows, put that exact visual in the game immediately on join; the ad promised it, so the first minute must deliver it; use YouTube playthroughs of similar games to find which upgrade moments players care about. Design the thumbnail as a simple, slightly exaggerated picture of actual gameplay so marketing promise and game never diverge; for anime the winning pattern is progression fantasy (noob becoming strong).
- **Name + genre selection changes measurable ad performance:** CTR jumped 1.4%→3.0% just from selecting a genre and renaming the game; the algorithm may down-rank names it thinks impersonate existing games.
- **Stability is the gatekeeper of retention:** buggy/laggy games make the tuned loop and good thumbnails invisible; one experienced dev's soft-shutdown omission (players kicked on update) damaged his algo standing; a competitor trademarked "War Tycoon"; a legal failure mode devs don't plan for.
- **Kids-specific design cues:** bright colors, constant satisfying sound stimuli on every button, robux offers visible everywhere, progression fast at the start then slowing; "follow marketing and casino tips."
