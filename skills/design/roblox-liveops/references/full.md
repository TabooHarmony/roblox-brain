# Roblox LiveOps and Launch: Full Reference

Sections marked **Official** describe documented Roblox behavior. Field reports are community or single-project observations: test them, don't treat them as platform rules.

Diagnosing stats, Home recommendations, experiments, and Kids & Select live in `roblox-growth-design`. Products and purchase code live in `roblox-monetization`. This skill covers what you ship after launch and how you put it in front of players: update cadence, events, season content, notifications, sponsored ads, and packaging.

## 1. LiveOps Taxonomy (Official)

LiveOps is the post-launch work that keeps a game engaging. Roblox describes four update types, in increasing scope:

1. **Content cadence:** regular fresh content (weekly to monthly) built on existing systems: limited-time events, seasonal content, UGC. Cheap to make, keeps players engaged between major updates.
2. **Major updates:** new or expanded systems that change gameplay: guilds, trading, PVP, leaderboards, tournaments, collections, or large live events aimed at lapsed players. Months of work; they retain current players and attract new ones.
3. **Quality-of-life improvements:** UI layouts, UX flows, visual refreshes, accessibility, performance. Often an outsized goodwill return; collect player frustrations and time sinks.
4. **Bug fixes:** prioritize by severity, effort, and how many players are affected.

Blend all four. Cadence keeps the game fresh, majors evolve it, QoL buys goodwill, and bug fixes preserve trust. Pick a cadence the team can reliably deliver.

### Sustainable content cadence (official)

- **Choose content that's cheap to make:** items, furniture, pets, vehicles, weapons, maps, and quests are mostly art and need little new code. Simple variants (recolors) are ideal. Themes (seasonal, holiday, a central concept) make a release feel coherent.
- **Manage scope:** under three weeks of effort per cadence release. Adding a new system to support a release turns it into an expansion.
- **Keep a routine:** every two weeks to a month is common. A steady rhythm teaches players when to check back, and the team gets faster with practice.
- **Don't make content instantly consumable:** release it through progression (endgame additions for veterans), limited-time content (event currency, quests, milestones balanced to take most players weeks), or season passes.

### Planning an update or event (official)

- **KPI first:** pick the metric you want to move (daily active users, D7, spend days) before designing. Events usually move several at once.
- **Player actions:** define what players should do and which KPIs those actions feed.
- **Economy impact:** more interaction changes earning and spending. A tournament that rewards a currency loop must not hand out rewards that break prices (`roblox-game-design`).
- **Communication:** plan external (social, community) and in-game (popups, lobby, UI) messages and their timing. Advance notice lets players plan their return; announcing too late gets overlooked.
- **Monitor:** check currency sources and sinks hourly or same-day during launch, and compare event weeks with the weeks before and after.

For each event, also write down what remains after it ends. Don't treat an event spike as proof of durable retention; compare later cohorts and ordinary weeks (`roblox-growth-design`).

### Applying the cadence (field reports)

- **Two tracks.** Patches (bugs, exploits, balance, monetization tweaks) ship whenever needed. Updates ship on a weekly or biweekly rhythm, and each names its target metric before work starts.
- **One stat per update.** Pick the weakest stat, ship one change aimed at it (for example, activity rewards that unlock after time in-game to lift session length), then watch that stat. One change per update keeps cause and effect readable.
- **Three inputs.** Qualitative (bug reports, community forums, the Creator Dashboard feedback summary), quantitative (dashboard analytics), and competitor research (what your core audience plays beyond the recommendation feed).
- **Core playtesters.** Dedicated players who out-play the team are great testers but not designers. Listen, then decide.
- **A reported weekly rhythm:** launch, plan the next update the same day, assign it the next day, build midweek, playtest internally then with core players, ship on the weekend. Field reports favor Friday afternoon or Saturday, when younger players are out of school. Roblox's own data shows weekly traffic peaking on Saturday.
- **Do:** talk to your audience, test before launch, watch small creators play your game to spot friction. **Don't:** put monetization ahead of gameplay, ship last-second untested updates, implement every suggestion (it can wreck the economy), or stop updating a live game.
- **Update during paid campaigns.** Operators ship at least one update during a two-week campaign, so the new players see the game improving.

## 2. Season Passes and Limited-Time Content (Official)

A season pass is a limited-time, quest-based progression system that is part of the content cadence. Players complete missions for pass XP and climb reward tiers. It is not a regular game pass (a one-time purchase); see `roblox-monetization` for products.

- **Build on the core loop.** Tie missions to every system and content type, so players learn the whole game and the pass drives engagement with existing content.
- **Make it self-explanatory.** Auto-enroll every player each season and keep a visible Season UI showing mission progress, tier, reward status, and time left.
- **Keep it achievable.** Missions shouldn't consume a player's whole daily session; vary task types to serve different playstyles; make rewards reflect effort.
- **Season length:** one month is a good starting point, with at least a one-week rest before the next season to prevent burnout.
- **Tiers:** about ten is a good starting point: frequent progress, not daunting at the start.
- **Rewards:** wanted but not economy-breaking; make the final reward a worthwhile capstone so players anticipate the next season.
- **Free and premium tracks** need extra care: the free track must feel rewarding on its own, and premium value must be clear.
- Roblox publishes a **Season passes feature package** with working out-of-the-box functionality.

Time-limited offers and season content still need honest timers and no fake scarcity (`roblox-player-psychology`).

## 3. Events, Update Announcements, and Notifications (Official)

<!-- temporal: 2026-11 -->

### Experience events

Create events in Creator Hub under **Engagement > Events & Updates**.

- Up to **10 ongoing or upcoming events** at once.
- Give each event a **unique thumbnail**; Roblox says a thumbnail different from your game thumbnails increases engagement. Without one, the primary game thumbnail is used.
- Events appear on the game's detail page and their own event details page. Players can **Join Event** or **Notify Me**, which sends a stream notification when it starts and offers push notifications.
- To be featured in **Trending Events in Experiences**, an event must be active, have started within the last 7 days, and have at least **1,000 RSVPs**.
- Players who join through an event surface carry the event ID in `GameJoinContext`, so you can greet them, route them, or show event prompts. You can also set a separate event place.

### Update announcements

Announce updates to opted-in players' notification streams: **60 characters maximum, at most once every three days**. Be specific ("New volcano zone and 3 pets," not "bug fixes"), and don't flood players. Roblox is merging events and updates, so the form may change.

### Experience notifications

Server scripts can send personalized notifications to opted-in users aged 13+ through the Open Cloud package (`OpenCloud.V2.UserNotification`). Ask for opt-in in context: call `ExperienceNotificationService:CanPromptOptInAsync()` in a `pcall`, then `PromptOptIn()` if allowed. Notifications can carry launch data, which the joining player's `Player:GetJoinData()` returns. Track reach and performance in the Creator Dashboard. Notify about something the player cares about (their crop finished, their friend's event started), not generic "come back" pings. Implementation: `roblox-cloud`.

## 4. Launch and Sponsored Ads

### Ads Manager facts (official)

<!-- temporal: 2026-11 -->

- **Objectives:** **Plays** reaches players most likely to start a session (broad distribution, testing ideas, initial traffic that can help a game get considered for Recommended for You); **Earnings** reaches players most likely to spend (use with a developed economy); **Qualify for Kids and Select** reaches age-checked Highly Engaged Players. That last one costs more per play, should get its own budget rather than budget moved from Plays, and stops automatically at the threshold. It's optional; many games reach the threshold organically.
- **Audiences:** New Players, Recent Players, and Lapsed Players (played 30–180 days ago; requires 20,000+ lapsed players). These audiences, and genre and gender targeting, only reach users eligible for personalized ads. Advanced targeting covers location, age, gender, genre, and device.
- **Bidding:** automated. You set budget and duration; engaging games can earn system discounts.
- **Budgets:** daily or lifetime. Unused ad credits return after a campaign; cancelling a campaign returns spent credits and stops card charges. Robux→ad-credit conversion is permanent (minimum 1 credit; Robux earned at the U.S. 18+ rate convert first).
- **Creatives:** up to **10 thumbnails per campaign**, **evenly distributed** across players; you can toggle individual thumbnails any time. Images display at 16:9.
- **Placement:** sponsored tiles show on Home and in search. A sponsored tile and your Recommended for You tile can both appear to one user. **Running ads does not affect Recommended for You ranking.** Games whose metadata and place files closely resemble existing games aren't prioritized, and their campaigns may not be effective.
- **Launch data and join options:** route ad clicks to a specific spot and tag the campaign, then tailor onboarding (a tutorial for New Players, "Welcome back" for Lapsed Players). Launch data is visible in the join URL and can be shared, so tagged joins won't exactly match sponsored plays.
- **Reporting:** impressions and clicks are real time; plays and earnings can take up to 48 hours and use attribution: new users are credited to the ad for 30 days, users resurrected after 7+ days away for 7 days; a user who played under 7 days ago from another source credits only that session. Check the Recent Users and Resurrected Users views when All Users looks weak.
- Hourly impressions, clicks, and spend are available programmatically (`roblox-cloud`), so you can line ad delivery up against your own logs.

### How operators run launch campaigns (field reports)

None of this is official; amounts are ballparks from many small games.

- **Ads are a data feed, not a growth engine.** Ad players are cold traffic with lower playtime, D1, and spend than Home players (one game: 8 minutes from ads vs 19 from Home). Spend changes how fast you collect data, not the ceiling. A game that can't hold players without ads isn't saved by more ads.
- **Steady, modest, continuous.** The common baseline is around 12–20 ad credits a day for 7–14 days in one continuous campaign. Spend steadily rather than in bursts, and don't keep restarting campaigns; a new campaign re-enters a learning period and CCU bounces.
- **Learning phase.** Expect CTR to start low and climb over the first 24–48 hours as delivery finds an audience; judge CTR and cost per play after that.
- **Judge creatives on volume.** Let each thumbnail reach at least 1,000 impressions (many say 10,000) before calling it; a 1-point CTR gap is meaningful at that volume. Reports of 10%+ CTR from a few hundred impressions mean nothing.
- **Split and target.** Desktop and mobile CTR differ enough that combined campaigns blur the data. Small targeted budgets have beaten larger untargeted ones (identical thumbnails: 3–4% CTR targeted vs about 2% untargeted at twice the spend). Match creative to the actual audience.
- **Age gate mismatch.** Until a game clears Kids & Select, campaigns that target all ages waste impressions on players who can't join; restrict targeting to the eligible audience.
- **CTR ranges people cite:** under about 2% means the package or idea is the problem; 2.5–4% is typical-good; 4–6% is strong; sustained 7%+ is rare. Cost per play under about 0.005 credits is a common target.
- **When to cut spend.** A widely used heuristic: run ads until Home recommendation impressions exceed ad impressions, then cut back. Treat rising Home traffic as a reason to *test* a budget cut, not an automatic shutdown: record paid and Home plays separately with spend, mature cohort retention, and server occupancy, set a recovery threshold first, and change nothing else at the same time. A before/after comparison isn't a randomized experiment, and multiplayer games may need paid traffic just to fill servers.
- **Ad delivery can change your audience.** Delivery can shift within an hour with no edit from you (in one case CTR rose from about 2% to 6% while impressions halved at the same spend, and retention fell on an unchanged build). Compare builds only within the same CTR band (`roblox-growth-design`).
- **Trial run as a probe.** A short cheap campaign tells you whether CTR and early retention have potential before you commit a real budget.

### Ads Manager traps (field reports)

- Gambling-adjacent words in asset or ability names have held ads in review; rename and resubmit.
- Schedule campaigns at least 30 minutes ahead; very short lead times have stuck in review.
- A lifetime budget can spend most of its credits within the first hours; prefer a daily budget for launch tests.
- Moderated thumbnails can still consume spend; appeal non-policy moderation warnings promptly.
- The ads and analytics platform has had platform-wide incidents (impressions collapsing, costs spiking). Check whether other creators see the same thing before blaming your game.

### Launch trajectories (field reports)

- **Ad-driven CCU is spiky.** First campaigns often spike for minutes or hours, then settle much lower. High CCU while ads run is mostly delivery, not organic success; read post-ad numbers.
- **Algorithm pickup shows in impressions first.** Watch impressions by thumbnail; Home impressions per hour rise before CCU does. Reported ramps run roughly exponential once Home picks a game up, with spikes and drops along the way. Avoid changing thumbnails or stopping ads mid-ramp.
- **Slow starts are normal.** Several games reported about two weeks of poor stats before Home found the right audience; strong first-day numbers didn't guarantee pickup either. A spike without a reason to return is a rented audience.
- **Live-event spikes fade.** A big in-game event can multiply CCU for a day, then leave a lower baseline than before if retention is weak.
- **Organic channels.** A pre-launch community, short-form videos, livestreams, and creator coverage have launched games with no ads. Short videos need a strong hook in the first seconds and sustained posting for one to two weeks; use the game's name rather than links. Livestreams can convert better because viewers want to play with the creator. Creator-driven traffic arrives already knowing the game, so its session time overstates platform growth (`roblox-growth-design`).
- **Ratings.** Some negative votes are unavoidable (bugs, difficulty, niche gameplay). Like-to-dislike ratio reportedly matters little for Home next to playtime and retention, so don't trade playtime for like-bait.
- **Feedback.** Put a short feedback form at decision moments (level end, rebirth confirmation) and store it server-side. Decode harsh comments for the signal: boring, confusing, too hard, too easy.

## 5. Packaging: Icon, Thumbnails, Title, Description

### Official requirements

<!-- temporal: 2026-11 -->

- **Accurate, original metadata.** Roblox can reduce exposure for giveaway-led metadata, metadata that doesn't match gameplay, and non-unique games whose metadata and place files closely resemble existing games. Quality status is re-evaluated with updates; a reduced-exposure banner appears in the Creator Dashboard and updates daily.
- **Custom thumbnail required for Home.** A game with only the default thumbnail isn't eligible for Home recommendation impressions.
- **Icon:** square, at least 512×512; keep detail away from rounded corners and overlays; check it at real tile size.
- **Thumbnails:** 16:9, ideally 1920×1080, under 3 MB. Keep 2–5 active for Home personalization; the detail page can show up to 10 images or videos.
- **Promotional text** (beta) is available in publish settings.
- **Event thumbnails** should differ from game thumbnails (§3).
- **Ad creatives:** up to 10 per campaign, evenly distributed (§4).

### Thumbnail personalization (official)

1. Activate 2–5 accurate thumbnails.
2. Roblox explores them across users, then gives winners more impressions per segment while keeping some exploration.
3. Read impressions, qualified plays, average playtime, QPTR, and the winning segment per thumbnail.
4. Keep several active so personalization can adapt.
5. Test new thumbnails around a major update, then leave them alone until the next one.

The Thumbnail Personalization API manages these sets programmatically: up to 5 thumbnails per configuration, and creating a new configuration resets its statistics. The place icon can be updated through Open Cloud's Update Asset with `updateMask=icon`, and detail-page images are the `previews` list (`roblox-cloud`).

QPTR on this page means qualified plays ÷ Home recommendation impressions; Discovery's top signal is called play through rate. Don't assume every dashboard uses the same denominator.

### Creative choices (starting points, not ranking rules)

- One dominant fantasy or action; subject, action, emotion, and contrast over clutter.
- Simple backgrounds, one or two characters (three only if the composition needs it).
- High contrast: bright subjects on a clean background.
- Big, readable emotions.
- A short mechanic tease ("Steal at Night") usually says more than the game's name.
- Honest in-game content and fidelity; no tiny text or UI-like layouts.
- Mobile first: check every image at actual tile size on a phone. Desktop-detailed thumbnails often turn to mush.
- Formats that recur: before/after (noob vs pro), first-person view of the action, two characters in conflict, one character plus action, or a concept unique to the mechanic (highest risk, most differentiation).
- Ad thumbnails and Home thumbnails do different jobs; one game only got Home traction after adding a thumbnail made for the Home row.
- Outsource art only if it beats your own measured results.

Optional tools: [qptr.io](https://qptr.io) previews an icon or thumbnail beside simulated neighbors; it doesn't measure live Roblox performance. [Creator Exchange](https://creatorexchange.io) offers directional market estimates, not official analytics.

### Title and description

- **Search every candidate title first.** An exact match of a big live game sits under the original in search and reads as a clone; a small variation may have no match at all.
- **Read what a title word means now.** Before relying on a word's promise ("Sandbox," "Tycoon"), read the descriptions of live games using it; meanings drift with each trend wave. A naming pattern among breakouts is correlation, not proof the word draws players.
- **Clarity over keyword stuffing.** Use title words for searchable clarity and differentiation.
- **Retitle last.** Fix thumbnails before renaming; field reports put the retitle window at about the first two weeks, unless the name looks template-adjacent and hides your twist.
- **Description:** lead with what the player does and the fantasy, keep it accurate, and give a reason to join now (current event, a code). Keep promotional codes and links within policy (`roblox-publish-checklist`).
- **Don't clickbait.** A higher click rate with worse first-play bounce or retention is a loss; Home signals measure what happens after the click (`roblox-growth-design`).

## 6. Rewarded Video and Ad Placements

Rewarded video (full-screen ads of 6–30 seconds that grant a reward) is a monetization feature with LiveOps implications: Roblox's playbook recommends opt-in prompts at moments of need, consumable rewards, a frequency cap, and hiding ads from likely spenders. Placement and policy details: `roblox-monetization`. Test the effect on retention and spend with an experiment before rolling it out.

## 7. Traps That End Launches

- **Content-rating surprises.** The content-ratings questionnaire maps mechanics to categories (for example, chasing or hitting can count as violence). A higher rating can lock a young-skewing game out of its audience. Check how innocuous mechanics map before launch, and answer accurately; moderation checks for discrepancies (`roblox-publish-checklist`).
- **Moderation during pickup.** Field reports describe moderation warnings received while a game entered Home recommendations collapsing its traction. Fix content-risk issues before you push traffic.
- **Clones and templates.** Template-adjacent games and near-copies are documented as not prioritized; "+1" clones compete head-on with the original.
- **Inflated playtime.** AFK farms and passive loops reportedly lose distribution; inflated playtime is a liability.
- **Multiplayer-only games.** They die fast when CCU can't fill servers: add solo fallbacks, warmups, bots, or lobby activities, and avoid "waiting for players" screens.

## Sources

Official Roblox sources (reviewed 2026-11-27):

- [LiveOps essentials](https://create.roblox.com/docs/production/game-design/liveops-essentials), [LiveOps planning](https://create.roblox.com/docs/production/game-design/liveops-planning), [Content updates](https://create.roblox.com/docs/production/game-design/content-updates), [Season pass design](https://create.roblox.com/docs/production/game-design/season-pass-design)
- [Experience events and updates](https://create.roblox.com/docs/production/promotion/experience-events), [Experience notifications](https://create.roblox.com/docs/production/promotion/experience-notifications)
- [Ads Manager](https://create.roblox.com/docs/production/promotion/ads-manager), [Search ads](https://create.roblox.com/docs/production/promotion/search-ads), [Rewarded video playbook](https://create.roblox.com/docs/production/promotion/rewarded-video-playbook)
- [Experience icons](https://create.roblox.com/docs/production/publishing/experience-icons), [Thumbnails](https://create.roblox.com/docs/production/publishing/thumbnails), [Publish games and places](https://create.roblox.com/docs/production/publishing/publish-games-and-places), [Discovery](https://create.roblox.com/docs/discovery), [Discovery FAQ](https://create.roblox.com/docs/discovery-faq)
- [Content ratings](https://create.roblox.com/docs/production/promotion/content-ratings)

Field reports: community operator discussions and single-project measurements, summarized without game names. Third-party tools: [qptr.io](https://qptr.io), [Creator Exchange](https://creatorexchange.io).
