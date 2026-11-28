# Roblox Growth Design: Full Reference

Sections marked **Official** describe documented Roblox behavior. Other examples, thresholds, and models are starting points to test, not verified ranking rules. Unverified hypotheses are marked in place.

LiveOps cadence, events, season content, launch ads, and packaging (icons, thumbnails, titles) live in `roblox-liveops`. This skill diagnoses: what the numbers say, how discovery works, and which experiment to run next.

## 1. Operating Model

A game-design diagnosis connects four layers:

1. **Promise:** what audience the title, icon, thumbnails, and premise attract.
2. **First session:** join reliability, comprehension, time-to-fun, and the first core-loop payoff.
3. **Long-term game:** progression, variety, social value, identity, mastery, and LiveOps.
4. **Business:** transparent products that add player value without damaging trust or the economy.

Do not jump from a weak metric to a feature prescription. A metric is an observation; several causes can produce it, and one change can move several metrics.

### Evidence hierarchy

1. Roblox Experiments with an adequate minimum detectable effect (MDE), full planned duration, confidence intervals, and stable variants.
2. Cohort or release comparisons with acquisition source, platform, locale, player age, and seasonality controlled where practical.
3. Funnels, journeys, session traces, errors, performance reports, economy sources/sinks, and behavioral telemetry.
4. Moderated playtests, player observation, support reports, surveys, and community feedback.
5. Competitor teardown and informed judgment.

The lower levels generate hypotheses. They do not prove causation.

### Experiment brief

Before changing the game, write:

- **Observation:** what moved, for which cohort and date range?
- **Hypothesis:** if we change Y because evidence Z, metric X should move.
- **Primary metric:** one measure tied to the hypothesis.
- **Guardrails:** metrics that must not regress, such as errors, D1, economy inflation, payer complaints, accessibility, or mobile frame rate.
- **Exposure:** eligible players, control, variant, rollout, and planned duration.
- **Power:** baseline, the smallest effect that would change the decision, and the sample or duration needed to detect it.
- **Decision rule:** what confidence and practical effect justify shipping?

**Official experiment rules.** Roblox Experiments run 14–60 days, with one baseline and up to two treatment variants, and one running matchmaking experiment per universe. Do not use first-day results for decisions, stop because a favorable line appears, or claim a causal win without significance. Stop or roll back for safety, severe regressions, broken instrumentation, or invalid exposure. Games below roughly 1,000 daily active users may struggle to detect useful effects; use the dashboard's MDE rather than inventing a universal traffic threshold. An **Early Harm Detection** webhook fires when an experiment shows critical harm in its first 24 hours (see `roblox-cloud`).

**Implementation (official):**

- Use `ConfigService:GetConfigForPlayerAsync(player)` (not `GetConfigAsync`) for a player-specific snapshot. `GetValue` on that snapshot enrolls the player; the first call is random and later calls return the same variant for the experiment's duration. `GetConfigAsync` does not apply targeting.
- Call `GetValue` as late as possible. Calling it early enrolls players who never reach the feature you are testing.
- Target enrollment with your own criteria (for example, only players with `racesCompleted == 0`). Store the assignment if you need it across sessions.
- Experiments track D1, D7, playtime, session time, payer conversion, ARPU, and ARPPU regardless of the goal metric. A metric is significant when its confidence interval does not overlap 0%. "Make decision" (or the Open Cloud `:complete` call with a `variantId`) promotes a variant to the default config; completing without a variant falls back to the previous value.
- Experiments can be created, started or scheduled, monitored, and completed through Open Cloud (`creator-configs-public-api/v1/experimentation`, `universe:read` and `universe:write`). Once started or scheduled, duration, rollout, and variants are immutable.
- Configs "do nothing unless you use them in code." A code-side fallback such as `snapshot:GetValue("x") or DEFAULT` only applies while the key is absent, so a live key with the same name always wins. Measured in one project: half of a pacing change never reached players because live keys shadowed the new code defaults. Log the effective tuning at server start, diff it against code defaults after every release, and change live keys through the configs draft-then-publish flow.

**Official best practices:** start with a written cause-and-effect hypothesis; skip tests whose MDE is too high (for example over 100%); run the full duration because novelty skews early results; avoid unrelated changes mid-test and simultaneous tests that could interact; read confidence intervals, not only verdicts; weigh results against qualitative feedback and product vision; document decisions.

### Acquire evidence before diagnosis

Ask for what actually exists: Creator Dashboard screenshots or exports, cohort windows, release dates, acquisition mix, session recordings, and player feedback. Use Studio or project telemetry for runtime facts. State what is missing and never fabricate a metric, cohort, or causal explanation.

The Analytics Query API (`universe.analytics:read`) returns the same metrics in a scriptable form, with breakdowns such as `AcquisitionSource` on forward D1/D7/D30 retention, and a data-point `status` of `Valid`, `Projected`, or `NotStatisticallySignificant`. Treat `NotStatisticallySignificant` as "imprecise, show the uncertainty," not as zero. Query and benchmark details: `roblox-analytics`.

## 2. Evidence Limits and Small Samples

### Low volume is imprecise, not noise

A small-cohort metric is a measurement with wide uncertainty, not meaningless noise. One random player can triple daily playtime at 5 CCU, and D1 can swing from 0% to 10% day to day, but that spread is the confidence interval talking. Report it that way:

- Show the **denominator** with every rate ("D1 4/37 = 11%").
- Show the **uncertainty** (an interval, or "a 10-point change is the smallest we could detect").
- Separate **diagnostic evidence** (where players drop, what broke, which cohort differs) from a **keep/kill/pivot verdict**. A small sample can still show that 30 of 40 new players never reached the first reward; it cannot show that the game has no audience.
- Say "not enough data yet" when the detectable effect is larger than any change you would act on.

Measured in one project: the same build's early retention swung between 18% and 41% by hour of day. About 350 new players per arm detected a 10-point change, and about 1,340 detected 5 points. Ship one change per build below that volume.

### Comparison designs that survive confounds

- **Split inside one build.** Test gameplay or onboarding as a 50/50 split by UserId inside one build (Roblox Experiments, or your own hashed assignment). Comparing builds published at different hours mixes the change with daypart. Write hypothesis, primary metric, counter-metrics, and decision rule first. Hash quality matters: `roblox-analytics`.
- **Match time blocks.** If you must compare builds or campaigns, compare the same weekday and time-of-day windows and report the cohort and observation window. Roblox documents weekly seasonality that peaks on Saturday; platform-wide, one dataset ran a Saturday at about 1.7 times a Tuesday, which once got a genre wrongly called dying.
- **Equal-width bins.** Plot exits in equal-duration intervals before describing a "cliff." A big drop in a wide bin may only reflect more elapsed time.
- **Fixed-window survivor checks.** To test whether an event protects retention, compare players active at the same window start over the same fixed interval. Otherwise the event looks protective because players had to stay long enough to see it.
- **Selection bias.** "Players left after buying X" needs a base rate: compare against leaves after other purchases at the same point (in one check both were 25% within five minutes). See `roblox-analytics` for more confounds.
- **Exposure, not just presence.** Count how many players actually experienced a feature. In one trace set, 93% of new players played alone because reserved friend slots left strangers one open slot; packing servers raised the average from 1.1 to 2.8 players. Total sessions hid that the social design was never seen.
- **Ad delivery drift.** When most traffic is sponsored, ad delivery can change the audience within an hour with no edit from you. In one case CTR jumped from about 2% to 6% and impressions halved at the same spend, and first-session retention dropped on an unchanged build. Pull hourly ad impressions and clicks (`roblox-cloud`) before calling a build better or worse, and compare builds within the same CTR band.
- **Return from saves.** When dashboard retention lags or is too coarse for a small cohort, compare each traced new player's saved last-seen time with their first join to compute same-week D1/D7 per acquisition cohort, then reconcile with the dashboard once it fills in.

### What reference evidence can and cannot prove

Studying other games is useful for hypotheses, but each method has a ceiling:

- **A feature present is not a feature working.** A checklist "yes" or a config entry shows presence. Reviewed task systems had unreachable thresholds, counters that never increased, and reward calls commented out.
- **Keep category definitions.** "31 scarcity signals" is not "31 fake timers." Summaries must keep the category's real definition; recount from the raw aggregate when a summary disagrees with it.
- **A matched kit is not the live game.** Kits matched to a live game by name or likes had different passes and reconstructed server scripts.
- **A CCU curve is not retention.** Latest-versus-peak CCU over different windows does not measure return rate, and one tracked day cannot show "spiked and died."
- **Text scans over- and under-match.** A source scan for an API name matched a generic `MembershipType` check as "Premium perks" and missed third-party analytics used instead of `AnalyticsService`.
- **Citations need reading.** A checker that confirms file and line bounds does not confirm that the cited code supports the claim.
- **Place-file geometry is not playable space.** Area and "walkable" totals from downloaded places are inflated by invisible collidable blockers, water and scenery tiles, gaps between zones, and below-map surfaces; round games often store only their lobby. Client-saved places contain no server scripts and are streamed subsets. Use walked routes and the game's own counters, and measure routes in your own prototype.
- **Naming patterns are correlation.** A word common among breakouts does not prove the word draws players.

A static `.rbxl` or `.rbxm` reveals structure, not player success. Handoff: **observe** the structure, turn it into a player-facing **question**, **instrument** the smallest success and abandonment events, then **test** with observation, logs, cohorts, or an experiment.

## 3. Official Home Recommendations Model

<!-- temporal: 2026-11 -->

Roblox's **Recommended for You** (RFY) system has two stages.

- **Retrieval** selects a personalized subset of games. It needs only a very low minimum number of plays from any source (ads, search, charts, friends, teleports, notifications, curation, external sharing), which is why an old game can grow again.
- **Ranking** orders candidates per user. Ranking signals come only from users acquired organically through RFY. Engagement from users first acquired through ads, search, friends, social media, or other sources does not enter this stage.

So external acquisition creates a seed cohort and revenue, and its behavior is valid product evidence, but it does not directly repair weak RFY signals. Roblox's Discovery FAQ adds: **ads do not hurt RFY ranking**; sponsored tiles are served by the ads system and aren't ranked as RFY candidates.

### Signal groups (official, dated)

Roblox says signal influence changes over time. Discovery's goal is long-term retention and long-term monetization.

**Most important:** play through rate (PTR, users who play after an RFY impression); first-play bounce rate (leaving within 60 s, with a 61–180 s bucket; negative); play days per user across D1, D2–7, and D8–28; playtime per user (capped at 60 minutes per user, per game, per day).

**Important:** intentional co-play days, qualified play sessions, spend days, and Robux spent, all per user.

FAQ details worth knowing:

- PTR and bounce count only RFY-acquired users in their **first session**. D2–7 and D8–28 follow those users even when they return through Continue.
- D2–7 play days is the average of how many of those 6 days users played; D2–7 playtime is total playtime divided by users.
- New games do not wait 28 days; signals arrive in stages.
- There is **no penalty** for a weak first test. Signals use a moving window, and the algorithm keeps testing new users; fix onboarding and it re-tests.
- Signals are per-user averages, so smaller games are not disadvantaged by totals.
- Games strong in only retention or only monetization still get impressions; strong in both may get broader distribution. If retention is low, fix core gameplay first.
- A custom thumbnail is required for Home recommendation impressions; a game with only the default thumbnail is not eligible.
- Reduced reach comes only from documented reduced-exposure or discoverability restrictions. Report issues through Support → Discovery Content Quality → Quality Reduced Exposure with the universe ID and creator ID.

### Explore, expand, and context

Roblox explores a game with cohorts and expands when they respond well. Impressions move with four factors (official): your updates, platform algorithm changes, Home traffic seasonality (weekly peaks on Saturday; summer, school, holiday cycles), and competitors improving faster. A drop while your signals are steady can be competitive, not punitive. A temporary PTR dip can accompany an impression increase as the game reaches less-matched users.

### Dashboard workflow

In Creator Hub, **Analytics > Acquisition > Home Recommendations** (also on the Analytics Overview):

1. Inspect RFY impressions and plays.
2. Check the most important signals first; if stable, check co-play, qualified sessions, spend days, and Robux spend.
3. Compare against benchmarks as rough context only. Benchmark games do not affect ranking. The Benchmarks API returns the same genre, similar-players, and top-experiences percentiles (10/50/90) programmatically and is experimental (`roblox-analytics`).
4. Segment other acquisition sources separately.

### Kids and Select gate (official, re-checked November 2026)

<!-- temporal: 2026-11 -->

Games published for all ages are first available only to age-checked 16+ users until they pass the Kids/Select evaluation: **100 unique plays by highly engaged age-checked users within 60 days**, evaluated hourly (the docs lowered this from 500 to 250 in August 2026 and to 100 in November 2026). Track it in Creator Hub > game > **Publish Settings** > **Manage Audience**. A highly engaged player meets tenure, playtime-in-your-game, and platform-spend requirements (a purchase **anywhere on Roblox** in the last 60 days plus time in your game in that window); Roblox says the criteria "will evolve." Publishing or updating for all ages needs a Roblox Plus or Premium subscription held for 2 consecutive months, or a refundable fee.

Do not conflate thresholds: the **publishing fee** (1,000 R$) is refunded when the game keeps **25** highly engaged players for 60 days without moderation; the **expedited review fee** (50,000 R$, lowered from 100,000 in September 2026; 48-hour review that restarts on resubmission) can be withdrawn after 90 days in good standing with **25** highly engaged players. Neither is refunded after permanent moderation. Content ratings (Minimal or Mild for Kids and Select) are a separate gate: `roblox-publish-checklist`.

Field reports, not official: ads serve 16+ automatically; Home placement can start before the gate clears; Home impressions fill the count faster than ads; a young-skewing audience fills it slowly because fewer players have recent platform spend.

### A working model of the algorithm (field reports, unverified)

Operators describe the system this way. None of it is documented ranking logic.

- **Ads are cold traffic.** Ad players are the cheapest, least-qualified audience: low engagement, spend, and D1. Launch stats on ad traffic look bad; Home traffic usually runs higher (one game: 8 min playtime from ads vs 19 from Home; another 1% vs 4% D1). Ad spend changes speed, not the ceiling.
- **Updates, not spend, move you up.** Run ads → collect data → find the worst stat → ship an update that improves it → re-run. One stat per update keeps cause and effect legible.
- **Gates in sequence.** A game can show great PTR and bounce, reach 150 CCU, and fall to 0 when playtime is mid; operators report needing the whole panel green, not one metric excellent.
- **Relative shelf.** Unchanged stats can still lose impressions as peers improve. Unexplained jumps and drops can come from Roblox testing a game against larger ones or from platform tests.
- **Stat divergence.** PTR up while D1 falls usually means expansion into adjacent cohorts, which is normal growth.
- **Lag.** Algorithm pickups have arrived weeks after the underlying stats improved; don't judge a fix within hours.
- **Suppressed patterns.** Template clones, misleading packages (exposed by bounce rate since the June 2026 PTR/bounce split), and playtime-farm or AFK-inflated designs are reported to lose distribution. Inflated playtime is a liability, not an asset.
- **Monetization percentile matters.** Regional pricing can hurt placement if category peers earn more per player (unverified); fix the weakest percentile stat first.
- **Legacy floor.** Very old top games reportedly keep a baseline allocation regardless of performance; don't benchmark launch D1 against their 50–60%.
- **Default attribution.** When stats stall, "the problem is probably within your game, not some external algorithm."

Beta mode (official) keeps a game out of Home recommendations. Some teams tune on cheap ad traffic in beta before opening to RFY; others argue it wastes the first exposure window. The community splits.

## 4. Diagnose Metrics Without Single-Cause Thinking

### Low play through rate

Hypotheses: icon or thumbnail unreadable at mobile size; image doesn't communicate genre, action, fantasy, or tone; packaging attracts an audience the game can't satisfy; premise too familiar; a recent expansion reached a broader cohort.

Evidence: RFY PTR; thumbnail personalization QPTR by thumbnail and winning segment; qualified plays and playtime per active thumbnail; detail-page CTR (users who played from the detail page ÷ users who viewed it); mobile and desktop previews; mismatch between promise and first session. A higher click rate with worse bounce or retention is not a win. Packaging fixes: `roblox-liveops`.

### High first-play bounce or weak early session survival

Investigate in order: join failures, crashes, errors, memory, frame rate, long loading; metadata-to-game mismatch; unclear controls or goal; mandatory menus, dialogue, character creation, or tutorial before meaningful action; first payoff too late; dead or confusing social spaces; platform-specific input or UI failure.

Instrument join complete, gains control, first meaningful action, first reward, core loop complete, and exit. Track negative outcomes too (a lost fight, a blocked purchase prompt). Use journeys for branching paths and funnels for ordered ones (`roblox-analytics`).

### Low D1 retention

Roblox points to core loop, first-time user experience, and performance. Hypotheses: loop understandable but not enjoyable; one cycle is fun but there's no reason to return; onboarding teaches mechanics without purpose; progression invisible or first goal arbitrary; starter resources don't let players sample the fun; mobile, localization, accessibility, or reliability fails a segment.

- Funnel every tutorial step, then fix the exact drop-off step rather than redesigning the flow.
- "Show, don't tell" is a strong default for younger audiences; keep required text brief and contextual.
- Give a concrete reason to return tomorrow: a crop that finishes growing, an escalating reward, a friend's base. Put it where players actually are. Measured in one game: a daily reward claimable only at one hub station was claimed by 4–6% of new players because 87% never returned to that hub after their first visit. Measure how many players ever see the return reason.

### Retention changes without a release

<!-- temporal: 2026-10 -->

Field observation: D1 can rise with concurrent players and fall after the peak with no game change, consistent with social network effects (more friends, opponents, and reasons to return). That's a possible mechanism, not proof. Before crediting an update or declaring a regression, compare mature acquisition cohorts, device/locale mix, seasonality, co-play, server occupancy, and matchmaking waits. A shift from paid to Home traffic can move aggregate D1 without changing any cohort.

### Low D7 or D30 retention

Don't reduce this to daily rewards. Investigate short-, mid-, and long-term goals; progression speed; content variety and mastery depth; collections, identity, status; co-play, parties, guilds, competition; endgame; LiveOps cadence; economy inflation or obsolete content. D7 often exposes progression weakness; D30 exposes endgame, cadence, social value, or exhaustion. A week of distinct goals, social-flex items, and regular events give returning players something to chase.

### Low average session time

Check whether players reach the fun, then whether the loop sustains it: time to first meaningful choice; action density versus waiting and travel; reward feedback and goal clarity; loop variety and escalating challenge; performance in long sessions; natural stopping points. Give every core action immediate feedback (sound, small camera shake, a visible counter), then test whether it moves playtime. Longer is not always better; don't trap players.

### Low payer conversion

Can players find and understand the shop? Is the product useful, expressive, durable, or fun, and does it fit current progression? Are there transparent options at several price points? Does onboarding show value before asking? Does the funnel fail before or after the Roblox prompt? A cheap first-purchase offer is one hypothesis, not a default; measure downstream retention, sentiment, and economy impact.

**Official item taxonomy:** durable or consumable, and enhancement or expression. Make each item's purpose legible. **Official shop design:** the shop is the economy's information hub, so make it integrated, contextual, and inviting. Roblox's built-in Shop (`MarketplaceService:OpenShop`) ranks listed items per player. Implementation: `roblox-monetization`.

### Low ARPPU or ARPDAU

Low ARPPU can mean a shallow catalog for engaged payers, or audience, regional pricing, product mix, or a healthy low-pressure economy. Inspect ARPDAU and payer concentration: high ARPPU with low ARPDAU means revenue depends on a narrow subset. Tiered packs give engaged payers somewhere to go; test whether a high-end segment exists before building for one. Never design around "whales," coercive scarcity, deceptive odds, or pay-to-escape friction.

### Declining impressions

Don't assume a shadow penalty. Check Home signals by priority, recent updates and regression dates, acquisition mix, seasonality, broader-cohort exploration, competitors, and a Creator Dashboard reduced-exposure banner (it updates daily).

## 5. Positioning and Idea Validation

### The purple-ocean lens

Seek proven demand with a clear twist rather than a pure clone or an idea with no audience:

1. **Demand:** are players already seeking this fantasy, mechanic, or genre?
2. **Supply:** who serves it, how concentrated is the audience, what do communities dislike?
3. **Difference:** can a player explain the distinction in one sentence?
4. **Roblox fit:** does it use avatars, co-play, identity, short sessions, touch controls, or the social graph?
5. **Production fit:** can this team deliver content, moderation, economy, and cadence?
6. **Evidence:** what cheap prototype or packaging test could falsify it?

Treat third-party estimates as directional. Public CCU, favorites, visits, social views, wishlists, and search trends measure different populations and can be gamed.

**Reading the market.** Compare the same weekday only. Before judging a format's size, sum its whole name cluster from a daily dataset, split by created date (new entrants vs old games), then read the leaders' descriptions, server sizes, and pass lists. In one check, three small look-alikes suggested a small format while the wider cluster had grown from 8k to 68k average CCU in five weeks. Browsing for games with high CCU but few total visits finds early winners.

### Trend lifecycle

1. **First to market:** an original concept captures demand with little competition.
2. **Saturation:** clones flood in; most die.
3. **Mutation:** survivors re-package with a new title, thumbnail, or altered loop. Straight copies of the original's title and thumbnail fail and can trigger metadata penalties.

Entering in phase 2 or 3 needs a real twist or an underserved sub-audience. Failed trend games are usually re-shipped as new games, not revived.

### Off-platform demand and premise checks

Demand proven elsewhere (large wishlists, web-game plays, gameplay videos popular with younger audiences) de-risks a launch, especially if nobody has brought that fantasy to Roblox well. Check Roblox search too: a theme saturated with basic roleplay can host a different genre entirely.

A concept should answer: what does the player repeatedly do; what fantasy does it serve; what changes each cycle; why is it better with others; what can be shown honestly in one icon and thumbnail; what stays fun without spending; what production burden grows with success.

### What makes a game take off (operator view)

1. **An idea a kid can picture before bed**: a fantasy the player wants to live, not just a mechanic.
2. **Onboarding that builds the why**, one mechanic at a time, with level design doing the teaching and minimal UI.
3. **Socialization in the core loop**, so friends invite friends; leaderboards and visible progress add flex.
4. **Simple mechanics with deep expression**, frictionless on mobile first.
5. **Clippable moments** creators can share; watch what they clip and double down.

Study top games for *why* their onboarding and social choices work, and copy function, not style. A common lens: build about 80% from patterns players already know and spend the differentiation budget on theme, fantasy, or twist.

### Idea selection and production

- An idea's job is to make design easier; if it creates design problems, pivot.
- Match ideas to the team's history; solo devs start simple.
- Build only the core loop, make it satisfying, and test with people who already like that niche.
- Release fast and update often; the team should enjoy playing it.
- When the first test with real strangers keeps sliding behind new prerequisites (finished UI, lobby, monetization, a better map), name the slide and make the test the next step. One project ran 13 days and 7 maps with zero strangers because one person's screenshot judgments gated everything. Tell a look complaint apart from a verdict on the game, and check any pivot against earlier decisions that ended the same format.
- YouTube-driven traffic inflates session time (viewers already learned the game); judge platform growth from Home cohorts.

### Commissioned work and rights

<!-- temporal: 2026-10 -->

Before commissioning code, clothing, models, audio, or UI, record deliverables, payment milestones, permitted uses, modification rights, third-party components, and whether rights are assigned or licensed. Prefer paid-on-completion milestones and a contract per scope. Keep signed agreements and provenance outside chat accounts. An invoice or access to source files does not establish ownership.

**U.S. legal boundary:** copyright ordinarily starts with the author (17 U.S.C. §201); owning a copy doesn't transfer copyright (§202); a transfer generally needs a signed writing (§204). Work-made-for-hire has specific requirements, and adding the phrase to a contractor agreement doesn't automatically qualify. A suitable license may be enough. Get jurisdiction-specific legal review; an agent should not assure that an asset is legally cleared. Roblox's own IP policy and notice process: `roblox-publish-checklist`.

### Core-loop audit

> **Action → feedback/reward → progression choice → more expressive or demanding action**

Is the repeated action enjoyable? Is feedback immediate and readable without relying only on sound, color, or motion? Does progression create decisions, not just bigger numbers? Can a new player complete a cycle quickly? Does the action work on touch, gamepad, and keyboard/mouse? Does co-play improve it rather than add bodies? Prototype the uncertain mechanic before building a large content shell. Structural loop and economy craft: `roblox-game-design`.

## 6. First-Time User Experience

Design for **play-first teaching**, not "players never read." Some controls need text; keep it brief, contextual, localized, and accessible. Roblox's retention guidance recommends reaching the fun within about five minutes; treat that as a diagnostic, not permission to rush a complex control scheme.

A first-session sequence: safe arrival with the game responsive → one obvious action with feedback → one small choice → first core-loop completion → a joyful payoff → visible next goals → deeper explanation after motivation exists.

**Official onboarding levers:**

- Keep early XP thresholds low; tune them with Configs without shipping.
- Starter items and currency let players sample utility or expression; find the amount with Experiments, then push the winner as a Config.
- Surface short/mid/long goals visibly; end onboarding with a designed moment of joy.
- Funnel the core-loop steps, track negative outcomes, fix the biggest drop-off, and test specific steps with Experiments.
- Social-first games can experiment with matchmaking parameters during FTUE.

Field notes: every required input between loading and play loses players (welcome popups, unskippable intros, team or slot selects); auto-choose optional steps; even one bouncing button with an arrow loses a few percent who never click. Mobile fails by a thousand small cuts: hand the game to a target-age player on a phone and watch silently, add "Buy 100"/"Max" for tap-heavy upgrades, and keep maps compact. Observe representative players, not teammates. With minors, use appropriate consent, privacy, and safeguarding practices.

Field benchmarks (community-reported, n often small): a 16-step tutorial converting 32.9% rose to 57.8% after a cut to 12 steps; one tutorial bug dropped completion from 80% to 30%; a visuals-only first-minute polish took completion from 45% to 75%. A healthy funnel baseline people cite is about 85% tutorial completion.

### Accessibility and device coverage

Check touch targets and thumb reach; gamepad focus and keyboard/mouse; readable text; contrast and symbols beyond color; captions or visual cues for sound-only information; reduced motion; localization expansion; lower-end memory, thermal load, frame rate, and network. Console players often play long sessions; don't skip a gamepad pass. Implementation: `roblox-input`, `roblox-gui`, `roblox-gui-components`, `roblox-localization`, `roblox-performance`, `roblox-audio`, `roblox-animation-vfx`.

## 7. Monetization With Trust

Good monetization exposes clear value to willing players while the free core stays enjoyable: a transparent storefront and purchase result; several price points mixing durable and consumable value; no hard-coded Robux prices when Managed Pricing can change them; regional pricing where appropriate; no deceptive odds, false urgency, disguised buttons, repeated interruption, or punishment for declining; server-authoritative, idempotent granting.

Price optimization needs volume: Roblox says it usually needs at least 60,000 transactions over the preceding 30 days. Smaller games should use value research and carefully scoped experiments.

Operator lessons that held up across reports:

- **Data first.** Sort product sales, find the best seller, hypothesize the next product from data and observed play, ship, check revenue *and* side effects, keep or revert.
- **Consumables lift spend days.** One-time passes cap the 7-day spend days stat; a repeatable product that solves real friction (a timed protection, a boost) is often the top seller.
- **Sell pain relief, not nice-to-haves:** effort (speed, cash), safety (protection while AFK), missing out (offline earnings), status (genuinely limited cosmetics).
- **Place offers where players are and when they decide**, with several pathways (HUD shop, a "+" beside currency, a capped shop popup after repeated failed buys).
- **Check collateral damage** to playtime, D1, D7, FTUE, and economy after every product.

Telemetry for these decisions: `roblox-analytics`. Implementation: `roblox-monetization`, `roblox-security`, `roblox-data`. Dark-pattern audit: `roblox-player-psychology`.

## 8. Social Design

Social features aren't automatically retention features. Define the interaction (collaboration, competition, spectating, gifting, trading, parties, guilds, shared creation); how solo and new players avoid exclusion; moderation, abuse, and scam-resistant trade; filtering for player text; griefing controls; whether server size and matchmaking support it; and how co-play is measured. Multiplayer-only games die fast when CCU can't fill servers: add solo fallbacks, warmups, bots, or lobby activities, and avoid "waiting for players" screens.

## 9. Audit Workflow

**Step 1: Request evidence.** Game link and audience; RFY impressions, PTR, bounce, play days, playtime, important signals; acquisition by source; onboarding funnel and journeys; D1/D7/D30 cohorts; session time; payer conversion, ARPDAU, ARPPU, products, economy; device, locale, region; errors, crashes, frame rate, update dates; thumbnails, icon, title, description, reduced-exposure banner; feedback and observed sessions.

**Step 2: Baseline.** Separate facts, inferences, and unknowns. Mark immature cohorts and their denominators. Note seasonality, source changes, events, ads, releases.

**Step 3: Narrowest broken transition.** Impression → play; join → control; control → first meaningful action; action → first reward; reward → loop completion; first session → return; retained player → shop visit; purchase intent → completed purchase.

**Step 4: Prioritize.** *Priority = expected player impact × confidence × reach ÷ cost and risk.* A qualitative High/Medium/Low is often more honest than fake precision.

**Step 5: Experiment backlog.** For each item: evidence and uncertainty, hypothesis, smallest change, primary metric and guardrails, cohort, instrumentation, decision date, rollback trigger.

**Step 6: Preserve identity.** Optimization is not a license to turn every game into the same simulator loop. Reject gains that depend on misleading acquisition or damaged trust.

## 10. Output Format

1. **Verdict:** the highest-leverage constraint.
2. **Evidence:** verified facts with source, date range, and denominators.
3. **Unknowns:** missing evidence that could change the diagnosis.
4. **Hypotheses:** ranked, not stated as facts.
5. **Next experiment:** one smallest interpretable intervention.
6. **Metrics:** primary outcome, counter-metrics, detectable effect, decision rule.
7. **Implementation routing:** which skills are needed.
8. **Later backlog:** useful work deliberately excluded from the first test.

## 11. Community Benchmarks

<!-- temporal: 2026-09 -->

Experience-based claims about a shifting platform, not official guidance. Re-check current docs before betting a launch on any number. Launch-ad and CTR benchmarks are in `roblox-liveops`.

**Revenue vs CCU.** Revenue per CCU varies roughly 10–30x with monetization quality, so CCU alone predicts earnings poorly: reports range from a 12k-peak game earning almost nothing (no monetization) to small, heavily monetized games out-earning games several times their CCU. Fix the weakest percentile stat (often ARPPU, not conversion) before chasing traffic. A conversion-only design (a cheap required purchase) can show very high payer conversion at tiny ARPDAU; that's a different business, not a template.

**Playtime.** Around 5 minutes average is widely called too low and about 10 the level operators see rewarded; under 8 minutes usually means something in the game is broken. Home traffic often roughly doubles session time versus ads. Bad launch stats are fixable: reports include 3.7 → 16 minutes in two weeks of daily funnel-driven changes, and 5 min / 4% D1 → 17 min / 18% D1 through iteration.

**D1 / D7.** D7 reads 0 until the game is 7 days old and swings as cohorts mature. Simulator D7 around 2% is reported near the 85th–90th percentile; tycoon 90th percentile near 15%. A launch D1 from Home recs typically settles lower as distribution spreads to less-matched cohorts. D1 can fall with no change (seasonality, school terms, a bad live-ops push). PTR below the 50th percentile blocked one polished game with strong D7 from Home exposure.

**Dashboard traps.** D1/D7 report with about a 3-day delay and overview metrics lag 2–3 days; thumbnail CTR and funnels are actionable first. The "session time" tile is a recent live-window average that swings wildly at low CCU; bouncer-heavy distributions read low even for good games; "sessions per day" ignores play beyond 60 min per player per day; rolling averages include your own playtests (one pre-release check read 100% payer conversion). Judge from daily values with smoothing off, and pull your own metrics if the dashboard lags.

**Platform economics (official).** The standard DevEx rate is 0.0038 USD per Earned Robux (0.0035 before September 5, 2025). The U.S. 18+ rate of 0.0054, effective June 8, 2026, applies to Earned Robux from developer products, passes, subscriptions, and private servers bought by age-verified U.S. adults in eligible games: player characters must be R15 (or qualifying custom human or nonhuman forms) for 100% of active playtime, with R15 animation packs, and a background compliance check removes eligibility otherwise. DevEx payments are royalties: U.S. creators without a valid W-9 face 24% backup withholding; non-U.S. creators with valid W-8 forms see 0–30% withholding on payments tied to U.S. sales, depending on treaty. Tax details: `roblox-monetization`.

## Sources

Official Roblox sources (reviewed 2026-11-27):

- [Discovery](https://create.roblox.com/docs/discovery) and [Discovery FAQ](https://create.roblox.com/docs/discovery-faq)
- [Kids and Select](https://create.roblox.com/docs/production/publishing/kids-and-select), [Publish games and places](https://create.roblox.com/docs/production/publishing/publish-games-and-places)
- [Analytics essentials](https://create.roblox.com/docs/production/game-design/analytics-essentials), [Acquisition](https://create.roblox.com/docs/production/analytics/acquisition), [Retention](https://create.roblox.com/docs/production/analytics/retention), [Engagement](https://create.roblox.com/docs/production/analytics/engagement), [Monetization analytics](https://create.roblox.com/docs/production/analytics/monetization)
- [Experiments](https://create.roblox.com/docs/production/experiments), [Experiments API guide](https://create.roblox.com/docs/cloud/guides/experiments), [Configs](https://create.roblox.com/docs/production/configs)
- [Analytics Query API](https://create.roblox.com/docs/cloud/guides/analytics), [Benchmarks API](https://create.roblox.com/docs/cloud/guides/analytics/benchmarks)
- [Core loops](https://create.roblox.com/docs/production/game-design/core-loops), [Onboarding](https://create.roblox.com/docs/production/game-design/onboarding), [Monetization foundations](https://create.roblox.com/docs/production/game-design/monetization-foundations)
- [Accessibility](https://create.roblox.com/docs/production/publishing/accessibility), [Regional pricing](https://create.roblox.com/docs/production/monetization/regional-pricing), [Price optimization](https://create.roblox.com/docs/production/monetization/price-optimization)
- [Developer Exchange](https://create.roblox.com/docs/production/monetization/developer-exchange), [U.S. 18+ DevEx rate](https://create.roblox.com/docs/production/monetization/18-plus-devex-rate), [Tax information](https://create.roblox.com/docs/production/monetization/tax-information)
- [Boost Your Discovery by Building Games People Want to Play](https://devforum.roblox.com/t/boost-your-discovery-by-building-games-people-want-to-play/4779042) (2026-08-06)

Commissioned-rights legal sources (U.S., reviewed 2026-10-02): [17 U.S.C. §§201–204](https://www.copyright.gov/title17/92chap2.html); [Circular 30: Works Made for Hire](https://copyright.gov/circs/circ30.pdf).
