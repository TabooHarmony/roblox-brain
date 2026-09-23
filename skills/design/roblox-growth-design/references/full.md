# Roblox Growth Design: Full Reference

> Examples, thresholds, and practitioner playbooks are starting hypotheses, not universal laws. Verify platform behavior against the dated sources, adapt to the game and audience, and test before broad rollout.

This reference combines Roblox's published discovery and analytics guidance with original practitioner synthesis. Sections labeled **Official** restate current Creator Hub behavior. Sections labeled **Heuristic** are diagnostic lenses, not claims about the recommendation algorithm. §8.3 practitioner heuristics are original synthesis derived from the submitted draft and operator experience; treat them as experience, not official guidance.

## 1. Operating Model

A game-design diagnosis should connect four layers:

1. **Promise:** what audience the title, icon, thumbnails, and premise attract.
2. **First session:** join reliability, comprehension, time-to-fun, and the first core-loop payoff.
3. **Long-term game:** progression, variety, social value, identity, mastery, and LiveOps.
4. **Business:** transparent products that add player value without damaging trust or the economy.

Do not jump from a weak metric to a feature prescription. A metric is an observation. Several causes can produce the same observation, and one change can move several metrics.

### Evidence hierarchy

Use the strongest available evidence:

1. Roblox Experiments with an adequate minimum detectable effect (MDE), full planned duration, confidence intervals, and stable variants.
2. Cohort or release comparisons with acquisition source, platform, locale, player age, and seasonality controlled where practical.
3. Funnels, session traces, errors, performance reports, economy sources/sinks, and behavioral telemetry.
4. Moderated playtests, player observation, support reports, surveys, and community feedback.
5. Competitor teardown and practitioner intuition.

The lower levels generate hypotheses. They do not prove causation.

### Experiment brief

Before changing the game, write:

- **Observation:** what moved, for which cohort and date range?
- **Hypothesis:** if we change Y because evidence Z, metric X should move.
- **Primary metric:** one measure tied to the hypothesis.
- **Guardrails:** metrics that must not regress, such as errors, D1, economy inflation, payer complaints, accessibility, or mobile frame rate.
- **Exposure:** eligible players, control, variant, rollout, and planned duration.
- **Decision rule:** what confidence and practical effect justify shipping?

Roblox Experiments run for 14–60 days. Do not use first-day results for decisions, stop because a favorable line appears, or claim a causal win without statistical significance. Stop or roll back for safety, severe regressions, broken instrumentation, or invalid exposure. Games below roughly 1,000 daily active users may struggle to detect useful effects; use the dashboard's MDE rather than inventing a universal traffic threshold.

**Experiments mechanics (official).** In-game experiments apply per-player config values; matchmaking experiments test matchmaking configs (only one matchmaking experiment at a time; recommend 100% rollout to avoid isolating players). Implementation:

- Use `ConfigService:GetConfigForPlayerAsync(player)` (not `GetConfigAsync`) to get a player-specific snapshot. `GetValue` on that snapshot enrolls the player; the first call is random, every later call returns the same variant for the experiment duration.
- Call `GetValue` as late as possible. Calling it early enrolls players who never reach the feature you are testing.
- Target enrollment with your own criteria: check the condition (e.g. new player), then enroll only those players (e.g. `racesCompleted == 0`). For cross-session persistence, store the assignment.
- Experiments track all metrics (D1, D7, playtime, ARPU, ARPPU, payer conversion, session time) regardless of the goal metric you pick. Use the Results tab after completion; a metric is significant when its confidence interval does not overlap 0%. Use "Make decision" to promote a variant to the default config.

**Experiments best practices (official):**
- Start with a written cause-and-effect hypothesis.
- Use the MDE to decide if the experiment is worth running; if the MDE is too high (e.g. >100%), statistical significance is unlikely.
- Let experiments run their full duration: the novelty effect can skew early results in and out of significance.
- Don't act without significance. If one metric is up and another down, decide whether the trade-off is worth it.
- Avoid unrelated changes during a running experiment; they can invalidate results. Only run simultaneous experiments if confident they won't interact.
- Use confidence intervals for deep dives; a too-wide interval means the metric may never reach significance.
- Balance experiment results against qualitative player feedback and the product vision. Experiments are probabilities, not certainties.
- Document findings and decisions as a body of knowledge.

### Acquire evidence before diagnosis

Ask for the evidence that actually exists: Creator Dashboard screenshots or exports, cohort windows, release dates, acquisition mix, session recordings, and player feedback. Use Studio or project telemetry for runtime facts when available. State what is missing and never fabricate a metric, cohort, or causal explanation.

### Static project structure: hypothesis only

A static `.rbxl` or `.rbxm` can reveal implementation structures, not player success, usability, retention, conversion, or fun. Use a short handoff:

1. **Observe:** name the structure and evidence boundary.
2. **Question:** translate it into a player-facing question.
3. **Instrument:** choose the smallest success and abandonment events that can answer it.
4. **Test:** use observation, logs, cohorts, or an experiment. Keep static evidence and measured outcomes separate.

## 2. Official Home Recommendations Model

<!-- temporal: 2026-07 -->

Roblox's **Recommended for You** system has two stages:

### Retrieval

The system selects a personalized subset of games using signals such as engagement, retention, and monetization. Sponsored ads, search, charts, friends, teleports, notifications, curation, and external sharing can bring initial players and help a game receive consideration for organic discovery.

### Ranking

The system ranks retrieved candidates for each user. How far organic Home distribution expands depends on users acquired through Recommended for You. Engagement, retention, and monetization from users first acquired through ads, search, friends, social media, or another source do not enter this ranking stage.

This distinction matters:

- external acquisition can create a useful seed cohort and revenue;
- external cohort behavior is still valuable product evidence;
- it does not directly repair weak organic Home-ranking signals.

### Current signal groups

Roblox says signal influence changes over time. Treat this as a dated map, not a permanent formula.

**Most important**

- **Play through rate:** users who play after a Recommended for You impression.
- **First-play bounce rate:** users leaving after a short first play, segmented at under 60 seconds and 61–180 seconds. This is negative.
- **Play days per user:** average unique play days across D1, D2–7, and D8–28 windows.
- **Playtime per user:** capped for this signal at 60 minutes per user, per game, per day.

**Important**

- intentional co-play days per user;
- qualified play sessions per user;
- spend days per user;
- Robux spent per user.

These are per-user averages. Smaller games are not automatically disadvantaged by lower total player counts.

### Explore, expand, and context

Roblox explores a game with cohorts and can expand distribution when those cohorts respond well. Impression changes are also affected by:

- game updates and gameplay changes;
- recommendation-system changes;
- weekly, school-year, summer, and holiday seasonality;
- competing games improving faster;
- audience expansion into less perfectly matched cohorts.

A temporary decline in play through rate can accompany an impression increase. Do not treat every movement as a penalty or secretly changed feature weight.

### Dashboard workflow

In Creator Hub, use **Analytics > Acquisition > Home Recommendations** (also surfaced in the Creator Analytics Overview page):

1. Inspect Home recommendation impressions and plays.
2. Check the most important signals first.
3. If those are stable, inspect co-play, qualified sessions, spend days, and Robux spend.
4. Compare against similar-game benchmarks as rough context only. Benchmark games do not affect ranking.
5. Segment other acquisition sources separately.

<!-- temporal: 2026-08 -->

### 2026-08 RFY direction (Roblox CGO announcement)

Roblox's Chief Growth Officer stated the next Recommended-for-You update (targeted late August / early September 2026) will better recognize long-term player value: games players return to over time, and where players find value in purchases. Source: DevForum announcement, 2026-08-06.

Working guidance from the same post:

- If retention is low, fix core gameplay first: first session clarity, a satisfying core loop, reasons to return, and iteration from feedback and analytics. Monetization alone cannot carry a game players do not keep playing.
- If retention is strong, build sustainable monetization: value players can feel, offers integrated into progression rather than interrupting play, fair and transparent pricing, and continued content investment.
- Both retention and monetization drive Home impressions; games strong in only one still receive recommendations, but games strong in both may get broader distribution.
- Four factors move Home impressions: your own gameplay/updates, platform algorithm changes (announced transparently), seasonality (weekly peaks on Saturdays, summer/holiday/school cycles), and competing games improving faster. A drop while your signals are steady can be competitive, not punitive.

Treat the timing as temporal; re-check the announcement thread for launch status before citing the update as live.

### Practitioner algorithm mechanics (supplementary)

A live-game operator's practical model of how the Home algorithm behaves. Experience-based; not official Roblox guidance.

**Traffic is learned from, but ads are cold traffic.** A new game needs initial traffic before it can be ranked; ads or short-form content (TikTok/YouTube clips) provide it. Ad traffic is the cheapest, least-qualified audience ("cold"): low engagement, low spend, low D1. Roblox uses ad traffic mainly for initial data to gauge the game and its audience. Home-algo traffic is the qualified audience: higher D1, D7, playtime, and spend. Do not panic if launch stats look bad on ad-sourced players.

**Ranking is progressive (unverified hypothesis).** Roblox docs state benchmark games do not affect ranking (see §2 Dashboard workflow). Separately, a practitioner model hypothesizes progressive staging: first against the broad genre (all games with similar loops/mechanics, including adjacent genres), then against "experiences with similar players": games your players also play (Analytics > Acquisition > Home Recommendations > benchmark). Practically, treat that benchmark as the competition that matters: this is where stats usually take a hit relative to the cohort, and where games with better stats steal your players (winner-takes-most). The staging mechanism itself is unconfirmed; do not cite it as a ranking rule.

**Ads money does not buy Home placement.** After initial data collection, ad players' statistics do not feed Home ranking (except some caveats). Running more ads without improving stats does not get you into the Home market; it only buys sponsored placement. The lever is meaningful stat-improving updates: run ads → collect data → find worst stat (D1, D7, playtime) → ship an update that improves it → rerun ads to re-feed data on the improved game. Updates move you up the ranking, not ad spend.

**The 28-day signals window (June 2026).** Roblox's RFY algorithm directly measures longer-term retention across Day 1, Day 2–7, and Day 8–28. The pre-June rolling "7-day window" guidance is stale. Optimize onboarding for D1, early loops for D2–7, and content cadence for D8–28; the skill's official §2 retention windows above match this.

**Beta mode (official feature).** While in Beta mode, your experience is not shown in Home recommendations. Use it to tune metrics with cheap ad traffic before opening to the algorithm, so the first Home exposure has already-optimized stats.

**June 2026 metric change (practitioner reading of official docs).** QPTR was split into **Play-Through Rate** (PTR: % of Home impressions converting to play sessions) and **First-Play Bounce Rate** (negative stat: % of players leaving within 60s; also a 61–180s bucket). D28 is now tracked. Bounce rate is a negative signal, so keep it low; clickbait/mystery-game packages that exploited QPTR are "cooked" because bounce rate now exposes them, and template clones and misleading titles suffer. **Experience detail page CTR** (users who played from detail page / users who viewed it) matters for overall PTR: put your best thumbnails and gameplay description there, not just on the Home tile.

**Game-as-funnel framing.** Think of the game as a funnel: Home impression → detail page view → play session → engagement → retention. Optimize the whole funnel, not just the thumbnail. Find and fix the single biggest bottleneck first (impression, detail page, bounce, D1, D7, D28), not everything at once.

**Diagnose with "rows" not totals.** In the Creator dashboard, slice engagement and funnels by device, platform, locale, and source. A game with good overall tutorial metrics can be terrible on console or mobile, and that friction caps growth. Console players play long and often; don't skip console.

**The 250 highly-engaged-player requirement (2026 platform change).** Games published for all-ages audiences are first available only to age-checked 16+ users until they complete Roblox's Kids/Select evaluation. Confirmation comes from Roblox's real-time multimodal moderation of player engagement (account age, play history, platform spend) verifying that players are genuine, not bots. Roblox's own definition of a highly engaged player: meets requirements on account tenure, playtime in your game, and platform spend, where platform spend means a minimum purchase **anywhere on Roblox in the last 60 days** (they do not need to spend in your game) **and** time spent in your game within that same window. The exact criteria "will evolve"; re-check the kids-and-select doc. Practitioner-reported dynamics (not official docs):

- Ads are served 16+ automatically with Roblox-recommended targeting; you do not need to target 16+ players yourself.
- You can hit Home algorithm placement before clearing the 250 threshold.
- The fastest path is ads for initial traffic, then Home impressions accelerate the count (engaged players come from Home faster than from ads).
- Anecdotal spend: roughly $16/day for ~2 weeks (~$180) hit the threshold from ads alone; one dev saw 190 in 2 weeks from 210K ad visits, then 350 more from 90K Home visits in 5 days.
- Not a huge new cost: similar to what launch ads already cost; commissions are an option if you cannot fund ads.
- **25 vs 250 thresholds (official).** The 250 unique plays by highly engaged players within 60 days is the Kids/Select **evaluation** requirement and applies to games published to all ages. Separately, the refundable **publishing fee** (1,000 R$) is refunded when your game maintains **25** highly engaged players for 60 days; the **expedited review fee** (100,000 R$) is refundable after 90 days if you maintain **25** highly engaged players. Different thresholds, different purposes. Do not conflate them.
- Fast track (official, shipped): the **expedited review fee** (100,000 R$/game, 48-hour review) lets timed launches reach kids/Select before the 250 bar; refundable after 90 days with 25 highly engaged players. See publish-games-and-places doc.

Source: official Roblox docs (kids-and-select, publish-games-and-places) + practitioner reporting, June 2026. Practitioner dynamics are experience-based; re-check the docs for rollout status before citing as live.

## 3. Diagnose Metrics Without Single-Cause Thinking

### Low play through rate or thumbnail QPTR

Likely hypotheses:

- icon or thumbnail is unreadable at actual mobile size;
- the image does not communicate genre, action, fantasy, or tone;
- packaging attracts an audience the game cannot satisfy;
- the premise is too familiar without a clear distinction;
- a recent impression expansion reached a broader cohort.

Evidence to collect:

- Home Recommendation play through rate;
- thumbnail personalization QPTR by thumbnail and winning segment;
- qualified plays and average playtime per active thumbnail;
- mobile and desktop previews;
- mismatch between packaging promise and observed first session.

Do not use generic clickbait. A higher click rate paired with worse bounce or retention is not a win.

### High first-play bounce or weak early session survival

Investigate in this order:

1. join failures, crashes, errors, device memory, frame rate, and long loading;
2. metadata-to-game promise mismatch;
3. unclear controls or goal;
4. mandatory menus, dialogue, character creation, or tutorial before meaningful action;
5. first payoff arriving too late;
6. dead or confusing social spaces;
7. platform-specific input or UI failure.

Instrument milestones such as join complete, player gains control, first meaningful action, first reward, core loop complete, and session exit. Track negative outcomes too, such as a failed fight or blocked purchase prompt.

### Low D1 retention

Roblox points to three broad areas: core loop, first-time user experience, and performance.

Useful hypotheses:

- the core loop is understandable but not enjoyable;
- players enjoy one cycle but see no reason to return;
- onboarding teaches mechanics without communicating purpose;
- progression is invisible or the first goal feels arbitrary;
- starter resources do not let players sample the fun;
- mobile, localization, accessibility, or reliability failures affect a segment.

A brief tutorial or contextual tooltips can help. "No tutorial" is not a rule. Teach only the essentials, get to meaningful play quickly, deliver a joyful first payoff, and preview future progress.

**Practitioner heuristics:**
- Instrument Funnels on every tutorial step to find the exact drop-off step, then fix that step specifically rather than redesigning the whole flow.
- "Show, don't tell" is a strong default for younger audiences: let players learn by doing (plant a seed and watch it grow) rather than reading a text block. Some control schemes still require text; keep it brief and contextual.
- Give a concrete reason to return tomorrow: a crop that finishes growing, a daily reward that escalates, a friend's base to visit.

### Low D7 or D30 retention

Do not reduce this to adding daily rewards. Investigate:

- short-, medium-, and long-term goals;
- progression speed and difficulty;
- content variety and mastery depth;
- collections, identity, customization, or status;
- healthy co-play, parties, guilds, competition, and cooperation;
- endgame and recurring reasons to return;
- LiveOps cadence and whether updates deepen the core loop;
- economy inflation or old content becoming obsolete.

D7 often exposes progression weakness. D30 often exposes endgame, content cadence, social value, or exhaustion. The boundary is not absolute.

**Practitioner heuristics:**
- A week of distinct content or goals gives D7 something to chase: a new zone, a rank, a collectible set, a limited-time event.
- Social-flex features (rare cosmetics, leaderboard placement, "admin abuse"-style novelty items players show off) give returning players something to signal status with.
- Live events on a regular cadence give lapsed players a reason to re-open the game.

### Low average session time

Check whether players reach the fun, then whether the loop sustains interest:

- time to first meaningful choice;
- action density versus waiting and travel;
- reward feedback and goal clarity;
- loop variety and escalating challenge;
- social interaction where it genuinely fits;
- performance degradation in longer sessions;
- natural stopping points and return hooks.

**Practitioner heuristic:** give every core-loop action immediate feedback. A rock hit plays a sound and adds slight camera shake; a coin collected pops and increments a visible counter. SFX + VFX on small actions makes the loop feel alive. Test whether feedback density actually moves your playtime before assuming it will.

Longer is not always better. Respect natural sessions; do not trap players with friction or punish leaving.

### Low payer conversion

Investigate product value and purchase friction:

- can players find and understand the shop?
- is the product useful, expressive, durable, or fun?
- does the product fit the player's current progression?
- are there transparent options at several price points?
- does onboarding show value before asking for payment?
- does the funnel fail before or after a Roblox purchase prompt?

A lower-cost first-purchase offer is one hypothesis, not a default. Measure downstream retention, refund/support sentiment, and economy impact.

**Practitioner heuristics:**
- A very cheap starter pack (under 50 Robux) removes the "first purchase" barrier; the goal is converting a non-payer into a payer, not maximizing that transaction.
- Cheap repeatable consumable developer products (e.g., 19 Robux to double offline earnings on login) build a purchasing habit without requiring a large commitment.

**Official item taxonomy.** Purchasable items are durable (unlimited uses, e.g. skins) or consumable (limited uses, e.g. boosts), and each is enhancement (improves capability: speed, protection, tools, event access) or expression (personalizes: skins, emotes, pets). Know what is being sold, where, and how, and make the purpose of each item legible to the player: a purchasable item should have visible value (Roblox's example: a flashlight in *Doors* that players immediately understand aids exploration). Describe items accurately and truthfully.

**Official shop design.** The shop is the experience's economy information hub, not just a market. Make it:
- **Integrated**: consistent icon/UI, quick in and out without disrupting play;
- **Contextual**: players need surrounding context to judge an item's value; explain items in relation to gameplay and each other (a "Revives" explanation teaches that reviving is core, limited functionality);
- **Inviting**: a destination to linger and browse; rotating or new stock gives players a reason to revisit.

Season passes are a documented delivery vehicle for cadence content (official creator-docs page: season-pass-design), though in practice few Roblox games run a classic paid-track pass. A good season pass: follows shop best practices, offers **free and premium tiers** (free keeps non-payers earning; premium is a superset rewarding payers), has **attractive rewards** previewed and tied to the core loop, a **manageable timeframe** (reward spacing relative to average session time; short and long missions; clearly communicated XP levels), and clear remaining-time communication.

### Low ARPPU or ARPDAU

Low ARPPU can mean the catalog lacks depth for engaged payers, but it can also reflect audience, regional pricing, product mix, or a healthy low-pressure economy. Consider durable and consumable options, seasonal products, and meaningful catalog variety.

Always inspect ARPDAU and payer concentration. High ARPPU with low ARPDAU can mean revenue depends on a narrow subset. Do not design around "whales" or use coercive scarcity, deceptive odds, pay-to-escape friction, or manipulative loss aversion.

**Practitioner heuristic:** tiered pricing ("small / medium / large fries") gives engaged payers somewhere to go: a basic pack, a pro pack, and an expensive overpowered pack. The expensive tier exists for players who want to spend; the cheap tiers keep the majority comfortable. Test whether your audience actually has a high-end segment before building for one.

### Declining impressions

Do not assume a shadow penalty. Check:

- Home signal changes by their documented priority;
- recent updates and regression dates;
- acquisition-source mix;
- seasonality;
- broader-cohort exploration;
- competing games and changing audience preferences;
- a Creator Dashboard reduced-exposure banner.

## 4. Positioning and Idea Validation

### The purple-ocean lens

**Heuristic:** seek proven demand with a clear twist rather than a pure clone or an idea with no demonstrated audience.

Use it as a research lens:

1. **Demand:** are players already seeking this fantasy, mechanic, or genre?
2. **Supply:** which games serve it, how concentrated is the audience, and what do reviews or communities dislike?
3. **Difference:** can a player explain this version's distinction in one sentence?
4. **Roblox fit:** does it benefit from avatars, co-play, user identity, short sessions, touch controls, or social graph?
5. **Production fit:** can this team deliver the content, moderation, economy, and update cadence?
6. **Evidence:** what cheap prototype or packaging test could falsify the premise?

Treat third-party estimates as directional. Public CCU, favorites, visits, review activity, social views, Steam wishlists, and Google Trends measure different populations and can be gamed or misread.

### Trend lifecycle

**Heuristic:** Roblox trends tend to move through three phases:

1. **First to market:** an original concept captures initial demand with little competition.
2. **Saturation:** clones and templates flood in; the player base disperses; most copies die.
3. **Mutation:** survivors re-package with a new title, custom thumbnail, or altered core loop. Straight copies of the original's title and thumbnail format fail and can trigger metadata penalties (§6).

If you are entering a trend in phase 2 or 3, a straight clone is the worst position. You need a meaningful twist or an underserved sub-audience.

### Off-platform demand signals

**Heuristic:** demand proven elsewhere de-risks a Roblox launch:

- Indie games with hundreds of thousands of Steam wishlists or millions of web-game plays show proven desire for the core concept.
- Gameplay videos pulling millions of views, especially with younger audiences, predict the concept can explode on Roblox.
- Being the first to bring a highly demanded fantasy to Roblox in a polished way is a strong entry point.

Check the Roblox side too: search for the concept's keywords. Is it actually done well? A theme saturated with basic RP/sims (airports, firefighters) can host a different genre entirely (action-checkpoint, extraction shooter). That gap is the opportunity.

### Premise checks

A useful concept should answer:

- What does the player repeatedly do?
- What fantasy or identity does that action serve?
- What changes after each cycle?
- Why is this better with other players?
- What can be shown honestly in one icon and one thumbnail?
- What remains fun without spending?
- What production burden grows with success?

### What makes a game take off (practitioner checklist)

A live-game operator's five things that make a Roblox game likely to go viral and keep players. Experience-based; not official Roblox guidance.

1. **An idea a kid can picture before bed.** The concept should be something a player would imagine falling asleep to: "a hospital run by animals" (Animal Hospital), "toys that live their own life" (Toy Story), "a city run by animals" (Zootopia). If the packaged title + thumbnail makes a player on the Home page unable to resist clicking, idea works. Test a concept by asking what fantasy the player is fulfilling, not just what the mechanic is.
2. **Great onboarding.** Not a tutorial that drags: get players emotionally invested in the *why* of their actions (title-sequence world-building, cutscenes showing a clearly felt threat), introduce one mechanic at a time, use level design to communicate danger/goals without text, and keep UI minimal during onboarding (Sell Lemons: no UI, fast progression, one mechanic at a time).
3. **Socialization as part of the core loop.** Make the game 10x more fun with friends so friends invite friends (the word-of-mouth flywheel: kids show each other at school/bus). Leaderboards add the social flex; cosmetics and visible progress create FOMO ("that kid is zooming past me"). Even simple social elements beat a great solo incremental with zero interaction.
4. **Simple mechanics with tons of depth.** One obvious mechanic (voxel building, boat building, role-play) that yields near-infinite player expression and session variety ("every session is different": build a new plane, new role, new PvP run). The mechanic must stay easy and frictionless on **mobile** first; on-mobile clunk caps growth even when desktop is fine.
5. **Clippable / strong community.** Design for content creators: visualize what a YouTuber/TikToker would clip from your game, and make those moments frequent and obvious. Community-created content (build showcases, unique hiding spots, crazy plays) compounds virality; watch the moments creators actually include and double down on them. A strong community keeps a game at 8–9K CCU for years.

**Study top games, copy functionality not style.** Play successful games in the genre (especially on mobile and console), understand *why* their onboarding/funnel/social choices work, and copy the function, not the aesthetic one-for-one. Diagnose toy friction by running your own game with a fresh account and watching where a new player gets stuck.

### Production playbook for fast shipping (supplementary)

A live-game operator's process for shipping quality fast, from a producer who runs a two-man team. Experience-based; not official Roblox guidance. Distilled from practitioner video on pumping out high-quality Roblox games quickly.

- **Execution is the bottleneck, not ideas.** Ideas are cheap and everywhere; the scarce resource is reliable execution. A big team is not a flex; top studios run lean (4-person or even 2-person) teams.
- **Get the MVP core loop done first.** Scope a minimal viable product (core loop only) so you can playtest whether the game is fun before investing in the full vision. Use AI (e.g., Claude) to prototype with basic parts and free models before hiring any dev.
- **The game design document is the contract.** A GDD (what players do, leveling, economy, progression) doubles as the statement of work for the programmer. Turn it into per-role Trello columns and actionable tasks per system.
- **Sequence the build: art/UI/models first, programmer second.** Programmers are more productive in a populated workspace; delivering builds/models/UI before scripting keeps execution fast.
- **Communicate visually and asynchronously.** Use recorded video (Loom-style), screenshots, and references to existing games rather than long text; most "wrong work" is a communication gap, not a skill gap. Prototype small ideas with AI first to avoid paid-dev round-trips.
- **Hire T-shaped people.** One person who does programming + UI, or building + modeling + animation, beats a bigger brittle team. Same time zone matters for fast iteration.
- **Reputation and vetting beat money.** In the Roblox talent pool (often young), trust decides everything: hire via Twitter/YouTube presence, prefer paid-upon-completion (never pay in full up front; that kills delivery), always sign a contract, make a new contract for new scope, and don't sneak unagreed work into scope mid-project (it breeds resentment and slows the team).

### Core-loop design

Write the loop as:

> **Action → feedback/reward → progression choice → more expressive or demanding action**

Audit:

- Is the repeated action itself enjoyable?
- Is feedback immediate and readable without relying only on sound, color, or motion?
- Does progression create decisions, not only larger numbers?
- Can a new player complete a meaningful cycle quickly?
- Can the primary action be expressed well on touch, gamepad, and keyboard/mouse, or does one platform require a different interaction model?
- Does the loop remain legible on lower-end devices?
- Does co-play improve the experience rather than merely add bodies?

Prototype the uncertain mechanic before building a large content shell. Prioritize from observed player behavior and the cost of being wrong.

**Practitioner heuristic (80/20):** build roughly 80% from proven mechanics, UI, and progression patterns players are already trained on (core loops, upgrade systems, map layouts from top games in the genre), and spend roughly 20% of your differentiation budget on the theme, fantasy, or twist. The ratio is a starting lens, not a law: a genuinely novel mechanic may need more invention, and a reskin may need less. The point is that familiarity lowers the comprehension barrier while novelty supplies the reason to click.

### Launch, sponsoring, and idea selection (practitioner, 2026-09)

Experience-based launch, sponsoring, idea-validation, and business notes. Not official Roblox guidance.

**Sponsoring checklist.** How to run launch sponsors without burning money or misreading data.

*Do:*
- Run sponsors at least 3–4 days before judging them.
- Keep sponsors consistent: swapping in new sponsors resets the learning period and makes CCU bounce around.
- Spend a steady, modest amount (~16 ad credits/day) instead of dumping a ton of money in. Total spend doesn't change the end result, only how fast you get there.
- Wait for 10k+ visits before trusting playtime or session data; below that it's basically noise.
- Work the game page itself (title, thumbnail, description): good CTR is worthless if viewers don't convert to plays.
- Add a code in the description to give people a reason to play: it converts better.
- Test an all-caps or punchier title if conversion seems weak.
- Be patient and methodical; the whole process is a waiting game.

*Don't:*
- Don't keep launching new sponsors: every new one relearns from scratch, which causes CCU to dip and stay volatile.
- Don't clickbait the title or thumbnail: clicks that never turn into qualified plays actually hurt with the algo.
- Don't trust early playtime data at low visit counts.
- Don't assume more money buys a better outcome: it speeds up the timeline, it doesn't raise the ceiling.
- Don't let cost per play (CPP) sit at 0.005+ and call it good enough; under ~0.005 is the target, and there's always room to improve even when CTR looks fine.
- Don't overhaul everything in one shot: change one thing at a time so you can tell what moved the needle.
- Don't let one bad-looking metric make you panic-pull the plug: CCU, playtime, and retention only really mean something once the game has scale.

**Targeted-stat updates.** A good update rhythm: pick one stat per update (e.g. to raise session time, add activity rewards that unlock after a set time in-game), ship it, then monitor that stat after the update. Combined with the funnel framing in §2, this keeps cause and effect legible.

**Idea validation and execution.** How to choose and pressure-test ideas before committing months.

- **An idea's job is to make design easier.** Grow a Garden came from offline growth: plants made "something grows while you are away" clearer than a rock would. If an idea creates design problems, pivot.
- **Match the idea to the team's history.** A simulator team should make simulator-style ideas; a team without FPS experience should not jump into a zombie shooter; solo devs start simple and scale from past work.
- **Stress-test with the core loop only.** Build just the core loop, make it satisfying, then test with people who already like that niche; feedback from outside the niche misleads.
- **Release fast, update weekly.** Don't spend two months on one unproven game; learn from failure and iterate on quality of life. Simple ideas are harder to think of than complex ones but better for learning.
- **Every original game is an iteration.** Fast teams can chase trends; slow teams should bet on originality, which is harder to copy.
- **Tie the comeback reason to the real goal,** not just cash or daily rewards.
- **The team must enjoy the game itself.** If nobody wants to play (or AFK) before launch, it isn't strong enough.

**Business and deal notes.**

- **Clip value test:** show the game to YouTubers and ask whether funny or shareable moments happen naturally. If it produces Shorts/Reels/TikTok material, creators may promote it for free, and you can clip it yourself.
- **YouTube traffic inflates stats:** viewers already understand the game from watching someone else learn it, so session time and retention look stronger than they are. Home recommendation stats matter more for judging true platform growth (cf. §2's external-traffic caveat).
- **Deal structure:** pay on completion to lower scam risk; contracts for equity, with equity matching real contribution; define in the contract what equity holders keep doing after launch.
- **Selling a game:** ask whether the buyer will scale it or kill it. If they'll kill it, selling more of it may make sense; if they can scale it, sell as little percentage as possible. Avoid buyers who only collect near-term revenue.
- **Outsource creative only if it beats your own stats**: outsourced thumbnails that underperform your own work are a downgrade, though hiring makes sense when you lack the skill.

### Practitioner stats-and-launch realism (supplementary, 2026-09)

Experience-based, not official Roblox guidance. Complements the sponsoring checklist above with the unglamorous parts.

- **Onboarding friction budget**: every required input between loading screen and gameplay loses players (welcome popups, unskippable intros, team/save-slot selects, fancy menus). First-session UI should be one bouncing button with an arrow and circle cutout, and even then ~5% of players won't click it. Use world beams, UI cutouts, finger pointers; auto-choose everything optional and drop the player into the game. Instrument every onboarding step with `AnalyticsService` funnels; first-time results are always a surprise.
- **Split ad campaigns by platform**: desktop and mobile CTR differ enough that combined campaigns produce useless data. Targeted low spend (5 credits/day with platform/gender/genre targeting) can beat larger untargeted spend (10–15/day). Match creative to audience (don't promote a cutesy dress-up game to boys).
- **Algo "biting" is visible before players arrive**: watch impressions-by-thumbnail (Places → Place → Thumbnails) while running launch ads; first impressions/hour show up before CCU moves. Expect a bumpy ride: spikes to thousands then 0. Don't touch thumbnails or stop ads mid-spike.
- **Paid vs organic gap**: ad-sourced playtime can be less than half of Home-sourced (observed: 8 min from ads vs 19 min from Home on one game). Check Acquisition → New User Funnel → Engagement by source to preview organic stats before turning ads off.
- **Console is a cheap niche**: small audience but often longer playtimes (sometimes overtakes desktop) and cheaper ads. Worth a gamepad-comfort pass.
- **Low-CCU stats are noise**: one random player can triple daily playtime; D1 can swing from ~0% to 10%+ day to day. One dev's "3% D1 is a lost cause" games now sit at 9–13%. Learn your own baseline; don't make kill/keep decisions on small samples, and don't retire daily rewards because D1 spiked once.
- **Don't trust The Spike**: a 400-CCU peak can decay to 1–2 despite dozens of updates and thumbnail tests. The algo gives and takes.
- **Negative ratings are unavoidable**: kids downrate for bugs, performance, UI, obvious AI use, niche gameplay, difficulty. Counters: volume of happy players (e.g. like-and-join-the-group rewards) or a flawless game: nothing else.
- **Make feedback frictionless**: custom feedback forms persisted to a DataStore, with the button surfaced at decision popups (rebirth confirmation, level completion). Negative feedback beats friend praise; decode trashtalk for its signal (boring, confusing, too hard, too easy).
- **Multiplayer games need singleplayer fallbacks**: coop/versus games die fast when CCU can't fill servers, and they need higher ad spend. "Waiting for more players" screens kill joins. Warmup modes, fun tutorials, bots, and lobby minigames help.
- **Streaming can beat shorts** (TikTok live especially): viewers want to play with the developer, stay longer, and purchase to support (if the game looks exciting on stream). Dev-streams also work. Game must be visually interesting; that's the bar.
- **Shorts/TikTok mechanics**: strong hook in the first seconds; no links (algo may penalize as spam), game name only (bait comments asking for it); conversion from views to plays is tiny but pre-qualified; needs 1–2 weeks of sustained posting. If nobody watches and plays, that's hook feedback, not platform failure.
- **Mindset**: your game dies when you decide it's dead. Most games are a long fight for every active player, not a front-page week. But know when to quit and re-ship (see §4 trend-lifecycle: failed games are usually re-shipped as new games, not revived).

## 5. First-Time User Experience

Design for **play-first teaching**, not "players never read." Some controls and systems require text. Make instruction brief, contextual, localized, and accessible.

Roblox's retention guidance recommends reaching the fun within about five minutes. Treat that as a diagnostic starting point, not permission to rush a complex control scheme.

A first-session sequence can be:

1. safe arrival with the game responsive;
2. one obvious action and immediate feedback;
3. one small choice that expresses agency;
4. first core-loop completion;
5. a joyful payoff;
6. visible next goals;
7. optional deeper explanation after motivation exists.

**Official onboarding mechanics.** The FTUE succeeds on two metrics: D1 retention and onboarding goals (teaching essentials, getting to fun quickly, leaving players wanting more). Practical levers:

- **Player XP-based leveling**: keep early-level XP thresholds low so players level up fast and feel progression immediately. Tune thresholds with Configs in real time without shipping an update.
- **Starter items and currency**: free equipment/soft currency lets players sample utility or expression early. Find the balance with Experiments (gift different starting amounts), then push the winner as a Config.
- **Goals and moments of joy**: surface short/mid/long-term goals in highly visible places (skill trees, season passes, quests, collections); end onboarding with an intentionally designed moment of joy (rewards, delightful animations, celebratory VFX).
- **Funnel instrumentation**: list core-loop steps, track completion rate per step (with special in-game items as step markers), track negative outcomes (lost fights, blocked purchases), and fix the biggest drop-off. Target the funnel with Experiments on specific steps (shorter dialogue vs guided arrow) to get causal answers.
- **Social FTUE**: if the game is social-first, use Experiments on matchmaking parameters during FTUE to find groupings that improve long-term engagement.

Observe representative players rather than relying on teammates who know the game. When testing with minors, use appropriate consent, privacy, safeguarding, and moderated research practices. Do not collect unnecessary personal data.

**Practitioner heuristics for mobile friction:**
- Mobile UX fails by "death by a thousand cuts": each tiny friction point is tolerable alone but they accumulate until the player quits.
- Hand the game to a target-demo player on a phone or tablet, explain nothing, and watch. UX failures, stuck points, and frustrations surface immediately.
- Remove tap tedium: if upgrading takes 500 taps, add "Buy 100" / "Max Buy" buttons on the HUD.
- Keep maps compact and action-dense. Excessive walking between points of interest kills engagement, especially on mobile. Proven compact layouts (floating-island style, hub-and-spoke) get players into the action faster.

### Accessibility and device coverage

At minimum check:

- touch targets and thumb reach;
- gamepad focus and keyboard/mouse controls;
- readable text at supported text sizes;
- sufficient contrast and symbols in addition to color;
- captions or visual cues for sound-only information;
- reduced-motion behavior;
- localization expansion and bidirectional layout where relevant;
- lower-end mobile memory, thermal load, frame rate, and network conditions.

Cross-reference `roblox-input`, `roblox-gui`, `roblox-localization`, `roblox-performance`, `roblox-audio`, and `roblox-animation-vfx` for implementation.

## 6. Packaging and Metadata

### Official requirements and behavior

Use accurate, original metadata. Roblox can reduce exposure for:

- giveaway-led metadata;
- mismatched metadata and gameplay;
- non-unique games with metadata and place files closely resembling existing games.

Quality status is reclassified with updates. Reduced-exposure experiences receive a Creator Dashboard banner that updates daily.

Icons should be square and at least 512×512. Thumbnails should be 16:9 and ideally 1920×1080. Preview both at small mobile sizes. Keep essential details away from areas Roblox overlays with metadata.

### Thumbnail personalization

For Home personalization:

1. Activate 2–5 accurate thumbnails.
2. Roblox initially explores them across users, then allocates more impressions to winners by segment while retaining exploration traffic.
3. Inspect impressions, qualified plays, average playtime, QPTR, and winning segment.
4. Keep multiple thumbnails active so personalization can adapt.
5. Test new thumbnails around a major game or content update, then avoid changing them again until the next update.

QPTR here means qualified plays divided by Home recommendation impressions. The broader Discovery signal table separately calls its top conversion signal **play through rate**. Do not silently treat every dashboard's denominator or qualification rules as identical.

### Practitioner creative heuristics

Use these as starting points, not ranking rules:

- communicate one dominant fantasy or action;
- prioritize subject, action, emotion, and contrast over clutter;
- make the image understandable at actual display size;
- use honest in-game content and visual fidelity;
- avoid tiny text and UI-like thumbnail layouts;
- use title wording for searchable clarity and differentiation, not keyword stuffing;
- test whether the package attracts players who actually enjoy the first session.

**Design specifics (heuristic):**
- Simple backgrounds. Clutter kills CTR.
- 1–2 characters (3 only if the composition demands it; more is visual noise).
- High color contrast: bright subjects popping off the background (yellow character on clear blue sky).
- Exaggerated, instantly readable emotions: manic evil smile, crying/stressed face, troll face.
- Tease a mechanic over the title: text like "Steal at Night" or "Cure the Survivors" gives context and intrigue; the game's name alone usually does not.

**Proven thumbnail formats (heuristic):**
1. **Before & after:** noob vs. pro, cheap vs. expensive split. Works for tycoons and progression games.
2. **First-person perspective:** viewer inside the action. Works for PVP, shooters, RP.
3. **Two-character scene:** conflict or interaction, someone getting outplayed.
4. **One character + action:** maximally readable and simple.
5. **Entirely new concept:** unique to your game's mechanic; highest risk, highest differentiation.

**Creation workflow (heuristic):**
1. Research genre tropes in top games of the niche (e.g., hacker games: masks, green binary, brand rivalries).
2. Rough mockup in a free tool (basic shapes, clip art, text) to fix the layout before committing to detail.
3. Generate or commission from the mockup with a highly specific scene prompt.
4. Iterate with explicit direction ("remove the clouds", "make text larger", "flip the character").
5. Simplify for mobile first. Detailed desktop thumbnails are often unreadable on phones.

**Testing:** A/B test 2–3 thumbnails per week. CTR naturally decays as impressions accumulate, so keep rotating fresh, readable thumbnails. Test around major game or content updates, then let the winner stabilize.

Optional tools:

- [qptr.io](https://qptr.io) previews an icon or thumbnail beside simulated neighbors. It does not measure live Roblox performance.
- [Creator Exchange](https://creatorexchange.io) offers directional market and game estimates. It is not an official Roblox analytics source.

## 7. Monetization With Trust

Good monetization exposes clear value to willing players while the free core remains enjoyable.

Design principles:

- transparent storefront and purchase result;
- several price points and a mix of durable and consumable value;
- no hard-coded Robux prices when Managed Pricing can change them;
- regional pricing where appropriate;
- no deceptive odds, false urgency, disguised purchase buttons, repeated interruption, or punishment for declining;
- no sale that corrupts competitive integrity unless the game's promise clearly supports it;
- server-authoritative granting and idempotent receipt handling.

Price optimization requires enough transactions for statistically useful data. Roblox says it usually needs at least 60,000 transactions over the preceding 30 days. Smaller games should use qualitative value research and carefully scoped experiments rather than pretending a tiny sample proves an optimal price.

When the economy or monetization health is in question, load `roblox-analytics` for the telemetry-first decision layer: sink/source ratio, inflation, whale concentration, and the diagnose-with-telemetry workflow. Telemetry tells you what broke; the design fix is yours.

Cross-reference `roblox-monetization`, `roblox-security`, and `roblox-data` before implementing purchases.

### Practitioner monetization mental model (supplementary)

A live-game operator's playbook for dev products, from a game that grew revenue ~3x on the same player base. Experience-based; not official Roblox guidance.

**Data first, then hypothesize.** Before touching products, sort dev product sales descending and identify the best seller. Form a hypothesis for the next product from data and observed behavior, ship it, check results (revenue AND side effects), keep or revert. Do not design products on instinct.

**Watch live play, not just numbers.** Your game won't always be played as intended: operators found players running an active game AFK (and getting robbed in PvP), which surfaced a real friction point. Combine dashboard data with observation and player feedback (Creator Dashboard > audience feedback) to find the pains worth solving.

**Convert valuable game passes into consumables.** 2x offline earnings, 2x cash, and similar high-value boosts are usually implemented as one-time game passes, but that caps the **7-day spend days per user** stat (number of unique days in 7 days a user spends Robux in your experience). Consumables (repeat-purchase dev products, like consumer packaged goods: toothpaste, supplements) pump that stat: players buy a 24-hour lock today, tomorrow, the next day. A consumable that solves a real friction point almost always becomes the top seller. Experiment with consumables aggressively.

**Products should be must-haves that solve a pain, not nice-to-haves.** Best sellers are pain-relievers:
- effort grind → buy speed/cash (pain of effort);
- losing progress while AFK → base lock / protection (pain of safety);
- fear of missing out → 2x offline earnings (pain of missing out on gains);
- status/looks → limited-stock cosmetics (pain of "looking like a casual"). Limiteds with real scarcity (only 100 for sale) outsell unlimited cosmetics.

**Place products at points of interest (POI), not just in the HUD.** Put physical dev products where foot traffic is highest (e.g., at the base entrance the player walks through constantly). Swap the paid product with the free one so the paid version sits at the highest-traffic spot. In addition: time the prompt at the decision moment (offer 2x offline earnings right when the player walks over the collect point; cheap 19-Robux upsell).

**Improve purchase pathways.** Multiple ways to reach the shop increase sales: HUD shop icon, a "+" cash button next to the currency display, and (after 3 failed buy attempts) an automatic cash-shop popup. First two "not enough money" errors show a soft error; on the third, open the shop. Keep the popup non-intrusive (cap per session). UI and physical in-world pickups both count as pathways.

**Check for collateral damage.** After shipping a product, check it didn't wreck other stats: playtime, D1, D7, session time, first-time user experience, and the in-game economy (over-priced currency or 2x boosts can destroy progression balance). Economy-destroying prices (e.g., $1B cash for 9 Robux) cook the game long-term.

## 8. Social Design and LiveOps

Social features are not automatically retention features. Define the interaction:

- collaboration, competition, spectatorship, gifting, trading, parties, guilds, or shared creation;
- how solo and new players avoid exclusion;
- moderation and abuse controls;
- scam-resistant trade and gift flows, reporting, and escalation;
- mandatory filtering for player-authored text and the review burden of uploaded content;
- griefing controls that preserve legitimate competition;
- whether server size and matchmaking support the intended behavior;
- how co-play is measured without manufacturing friction.

### 8.1 LiveOps taxonomy (official)

LiveOps is the post-launch support that maintains engagement. Four update types, in increasing scope:

1. **Content cadence**: regular release of fresh content (weekly to monthly), building on existing systems: limited-time events, seasonal content, UGC. Cheap to produce, maintains engagement between major updates, concentrates programming resources on the next major.
2. **Major updates**: new or expanded systems that change gameplay: social systems (guilds, trading), competitive systems (PVP, leaderboards, tournaments), collections/achievements, large live events aimed at re-engaging lapsed players. Months of development; retain existing players and attract new ones.
3. **Quality-of-life improvements**: polish: UI layouts, UX flows, aesthetic refreshes, accessibility, performance. Can have outsized goodwill impact; gather player feedback on frustrations and time sinks.
4. **Bug fixes**: implementation issues. Prioritize by severity (impact on gameplay), effort, and number of players affected.

Blend all four; cadence keeps the game fresh, majors evolve it, QoL buys goodwill, bug fixes preserve trust. The precise cadence depends on the team's capability and the game's systems; balance player desires against what can be reliably delivered.

**Content cadence sustainability (official).** Keep cadence releases cheap and maintainable:

- **Choose correct content**: items, furniture, pets, vehicles, weapons, maps, quests are predominantly art-based, requiring little programming or design. Simple variants (color changes) are ideal. Themed releases (seasonal, holiday, around a central concept) unlock cross-item creativity. Use analytics and player feedback to target high-value content.
- **Manage scope**: spend under three weeks of effort per cadence release so the schedule stays rapid and leaves room for other LiveOps. Adding new systems to support a release turns cadence into an expansion and becomes unsustainable.
- **Establish a routine**: a regular cadence (common: every two weeks to a month) makes players check back and anticipate releases; it also makes the team more efficient with practice.
- **Prioritize sustainability**: content should not be immediately consumable by most players, or the team is forced to over-release. Deliver sustainably through: progression (add permanent content near endgame where veterans run out of objectives), limited-time content (available to all for an event; earn via quests/milestones/event currency, balanced so it takes most players weeks to exhaust), and season passes (the standard delivery vehicle: quest-based, with free and premium tiers).

### 8.2 Planning (official)

- **KPIs**: pick the metric you want to impact (e.g. daily active users) before designing the update. Events usually move several KPIs at once.
- **Player actions**: define the intended player actions during the event and the KPIs those actions influence.
- **Economy impact**: increased interaction can change earning/spending patterns. Design rewards so they don't damage the economy (e.g. a fishing tournament that exposes a currency-earning loop must not hand out rewards that break price levels).
- **Communication**: plan external (social, community) and internal (popups, UI, lobby) communication, and its timing. Advance notice lets players schedule their return; waiting too long risks being overlooked.
- **Monitor and analyze**: track currency sources/sinks; make data timely (hourly or same-day checks during launch), comparable (compare event weeks to pre/post event weeks), and use it to confirm the event is hitting goals without granting too much.

### 8.3 Practitioner heuristics (supplementary)

From a practitioner with a live 21K CCU game (~$131K/mo). Experience, not official guidance:

- **Patch vs update track**: patches (bugs, exploits, nerfs/buffs, monetization tweaks) ship daily if needed; never wait for a weekly window. Updates ship weekly/bi-weekly and each names its metric before work starts.
- **Three data sources**: qualitative (Discord bug reports, community forum, Creator Dashboard Feedback tab AI summary), quantitative (dashboard analytics), competitor research (mine your core audience's server tags and past games to find what they play beyond the recommendation feed).
- **Core audience**: dedicated playtesters who out-play you. Plan and playtest with them, but discern: they are players, not game designers. The player is usually right, not always.
- **Cadence**: launch, plan next same day, assign next day, build midweek, playtest internal then core on Friday, launch Saturday.
- **Dos/don'ts**: listen and talk to your audience; test before launch; watch small YouTubers play (sort by posted today, low views) to find friction; prefer internal team over big studio when resources allow; don't prioritize monetization over gameplay (pay-to-win kills); don't do last-second updates; don't please everyone or implement every suggestion (can fry the economy); don't get lazy ("we made it, don't need to touch it" kills games); don't push updates that create no engagement.
- **Sunk cost fallacy**: players keep playing due to invested time/money/effort; design updates that deepen emotional investment in progress (e.g. build mode where new players build safely before facing pressure).
- **Retention lens**: Roblox discovery accounts are D28: continuous content keeps the algorithm feeding fresh engagement.

LiveOps should complement or deepen the core loop. For each event or update, define:

- target audience and KPI;
- intended player actions;
- economy sources, sinks, and reward impact;
- communication before and during the event;
- hourly health checks during launch;
- comparison with pre-event and post-event periods;
- what remains after the temporary event ends.

Do not use event spikes as proof of durable retention. Compare later cohorts and ordinary weeks.

## 9. Audit Workflow

When asked to audit a Roblox game:

### Step 1: Request evidence

Ask for what exists, not an idealized dashboard dump:

- game link and intended audience;
- Home recommendation impressions, play through, bounce, play days, playtime, and important signals;
- acquisition by source;
- first-session retention and onboarding funnel;
- D1, D7, and D30 cohorts;
- session time and playtime;
- payer conversion, ARPDAU, ARPPU, products, and economy health;
- device, locale, and country/region breakdowns;
- errors, crashes, frame rate, and recent update dates;
- thumbnails, icon, title, description, and reduced-exposure banner;
- player feedback and observed sessions.

### Step 2: Establish the baseline

Separate facts, inferences, and unknowns. Mark immature D7/D30 cohorts. Note seasonality, traffic-source changes, events, ads, and releases.

### Step 3: Find the narrowest broken transition

Examples:

- impression → play;
- join → player control;
- control → first meaningful action;
- action → first reward;
- reward → core-loop completion;
- first session → return;
- retained player → value-aware shop visit;
- purchase intent → completed purchase.

### Step 4: Prioritize

Use a simple evidence-weighted score:

> **Priority = expected player impact × confidence × reach ÷ cost and risk**

Do not fabricate precision. A qualitative High/Medium/Low score is often more honest.

### Step 5: Produce an experiment backlog

For each recommendation include:

- evidence and uncertainty;
- hypothesis;
- smallest viable change;
- primary metric and guardrails;
- eligible cohort and segmentation;
- instrumentation required;
- expected decision date;
- rollback trigger.

### Step 6: Preserve the game's identity

Optimization is not a license to turn every game into the same simulator loop. Protect the intended fantasy, audience, tone, accessibility, and creative distinction. Reject metric gains that depend on misleading acquisition or damaged player trust.

## 10. Output Format

Use this structure for a game-design diagnosis:

1. **Verdict:** the highest-leverage constraint.
2. **Evidence:** verified facts and the source/date range.
3. **Unknowns:** missing evidence that could change the diagnosis.
4. **Hypotheses:** ranked, not stated as facts.
5. **Next experiment:** one smallest interpretable intervention.
6. **Metrics:** primary outcome, counter-metrics, and decision rule.
7. **Implementation routing:** which Roblox Brain skills are needed.
8. **Later backlog:** useful work deliberately excluded from the first test.

## 11. Community benchmarks and launch observations

<!-- temporal: 2026-09 -->

These are experience-based claims about a live, shifting platform, not official Roblox guidance. Cross-check against current Creator Hub docs before betting a launch on any number. **CONFLICT** marks direct disagreements between reports.

### 11.1 Benchmarks

#### Revenue vs CCU

- Revenue-per-CCU varies ~10–30x by game quality/monetization; CCU is a weak predictor of earnings. Data points: 100 CCU → 300 R$/day (weak tower game) vs ~70 CCU → ~$2k/month (well-monetized); 500 CCU can out-earn 1k–1.5k CCU; 20 CCU → 30k R$/72h (heavily monetized); 130–180 CCU → 390–440k R$/72h; 100 CCU → 20k/72h called "terribly monetized"; 1.5k CCU → 7–8k R$/day; a 12k-CCU-peak game made $3 (no monetization); a "dead" 10-CCU game still made 1–3k R$/day; one player-only-CCU roleplay game averaged 34 CCU with many dislikes and still made ~$3k in its first beta week. One dev claimed CCU only "starts to matter" past ~30k; Blade Ball at 30k CCU reportedly out-earns Blox Fruits at 300k CCU (54 pages of dev products).
- Market-rate bands cited for planning: a 2,500-CCU game makes roughly $25k–55k/month median, hyper-monetized outliers $70k+; ~500 CCU with consistent playerbase and good monetization → $50–80k USD/year, others report thousands/month at 300–600 CCU; $30k/mo per 1k CCU is the *high end*, only niche sticky-audience games reach it; one dev's friend made $200k/month consistently off 5k CCU; 10k CCU up to ~$800k+/month, 500k CCU ≥ ~$1M/day, ~500 CCU ≈ top 0.1% of games. Only ~3% of non-minor devs ever hit 2.5k CCU.
- Incremental/idle economics: a pure incremental with 75min+ average playtime and good balancing is "a free ticket to ~$1k USD/day for 2–3 months"; one member's incremental made 200–400k R$/day; anything over ~75 min average playtime is basically incremental or automated-TD territory.
- Misc revenue datapoints: incremental keyboard game 450k R$/72h at 1k CCU; "guess my brainrot" ~50k/72h at 10k CCU; a 3rd game made 30k R$/72h at 30 CCU before being sold and scaled to 500 CCU by the buyer; 700-CCU game earning only 1.5k R$/day blamed on bad demo; gas-station tycoon with decent CCU and 25% US players <3k R$/day; outfit/UGC game profiting 7–10k R$/day off ads alone; a trend-chasing horror game made ~700k R$ over a 3-week lifespan before a maturity-questionnaire flag collapsed its CCU; trend games have a weeks-long shelf life; 30 CCU / 10k R$ per 72h → 2k+ CCU / 300k per 72h after iterating on feedback.
- Payer-conversion vs ARPPU trade-offs: 0.09% PCR with 524 ARPPU (98th percentile; whaling hard on almost nobody) vs 0.96% conversion with 120 ARPPU; snapshot math: 400 CCU × 2% PCR × 100 ARPPU ≈ 800 R$; A "conversion-only" success: ~5 CCU avg, ~3,000 daily players, 25-R$ forced spend, ~95% payer conversion, ARPDAU ≈ 20 R$; pure algo traffic on insane conversion despite horrible stats. 100 CCU at 2% PCR but only 2–3k R$/day because avg spend ~16 R$; low ARPPU, not conversion, was the bottleneck. A clicker with 3% payer conversion but only 60 ARPPU; a PvP game with 27 min playtime and 3–4% payer conversion but bad D1/D7. Focused advice: fix the weakest percentile stat first (e.g. 18th-percentile conversion)
- Live-ops turnaround case with numbers: monetization redesign (+180% PCR), UGC traffic push (+20M impressions), weekly live-ops calendar (+17M impressions), UI/UX + progression rework (+30% ARPDAU).
- Game acquisition market: a 700-CCU game drew a $2k offer; a 20-CCU game evaluated at $100k–$175k (sold 20% for $20k purely on potential); common valuation shortcut = current month's earnings × 22; a buyer evaluated Hack a Business at $12k; buyers pay up for ~500-CCU games they believe can blow up; buyers purchase dead games cheaply to revive.
- Investor/publisher deal structures shared: one contract gives +5% to the publisher if CCU stays >10k for 5 straight days; a 25k-CCU-peak game generated ~3M R$ in 72h while climbing +2k CCU/day, and revenue peaked when it was sold.
- Solo small-team outsourcing rates (2026 USD): builder $400, UI artist $300, modeler $270, animator+VFX $400, icon+thumbnail $60–125, or lead artist $300 + 10% rev share.

#### CTR (sources disagree on "normal"; keep all)

- 7–8.5% CTR at ~$0.002 CPP is achievable and elite (8.5%/$0.002 via a 25-thumbnail method; 7% CTR, 50 CCU, $0.052 CPP on $20/day).
- 1–1.5% CTR is the "your thumbnail is the problem" zone (15 thumbnails stuck at 1.5%); anything under ~2% gets essentially no push; ~1% is normal and 30% outliers are the algo randomly hitting the right audience, not repeatable; reported self-CTRs >10% from tiny impression counts are meaningless.
- ~2.5–4% is healthy/typical-good; 3.5–4%+ CTR makes ad impressions "skyrocket"; top AI thumbnails hit 4–6%; a claimed 21% CTR is considered impossible to manufacture; a party/casual round-based game hit 12% overall impression CTR.
- CTR improves on its own during/after the learning phase: 1.2% → 2.1% over 3 days; the same thumbnail went 3.51 → 4.53 → 5.82 across re-runs; one dev got ~50% more CTR by starting a fresh campaign with identical thumbnails.
- Targeting dominates thumbnail quality: identical thumbnails got 3.2–4.0% CTR with 8 credits targeted vs ~2% with 16 credits untargeted: wrong audience can halve CTR.
- Ad-sourced retention sets a ceiling: 2% retention from ad traffic caps you ~5k CCU; 20k+ requires better organic retention.

#### Tutorials and funnels

- A 16-step tutorial converted 32.9%; re-cut to 12 steps with weak steps fixed → 57.8% (n≈110–143); 14% completion is bad, "80%+ is the goal"; 65% still called awful; 45%+ drop-off within 5 minutes is serious; ~60% new-user first-session retention is good; Healthy funnel baseline: 85% tutorial completion, 12% bounce after 180s
- A single bug in one tutorial segment dropped completion 80%→30% and flopped the game; raising tutorial difficulty dropped completion 70%→50%; a visuals-only update (no tutorial changes) took completion 45%→75%; polish of the first minute moves funnels as much as tutorial design; 49% before → reworked simpler; highest-leverage D1 fix.

#### Playtime

- ~5 min average is too low; ~10 min is the level the algo rewards; 5–7 min is "horrible", ~9 min ≈ 50th percentile for one genre (Encryptíc+); <8 min session time = the game itself is broken; home recommendations roughly double session time (10 → 23 min once recs kicked in); a $1k-earning game went 3.7 → 16 min playtime in two weeks via daily funnel-driven small changes; a failing game went 5 min/4% D1 → 17 min/18% D1 through iteration: bad launch stats are fixable.

#### D1 / D7

- Legacy top games (MM2, Adopt Me, Grow a Garden) run 50–60% D1, a level new games can't touch, and get a guaranteed algo-impression floor.
- Scale-invariance claim: a 5k-CCU simulator at 22min playtime / 17% D1 / 2.31% D7 / ARPPU 36.9, and its own 500-CCU version showed nearly identical ratios (20min / 14% D1 / 2.31% D7); A 20k-CCU game had 11% D1 / 3% D7; a 20min/20% D1/1% D7 profile attributed to late-game difficulty spikes.
- D1 falls with no changes: a vibe-coder live-ops mistake dropped D1 20%→10% and CCU 20k→11k within days; a 10k-CCU game saw D1 fall 20%→15% (seasonality/school); one dev's genre had all benchmark percentiles at 99.
- D7 is hard for everyone: stays low until home recs kick in; D7 reads 0 until the game is 7 days old and swings wildly day-to-day (9% → 0% → 10%) as cohorts mature.
- Percentile estimates: D7 = 2% ≈ 85th–90th percentile for a simulator (2.2% = 90th); tycoon 90th percentile ≈ 15% D7; a launch D1 of 33% from home recs is predicted to settle ~25–28% (the first push finds the core audience, then it spreads to broader, less-matched ones; "as long as you can add some more depth, the game's going to blow up"); 22% D1 on the retention chart is "fantastic" in context; sessions predicted to settle 30–35+ min.
- PTR (play-through rate) below the 50th percentile is the growth blocker: a polished game with great D7 and weak ARPU wasn't hitting the homepage; "with those stats you would imagine it's in the homepage. It's the PTR holding it back."

#### Dashboard traps

Condensed here; full detail in §11.5 Traps. D1/D7 has ~3-day reporting delay, overview metrics lag 2–3 days, Roblox analytics lag 24–48h; only thumbnail CTR and funnel data are actionable in the first days; the stat tiles systematically undercount before 500 HEP (one dev's playtime jumped 13→27 min purely as a threshold artifact); rolling averages include your own playtesting; "session time" is a live-window average that swings 0.7→20 min at ~5 CCU; "sessions per day" ignores play beyond 60 min/player/day; pull your own metrics into Grafana; the dashboard lags badly.

#### Platform economics

- Roblox takes 30% of purchases (1k R$ item → 700 to creator); group payouts are untaxed and require 14 days of group membership
- DevEx real-cash rates ≈ 100k R$ → $250–400 depending on region/path; cash-outs once per month; DevEx split: 18+ verified US purchases pay ~$0.0054/R$ vs standard ~$0.0038, auto-split by buyer origin.
- From Nov 1 DevEx is treated as royalties: creators without valid tax info by Oct 31 face up to 24% US withholding; a 64M+ R$ lifetime devexer recommends jurisdiction/timing planning ("California tax gets worse the more you make"); US withholding is taken before DevEx, no-treaty countries get double-taxed (UK filers report 0%), W-8/W-9 required, moving residency is a real strategy ("2k–15k/month → Georgia is the meta"; Argentina cited as bleeding devs dry).
- R6 anywhere in playtime disqualifies a game from the US 18+ DevEx rate: enforce R15-only.
- Ad-credit economics: 1 ad credit ≈ $0.98; 1 credit ≈ 200 players delivered (community ballpark)

#### Ad-spend baselines

- $180/day in ads → 2 CCU; 16 ad credits/day first day → ~10 CCU average; $25 spent → 45k impressions → 240 visits (~0.5% CTR-ish on a weak page); launch with 20 credits/day and ~4% avg CTR → ~100 CCU day 2, ~200 CCU day 4; $16/day for 14 days ≈ 30–40 sustained CCU and pays back ~$300/month if monetized; $10/day for 7 days got ~45 active players day 1; 16 credits/day for a week took a game 100 → ~500 CCU; small-scale ROI: 20 credits/day for a month at 40–60 CCU returned 40k R$ per 26k spent (~1.5x); 1.5% CTR but ~2k ad credits pushed a copycat to 30k CCU; high spend can brute-force scale at mediocre CTR if the game converts; A/B on budget: $10/day averaged 12–15 CCU vs $16/day 25–32 CCU on the same game.
- Ad-spend-to-HEP (highly engaged players) math: ~$100 of ad spend reached the 500-HEP threshold (vs paying 100k R$); a 10-CCU, 1-min-playtime game got 85 eligible players in a week on $16/day; 18 credits/day for 3 days produced 500 engaged players + usable initial stats; $16/day since mid-July at 4.5% CTR produced 280k impressions ≈ halfway to 500 home-engaged users.

#### Launch trajectories and CCU shape

- Ad-driven CCU is spiky and front-loaded: first campaigns spike ~100–200 CCU for minutes-to-hours then settle ~30; running ads one day took a game to 60 CCU then back to 1; stopping a campaign produced a 71-CCU spike decaying to ~25–30; high day-1 CCU while running ads is Roblox boosting impressions to gather data, not organic success; read post-ad stats, not during-ad stats.
- Home-rec impression ramp is roughly exponential once the algo picks a game up: D1 5K → D2 7K → D3 11K → D4 20K → D5 30K → D6 35K → D7 50K; impressions also start low and spike intermittently rather than growing linearly.
- Good day-one numbers ≠ instant algo: a first day with 17.4K visits, 45 avg CCU, 88% like rate and 4.5k R$ earned was not picked up immediately; a "pre-algo" snapshot at day 4 (ads running, 21% D1, 55 min daily playtime, 13 min per-session) still had no home-page push; a day-3 snapshot of 20–30 CCU / 13 min / 10% D1 with rec impressions trickling in but 500 HEP not yet hit is a common launch shape.
- Full-launch week case study (16 ad credits/day): day 1 = 6–12 CCU on ads; day 2 CCU rises; thumbnails pruned to winners; days 3–4 = 20–30 CCU, first home recs; day 5 update pushes 40–60 CCU; ads stopped and CCU held, hitting 500 HEP by day 7–8.
- Second-campaign case: two 7-day campaigns at 16/day: first produced 4 home-rec impressions, second produced 7k; home-rec peak 170 CCU vs only 44 CCU peak from ads themselves; with 5 credits/day you get ~1–2 players at a time with ~20-min dead gaps, which doesn't read as healthy to the algo.
- Algo ramp is slow and non-linear: home-rec plays went 224 → 844 in a single day during the ramp; multiple devs observed ~12 days of bad stats before stats "blew up" once the recommendation system found the right audience; keep updating, don't panic-judge on hourly numbers.
- Zero-ad organic-growth case: ~170-member Discord pre-launch → week 1 200–300 CCU → big update blew it to 1,000+ CCU (peaking 1.5k) in 2 weeks; playtime ~50 min and dropping (new players churn) but 16,000 total hours; frequent thumbnail refreshes (different poses/angles) part of the loop.
- Launch-day collapse pattern: 80 CCU two hours after a 10:00 launch → ~10 CCU by 14:00; measure retention of the first hours, not peak CCU; a spike without D1 mechanics is a rented audience.
- Admin-abuse-style live events spike CCU (1–2k CCU game hit 4k+ during one) but the post-event baseline dropped to 300–400; spikes don't hold without underlying retention.
- Like/dislike ratio barely affects the algorithm; playtime/retention dominates; trading a like-bait mechanic for playtime is a bad trade. Whale behavior is real and fast: one player bought every gamepass in a single sitting while the dev watched his profile page.

### 11.2 Ads-as-data-feed model and algorithm behavior

- Core model: the ads system is a data-feed for the algorithm, not a growth channel; spend level mostly changes speed, not outcome. "It just feeds your organic algo with bad data" if the game is unfixed, but run ads for a week *while improving the data* to raise the chance of stable organic CCU after ads. A 10k-CCU-caliber game reaches the same algo injection from 75 credits as 750; only multiplayer-dependent games need the higher floor; "whether you spend 1,000 vs 50 ad credits it will only change how fast you stimulate it". Roblox now prioritizes organic growth so heavily that a game which can't hold CCU without ads won't be saved by ads. Pause ads entirely while shipping a core-loop rework so bad new-session data doesn't poison your stats.
- Ad traffic pollutes stats: ad players have measurably worse retention than home-rec traffic (e.g. 1% D1 sponsored vs 4% home on the same game); ads pollute the stats the algorithm judges; some devs deliberately pause ads and let organic impressions recover the numbers.
- Stop-ads rule (consensus, multiple wordings): run ads until home-recommendation impressions exceed ad impressions (practically until home recs alone sustain 10+ CCU), then stop or cut ~50–60%; organic algo players are "infinitely better" than ad players. Continuing ads after home recs dominate can even lower total impressions; several devs reported playtime jumping ~4 min (ads) → ~28 min (algo) on the same game; one kept ads until 100–150 CCU from home recs alone. Home-rec players match your target audience almost exactly, so post-algo stats are structurally higher; ad stats understate a good game.
- Sponsored impressions are an algo-weighted auction, not a pure bid: higher spend buys more (and somewhat better-quality) impressions but you can't crowd out competitors; even giants like Rivals and Pet Sim 99 still take a large share of sponsored traffic; run a second ad wave only after home recs dry up.
- Beta mode is a stat-laundering tool (consensus with counterpoint): release in beta → the game stays out of home recs → burn ad credits, fix funnels/D1/playtime/monetization while ratings can't tank you → flip public with clean data for a large influx; heavy beta spend is for A/B testing ~100 thumbnails and proving sticky metrics. "Bad data is worse than no data": a buggy public launch permanently teaches the algo your game is bad; it "ruins your game's future recommendation ranking." Counterpoints: it eats your 7-day algo window; one dev argues it's wasted money vs launching ready; beta mode may have hurt one game's home-recs traction for a month; another warns that beta mode will only reduce the player count. The community splits.
- Use a small trial ad run as a stats probe, not a growth bet: a short cheap campaign tells you whether retention/CTR have potential before committing real budget.
- Idea-validation heuristic: browse for games with high CCU but low total visits: good stats early in a game's life indicate it will keep getting pushed with little resistance.
- The recommendation system is treated as deterministic and optimizable, not luck-based; timing relative to algorithm shifts is the only luck component: "The algorithm is deterministic... you're able to optimise everything... Ship fast, build for what works." Counterpoint: wild week-scale algo shifts mean being poised at the right time does require luck. The current algo generation (stats-driven rather than luck) is what pulled retired/commission-only devs back because hits became reproducible; the front page now reportedly resembles 2020 more than 2025: simpler games winning again.
- The mid-2026 algo shift weights long-term behavior over launch-day excitement: retention, low bounce, returning players, friend invites; live-ops updates are effectively mandatory; monetization now weighs roughly as much as retention. Reports emphasize "organic engagement, low bounce rate, players coming back, inviting friends"; "retention is probably the stat you should focus on"; and "longer-term behavior rather than launch-day excitement. Updates are no longer optional." Regional pricing can actively hurt placement if category peers earn more robux per player; the algo compares you against category peers. Games get pushed when conversion/ARPPU percentiles are strong; Roblox now actively promotes highly-monetized games, even mediocre ones.
- Roblox has publicly published only one metric ranking: the signal order used by "Recommended For You"; everything else in the creator dashboard (D1, D7, etc.) has no officially published algo weight. Useful for not over-trusting community percentile claims.
- Doors model: the algo behaves like a sequence of doors: each checks average session time/playtime, then retention; fail one gate and you don't pass to the next tier of push. Retention + monetization are what Roblox currently targets with home recs. A game can hit 150 CCU with great PTR and bounce rates and still fall to 0 with no changes when playtime is mid; the algo requires green across the whole stat panel, not excellence in one metric.
- Relative shelf, not absolute bar: even with unchanged stats a game drops as competitors' stats improve; "hitting algo" is never permanent. Roblox also periodically A/B-tests your game against bigger games (unexplained CCU jump explained as "testing you with top dogs, then dropped you back but raised you"), and runs live algo tests causing stat fluctuation.
- Platform-wide algo shifts swing small games violently with zero dev action: 82 → 1500 CCU in an hour (settled 230); 50 → 130 CCU on an un-updated old game; a dead game went 0 → 30 CCU, unlocking the 250-engaged threshold and stabilizing at 100 CCU with 6% D7.
- Algo decisions lag fixes: a game that randomly "algos" months after flopping had its underlying metrics improve invisibly: tutorial conversion went 40%→80% with no changes, then the push came ~2 months later. Stats also lag fixes (don't judge a fix within hours), and conversion/D1/D7 benchmarks are mainly driven by non-sponsored (home-rec) players.
- Cohort model: the algorithm partitions ~300M players into interest cohorts, shows your game to the best-matching ones, then expands to adjacent cohorts if stats hold; a niche game gets pinned to its cohort; survivable at ~500 CCU with high ARPDAU (~10x typical). Stat-divergence reading: playthrough rate up while D1/retention down = expansion into adjacent, less-matched cohorts: normal growth, not an anomaly. The new algorithm weighs ~day-30 retention and takes ~2 weeks on average to pick a game up; D28/D30 is newly important and newly measurable. "The problem is probably within your game, not some external algorithm"; default attribution when stats stall.
- QPTR relative to CTR is the stronger signal: if QPTR is strong *relative* to CTR, that helps more; weak CTR may be thumbnails or a weak core fantasy; don't panic-cancel campaigns after day one.
- Retitling window: don't retitle once deep into collecting data; ~2 weeks post-launch is still the window; "start with thumbnails first... retitle as an absolute last resort"; unless the name is template-adjacent, where packaging blocks players from ever seeing your twist.
- Update-during-ads rule + Friday-noon cadence: 2 weeks of ads → at least 1 update during the campaign; 3 weeks → 2; "update as much as you can." Use Roblox events + update Friday noon–3pm, "the known best time to update your game" (kids off school; the event feature lets players RSVP).
- Ad-litmus test: if the game looks clean, gives players direction, and rewards them in the first five minutes, the ad should do fine. If ads lose money, check the thumbnails and what players see right away.
- Suppression patterns: "+1" clones get no algorithmic protection for the original; clones compete head-on, and most clones averaging ~4 CCU shows the survivorship ("Will Roblox always favor the one released first?" got no confirming answer). Template/semi-template games are being algorithmically suppressed. Roblox reportedly shifted toward 30-day retention weighting, disproportionately hurting brainrot games optimized for 7-day windows; a "retention algo update" was credited with granting more home recs; an earlier front-page filtering update visibly killed a wave of brainrot games; the March 2026 changes specifically killed playtime-farm games (100 → 10 CCU under "the farm or die treatment"). Roblox suppresses home recommendations for "playtime farm" games: fake/AFK playtime pollutes the data the algo trains on; inflated playtime is a liability, not an asset. Doomscroll-style games produce super-inflated playtime; don't benchmark against passive-addiction "retention".
- Legacy/old games get a fixed monthly impression allocation regardless of performance, part of why ancient games sit on the front page.

### 11.3 Ads operations

#### Consensus playbook

16 ad credits/day (~$16) as baseline (12–16/day range cited) for 7–14 days minimum, one continuous campaign; never restart it or flicker it on/off (the algorithm penalizes gaps); keep multiple thumbnails in rotation, kill under-2%-CTR creatives; low CTR means the thumbnail/title/idea is the problem, not the algorithm; stop once home recs carry you. Variants: one dev consistently runs 40 credits/day for 10 days and hits algo on day 3–4; another claims algo can trigger on as little as 5 credits/day if the game deserves it; Leif (Slime RNG creator) method: 22 credits/day for 14 days, ~$300 total. The "~14 days" advice is a generous approximation of the crossover point.  (panic-dropped ~200k R$ into ads out of FOMO after stopping 3 days pre-algo; the sustained cadence exists to avoid this). Spend level trades off against CTR quality: "$5/day with a high-CTR thumbnail beats $16/day with standard CTR". A 15-min average session game should clear the engagement threshold for 16+ (all-ages) eligibility within about half a week at 16 credits/day, a rough pacing benchmark. Buying ad credits with Robux costs ~3x the dollar price ("100k Robux" of credits ≈ $100 of credits; credits priced at ~$0.98 at the DevEx rate); plan funding in USD directly in Ad Manager.

#### Platform targeting and age gates

- Run the first ~7 days all-devices/all-regions, then check where home recs actually land (e.g. 1M PC recs vs 10K console) and only sponsor the platforms that pull weight.
- Age-gating mismatches silently wreck ad stats: if your game isn't unlocked for all ages but the campaign targets all ages, ads serve to under-13s who can't play → trash CTR; devs report CTR jumping after loosening age settings. "If you didn't pay for the all-ages thing... put your ads on +16 only so you get great ctr."
- Kid-oriented genre reality: +1-per-click-style games' core audience is under 16, so you must run engagement ads (plays ads can't reach under-16s until all-ages unlocks); one workaround chain: ship a 16+ game first → earn 100k R$ → pay the fee to bypass HEU → then advertise your kids' game.

#### Learning phase and thumbnail culling

- Campaign learning phase: Roblox ads have a ~24–48h learning period; CTR is artificially low while it finds the right demographic (0.8% at 2h in can become 3%+); judge CTR only after the phase; learning phase has inflated CPP; don't judge a campaign or thumbnail on day-1 numbers.
- Don't manually kill underperforming thumbnails early: the ad system auto-detects bad creatives and starves them itself; hand-disabling can kill "a golden goose that was just an ugly duckling at the start"; Roblox cycles thumbnails ~24h to find the winner then pushes it.
- Culling protocol (quantitative union): load 8–12 (up to ~25) thumbnails into one campaign; let every creative reach 1,000 impressions (some say 10,000) before judging; a 1% CTR difference is enough reason to swap; 6-thumbnail tests consumed a 500k-R$ budget on one big launch; keep 4–8 activated max (inactive ones still soak impressions); add new creatives only if none is a clear winner. Give each thumbnail ~10,000 impressions minimum; don't add thumbnails to a campaign stuck in learning phase; start a fresh campaign instead.
- The 25-thumbnail method: upload ~25 creatives, run ads untouched until 250 highly engaged players, keep the best 3, then cut to the single clear winner; this produced 8.5% CTR and $0.002 CPP. Roblox optimizes spend toward the highest-CTR creative automatically, so rotating many thumbnails is cheap discovery.
- Ad thumbnails and home-rec thumbnails are different jobs: one dev couldn't get home recs after 2 weeks of ads until he added a thumbnail specifically designed for the home-recs row; stats tripled and home-rec impressions hit 800k+.

#### Campaign objective

CONFLICT on plays vs engagement: engagement/HEP targeting gets fewer impressions but higher CTR and pre-filters for spenders (a play-optimized ad delivers 100 visitors, engagement-optimized ~10 of those 100, pre-filtered for spenders); plays targeting gets broad volume at lower CTR; engagement ads have a lower CCU requirement and fill the engaged-players gate faster; plays is cheaper for growth/data/push. Several devs say never use engagement campaigns (one got ~0 CCU from engagement vs 10+ players within an hour from plays; another saw 4x impressions and higher CTR from plays); a minority counters "Engagement >>> Plays because engagement buys more plays long-term"; Roblox's own UI recommends engagement and devs call that "very misleading." Practical split: plays for growth/volume, engagement when you specifically need to close the HEP gap.

#### HEP gate

- The 250 highly-engaged-player gate (formerly 500): ads count toward it; the paid 100k-R$ expedited bypass is widely considered not worth it; one dev who paid found stats "basically the same, even for games meant for young kids"; the free route is 250 engaged plays → (auto) unlock. CONFLICT: one dev whose audience was ~80% kids paid the 100k (kids couldn't pass the 16+ wall) and CCU jumped 100–150 → 300–400 (500 peak) the day after; worth it for kid-skewed audiences. Community consensus otherwise: a decent game reached 500 HEP on <$100 of ads under the old threshold.
- All-ages/HEP mechanics beyond docs: the 1,000-R$ refundable fee publishes to all ages only after completing the HEP requirement; unlock is automatic ~24–48h after crossing, per-game not per-account; HEP progress accumulates while the Maturity Questionnaire is under review but the questionnaire must also pass; after 500 HEP (under the former threshold) the algo starts actively testing your game (good metrics at 30 CCU can push 50–100+ CCU, no guarantee); "highly engaged" ≈ spent robux on-platform recently + plays long enough, so a young-skewing audience slows the gate badly; getting ~500 visits from tiny ad spend doesn't give the algo enough data; no home recs follow, the spend floor exists to generate statistically meaningful sessions.
- Toggling from under-16 to 16+ doesn't rescue bad stats; a game underperforming before the unlock stays underperforming; the 100k all-ages unlock (fully refundable, so established devs pay it on every new game) is mainly a bot/low-quality gate and trivially cheap for anyone with a 300+ CCU game.

#### Ads-manager gotchas

- Ad review rejections can come from asset naming: abilities named "Gambler" and "Jackpot" sat in review for 12 hours until renamed; gambling-adjacent vocabulary trips moderation. Ads-manager gotchas: you CAN add creatives to a running campaign (three-dots → edit); canceling wastes no money; multiple campaigns at once are fine; moderated-thumbnail status still spends; appeal any non-TOS moderation warnings immediately (they stack); schedule campaigns ≥30 min ahead or they get stuck in review indefinitely; never use lifetime budget: it burns your credits in ~1 hour leaving 23 empty hours (only consider it when CCU already comes from home recs).
- The ads/analytics platform goes through periods of being bugged platform-wide: impressions cut to 1/10, spend 10x-ing overnight for the same impressions, campaigns freezing; verify against other devs before blaming your game.
- Managed (regional) pricing: enable it: prices adjust by country development index, and lost margin from cheap regions is smaller than the sales you'd otherwise lose ("cheap for the US is still pricey elsewhere"); one dev considered blocking Brazil (22% of players at 0.08% payer conversion) via regional access settings.
- External creator funnels are a real acquisition channel: a team drives players from YouTube and estimates ~5k active long-retention players from it; a random toolbox-built game hit 1k+ CCU (16+ audience) purely via TikTok virality.

### 11.4 Traps

- Dashboard lag: D1/D7 has ~3-day reporting delay, overview metrics lag 2–3 days, Roblox analytics lag 24–48h; only thumbnail CTR and funnel data are actionable in the first days; pull your own metrics into Grafana, as the dashboard lags badly; US/Brazil demographics dip at night; compare week-over-week, not hour-by-hour.
- Stat-tile traps: the "session time" tile is a recent live-window average, not all-time; at ~5 CCU it swings 0.7→20 min from sampling noise, and bouncer-dominated distributions make it read low even for elite games; most drop-offs happen within the first minute and long-session players are invisible on the "session time by place" chart; the graph systematically understates your best players; "sessions per day" doesn't count beyond 60 min/player/day, so ultra-long AFK-loop design is invisible in stats; the 7-day rolling averages include your own playtesting; switch smoothing to "none"; your own test sessions skew stats (one dev's pre-release play made PCR read 100%); judge from daily stats, not rolling averages; before 500 HEP all stats are undercounted; one dev's playtime jumped 13→27 min purely as a threshold artifact.
- Moderation/questionnaire kill-shots: a moderation warning received *while* entering home recommendations can nuke traction permanently; the game gets "thrown to a different audience" and full-green stats collapsed in one day; content-maturity labels have been removed; warnings exist for off-platform links in bios (enforced); one game's CCU dropped by a third after being force-set all-ages. Scrub content/age-rating risks *before* pushing into algo. Maturity questionnaire answers have kill-shots: Roblox auto-flagged "chasing NPCs = violence" and locked a climbing 50-CCU game (headed to 20k) to 16+, gutting its audience; check how innocuous mechanics map to questionnaire categories before launch. Trend games die the same way: a maturity-questionnaire flag collapsed a horror game's CCU after ~700k R$ over 3 weeks.

## Sources

Official Roblox sources, reviewed 2026-08-02 (RFY direction update reviewed 2026-08-07):

- [Discovery](https://create.roblox.com/docs/discovery)
- [Analytics essentials](https://create.roblox.com/docs/production/game-design/analytics-essentials)
- [Acquisition](https://create.roblox.com/docs/production/analytics/acquisition)
- [Retention](https://create.roblox.com/docs/production/analytics/retention)
- [Engagement](https://create.roblox.com/docs/production/analytics/engagement)
- [Monetization analytics](https://create.roblox.com/docs/production/analytics/monetization)
- [Experiments](https://create.roblox.com/docs/production/experiments)
- [Core loops](https://create.roblox.com/docs/production/game-design/core-loops)
- [Onboarding](https://create.roblox.com/docs/production/game-design/onboarding)
- [LiveOps planning](https://create.roblox.com/docs/production/game-design/liveops-planning)
- [LiveOps essentials](https://create.roblox.com/docs/production/game-design/liveops-essentials)
- [Content updates](https://create.roblox.com/docs/production/game-design/content-updates)
- [Monetization foundations](https://create.roblox.com/docs/production/game-design/monetization-foundations)
- [Season pass design](https://create.roblox.com/docs/production/game-design/season-pass-design)
- [Icons](https://create.roblox.com/docs/production/publishing/experience-icons)
- [Thumbnails](https://create.roblox.com/docs/production/publishing/thumbnails)
- [Accessibility](https://create.roblox.com/docs/production/publishing/accessibility)
- [Regional pricing](https://create.roblox.com/docs/production/monetization/regional-pricing)
- [Price optimization](https://create.roblox.com/docs/production/monetization/price-optimization)
- [Boost Your Discovery by Building Games People Want to Play](https://devforum.roblox.com/t/boost-your-discovery-by-building-games-people-want-to-play/4779042) (2026-08-06)

The practitioner sections are experience-based, not official Roblox guidance. [qptr.io](https://qptr.io) and [Creator Exchange](https://creatorexchange.io) are optional third-party research aids, not Roblox sources.
