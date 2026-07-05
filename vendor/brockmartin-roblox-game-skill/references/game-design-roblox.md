# Roblox Game Design Reference

> **Load this reference when:** the conversation involves game design questions, player retention concerns, genre selection, core loop design, engagement strategy, first-time user experience, difficulty tuning, social system design, update planning, or monetization-adjacent design decisions for a Roblox game.

---

## 1. Overview

Game design on Roblox differs fundamentally from traditional game development. The platform is social-first, mobile-dominant, and session-driven. Players discover games through friends, algorithmic recommendations, and the home page -- not storefronts. Retention is king: a game that retains players climbs the algorithm, which brings more players, which funds development. Every design decision should be evaluated through the lens of "does this make a player want to come back tomorrow?"

Key platform realities that shape design:

- **Young demographic skewing older** -- the audience ranges from 8 to 25+, with the fastest-growing segment being 17-24. Design for accessibility but do not condescend.
- **Mobile dominance** -- over 60% of sessions happen on mobile. Touch controls, screen real estate, and performance constraints are first-class design considerations, not afterthoughts.
- **Short sessions, high frequency** -- average session length is 20-30 minutes. Design loops that deliver satisfaction within that window while leaving hooks for return.
- **Social discovery** -- players join games because friends are playing. Every system should have a social surface: something to show off, share, or do together.
- **Free-to-play economy** -- revenue comes from Robux purchases. Monetization must feel fair or players leave and review-bomb. Design generosity first, then offer acceleration.

---

## 2. Core Loop Design

Every successful Roblox game has three interlocking loops operating at different time scales.

### Primary Action Loop (moment-to-moment, 5-30 seconds)

This is what the player does constantly. It must feel good on its own, independent of progression.

- **Pet Simulator 99:** Tap/click to break objects, collect coins, open eggs. The screen fills with numbers, particles, and pet animations. The loop is: hit thing -> stuff flies out -> collect stuff -> hit bigger thing.
- **Blox Fruits:** Find enemy -> combo attack -> defeat -> collect XP/drops -> find next enemy. Combat feels impactful with visual feedback and skill expression.
- **Doors:** Enter room -> scan for threats -> solve puzzle/avoid entity -> proceed. Tension builds with each door opened.
- **Brookhaven:** Choose role -> enter space -> interact with props/players -> create narrative. The loop is emergent and player-driven.

Design principles for the primary loop:
- It must feel satisfying with zero progression context. Clicking things in Pet Sim feels good before you understand anything about pets or upgrades.
- Visual and audio feedback is non-negotiable. Every action needs a response: particles, screen shake, sound effects, number popups.
- The loop cadence should be fast. If more than 5 seconds pass without the player doing something meaningful, something is wrong.

### Progression Engine (session-scale, 10-30 minutes)

This is how the player grows within a single session. It answers "what am I working toward right now?"

- **Currencies and upgrades** -- earn gold to buy better tools that earn gold faster. The classic incremental loop.
- **Zone unlocking** -- reach a threshold to access a new area with new visuals, enemies, and rewards. Provides concrete milestones.
- **Equipment/pet tiers** -- acquire increasingly rare and powerful items. Each tier feels meaningfully different.
- **Skill trees/ability unlocks** -- choose how to specialize. Gives players agency in their growth path.

The progression engine must deliver a meaningful milestone within a single session. If a player plays for 20 minutes and feels like they made no progress, they will not return.

### Meta-Progression (cross-session, days to months)

This is what persists and accumulates over a player's lifetime with the game. It is the primary retention driver.

- **Account-level unlocks** -- titles, badges, profile cosmetics that signal veteran status.
- **Collection completion** -- filling out a bestiary, pet index, or achievement log. Progress toward 100% is deeply motivating.
- **Prestige/rebirth systems** -- reset progress for permanent multipliers or exclusive rewards. Extends the game's lifespan by making the journey itself repeatable with new context.
- **Social investment** -- guild rank, trade history, friend connections. The more social capital a player builds, the harder it is to leave.
- **Seasonal exclusives** -- items that were only available during a specific event. They become status symbols and conversation starters.

### How the Loops Interconnect

The primary loop feeds the progression engine (actions generate resources for upgrades). The progression engine feeds meta-progression (session milestones contribute to long-term goals). Meta-progression enhances the primary loop (permanent bonuses make moment-to-moment play feel better). This creates a flywheel: each layer makes the others more engaging.

```
Primary Loop (seconds)
    |
    v  [generates resources]
Progression Engine (minutes)
    |
    v  [contributes to long-term goals]
Meta-Progression (days/weeks)
    |
    v  [permanent bonuses enhance...]
Primary Loop (feels better) --> cycle repeats
```

---

## 3. Retention Mechanics

Retention is the single most important metric on Roblox. The algorithm rewards games that bring players back, creating a virtuous cycle of visibility and growth. Day-1 retention (D1) above 30% is good. D7 above 15% is strong. D30 above 5% is exceptional.

### Daily Login Rewards

Structure escalating value over consecutive days to punish breaks without being cruel.

- **Days 1-3:** Small but useful resources (coins, basic items). Low commitment to start the habit.
- **Days 4-6:** Moderately valuable rewards (rare materials, mid-tier eggs/crates). The streak starts feeling worth protecting.
- **Day 7:** A significant reward (exclusive pet, large currency bundle, cosmetic). This is the anchor that keeps players coming back through the mundane early days.
- **Days 8-14:** Reset the cycle but with higher base values. Optionally add a Day 14 mega-reward.
- **Day 30:** A truly exclusive reward (unique title, legendary item). This becomes a flex and social proof.

Design rules:
- Never reset the streak to zero on a single missed day. Use a "streak freeze" mechanic or simply pause progress. Punishing players for having a life breeds resentment, not loyalty.
- Show the full reward calendar so players can see what they are working toward.
- Make the login reward collection feel ceremonial: a special UI, animation, and sound.

### Limited-Time Events

Seasonal and time-limited content creates urgency and gives lapsed players a reason to return.

- **Seasonal events** (Halloween, Winter, Summer) -- themed areas, exclusive collectibles, limited-time game modes. Plan these months in advance.
- **Collaboration events** -- partner with other Roblox games or IP for crossover content. Drives cross-pollination of player bases.
- **Weekend events** -- double XP, boosted drop rates, special challenges. Low development cost, high engagement impact.

Ethical FOMO guidelines:
- Time-limited cosmetics are fine. Time-limited power is not. Players who miss an event should not be permanently weaker.
- Bring back popular event items occasionally (maybe recolored) so players do not feel punished for discovering the game late.
- Communicate event schedules clearly. Surprise events feel exciting; surprise endings feel unfair.

### Social Features That Drive Return Visits

- **Guilds/clans/groups** -- players feel obligation to their social unit. Guild goals, guild leaderboards, and guild-exclusive content make the game feel like a shared commitment.
- **Friends list integration** -- show when friends are playing. "Join friend" is one of the most powerful retention hooks on Roblox.
- **Trading** -- when players invest time building a trade portfolio, they have sunk cost keeping them in the ecosystem. Trading also creates social bonds and community identity.
- **Gifting** -- let players send items to friends. Generosity loops create reciprocal engagement.

### Collection Completion

The "gotta catch 'em all" instinct is one of the most powerful motivators in game design.

- **Visible collection progress** -- show X/Y collected with clear categories. A 73% complete collection nags at a player's brain.
- **Rarity tiers** -- common, uncommon, rare, epic, legendary, mythical. Each tier up should feel meaningfully harder to obtain but not impossible.
- **Collection bonuses** -- completing a set grants a bonus (stat boost, cosmetic, title). This incentivizes collecting the "boring" items too.
- **Index/bestiary/album UI** -- make the collection browsable, sortable, and shareable. Silhouettes for undiscovered items create curiosity.

### Streak Systems

Beyond daily logins, streaks can be applied to many mechanics:

- **Play streaks** -- consecutive days with at least N minutes played.
- **Win streaks** -- consecutive victories in competitive modes.
- **Quest streaks** -- completing daily quests without missing a day.
- **Streak multipliers** -- each consecutive day increases rewards (1x, 1.2x, 1.5x, 2x, 3x). The accelerating value makes breaking the streak feel increasingly costly.

---

## 4. Genre Theory

Each genre succeeds on Roblox for specific psychological reasons. Understanding these helps you design within a genre or innovate by combining elements.

### Simulators

**Pattern:** Collect -> Upgrade -> Unlock Zones -> Prestige

**Why it works:** Simulators tap into the "numbers going up" dopamine loop. The core satisfaction is watching your power, wealth, or collection grow visibly. Pet Simulator, Bee Swarm Simulator, and Mining Simulator all follow this template.

**Key design elements:**
- Exponential scaling -- each zone should feel like a massive jump in both challenge and reward. Going from earning 100/click to 10,000/click is inherently exciting.
- Visual power fantasy -- the player's character, pets, or tools should visibly reflect their progress. A new player and a veteran should look completely different.
- Prestige/rebirth -- when players hit the ceiling, let them reset for permanent multipliers. This turns one game into many playthroughs, each faster and more powerful than the last.
- Egg/gacha systems -- randomized rewards with visible rarity tiers. The "will I get the legendary?" moment is the emotional peak of the genre.
- AFK mechanics -- let players earn passively (at reduced rates) so they feel progress even when not actively playing. This respects time while encouraging return visits to collect accumulated rewards.

**Pitfall:** Simulators that are purely numbers with no variety become stale. Add mini-games, social events, and collection goals to break up the grind.

### Tycoons

**Pattern:** Build -> Earn -> Expand -> Automate

**Why it works:** Tycoons satisfy the empire-building fantasy. Players start with nothing and construct something visible and impressive. The satisfaction comes from spatial growth and increasing automation.

**Key design elements:**
- Visible construction -- the player's tycoon should physically grow as they invest. Walking through your own factory/restaurant/theme park is deeply satisfying.
- Automation tiers -- early game is manual. Mid game introduces helpers/machines. Late game is a self-running empire the player optimizes rather than operates.
- Customization -- let players choose layouts, colors, and decorations. Two maxed-out tycoons should look different based on player preference.
- Competition -- side-by-side tycoons where players can see each other's progress. Rivalry drives engagement.
- Income display -- always show the player how much they are earning per second/minute. Watching that number climb is the core reward.

**Pitfall:** Tycoons that are purely linear (step on pad, wall drops, step on next pad) feel dated. Modern tycoons need choice, strategy, and social elements.

### Obbys

**Pattern:** Attempt -> Fail -> Learn -> Succeed

**Why it works:** Obbys tap into skill mastery motivation. The satisfaction comes from overcoming a challenge through practiced skill, not time or spending. Each checkpoint conquered is a genuine achievement.

**Key design elements:**
- Checkpoint generosity -- frequent checkpoints reduce frustration without reducing challenge. The enemy is the obstacle, not lost progress.
- Difficulty curve -- start trivially easy, ramp gradually, spike occasionally for "boss" sections, then ease back. A sawtooth pattern with an upward trend.
- Visual variety -- change environments, mechanics, and aesthetics every 10-15 stages. Same difficulty in a new context feels fresh.
- Speedrun support -- timers, leaderboards, and ghost replays for competitive players. This extends the life of content enormously.
- Skip options -- selling stage skips for Robux is acceptable as long as the game does not artificially inflate difficulty to force purchases.

**Pitfall:** Obbys with unfair difficulty (invisible kill blocks, misleading visuals, pixel-perfect jumps without warning) feel cheap, not challenging. Difficulty should come from skill demands, not deception.

### RPGs

**Pattern:** Quest -> Fight -> Loot -> Level Up -> Explore

**Why it works:** RPGs combine narrative motivation with mechanical progression. Players grow attached to their character, invested in the story, and motivated by both what comes next and what gear drops.

**Key design elements:**
- Character identity -- classes, customization, and build variety. Players should feel that their character is unique.
- Loot anticipation -- randomized drops with visible rarity. The moment before opening a chest is more exciting than the contents.
- World design -- interconnected zones that reward exploration. Hidden areas, secret bosses, and lore fragments for dedicated players.
- Party systems -- encourage group play for dungeons and bosses. Social bonds form through shared challenges.
- Quest variety -- mix fetch quests, combat challenges, puzzles, and story quests. Repetitive quest types drain motivation.

**Pitfall:** RPGs on Roblox fail when they try to be too complex. Streamline systems, make combat feel responsive on mobile, and front-load exciting content. A 20-minute tutorial kills a Roblox RPG.

### Horror

**Pattern:** Explore -> Tension Build -> Scare -> Survive

**Why it works:** Horror games on Roblox benefit enormously from the social layer. Playing with friends transforms fear into fun. Screaming together, daring each other to go first, and laughing at jump scares creates memorable shared experiences.

**Key design elements:**
- Atmosphere first -- lighting, sound design, and environmental storytelling matter more than monster AI. A dark hallway with distant footsteps is scarier than a visible monster.
- Pacing -- horror needs rhythm. Tension must build and release. Constant scares become numbing; constant calm becomes boring. Alternate between dread and relief.
- Procedural elements -- randomized entity spawns, room layouts, or event sequences keep the game scary on repeat plays. Predictable horror is not scary.
- Social screaming -- design moments where one player's reaction triggers others'. The player who opens the door, the player who looks behind them, the player who gets separated from the group.
- Replayability through mystery -- hidden lore, multiple endings, secret rooms, and community-driven discovery (ARGs, hidden codes) extend horror games far beyond their content length.

**Pitfall:** Relying solely on jump scares. Effective horror uses dread (something bad is coming), tension (it could happen any moment), and relief (the scare passes) as a cycle. Jump scares are punctuation, not the entire sentence.

### Battle Royale

**Pattern:** Drop -> Loot -> Fight -> Survive

**Why it works:** Battle royale combines competitive tension with high stakes. Each match tells a story, and the shrinking play area forces escalating confrontation. The "one more game" pull is strong because each match is different.

**Key design elements:**
- Fast matches -- Roblox BR games should run 8-15 minutes, not 25. Session length matters.
- Skill expression -- movement mechanics, aim, building, or ability usage that separates good players from great ones.
- Loot variance -- different loadouts create different play experiences each match. The randomness is a feature, not a bug.
- Spectating -- let eliminated players watch friends. This keeps the social group engaged even when individuals are out.
- Cosmetic progression -- battle passes, ranked rewards, and win trackers give long-term goals beyond individual matches.

**Pitfall:** Matchmaking is critical and hard on Roblox. New players getting destroyed by veterans kills retention. Consider skill-based lobbies, bot backfill for low-skill matches, or protected beginner brackets.

---

## 5. First-Time User Experience (FTUE)

The FTUE is the most important 60 seconds of your game's existence. Most players who leave in the first minute never return. Every second of the FTUE must be intentional.

### The First 30 Seconds

The player should understand what this game is and experience the core loop within 30 seconds of joining.

- **Immediate context** -- the player should know where they are and what they are supposed to do without reading anything. Visual language (arrows, glowing objects, NPC gestures) over text.
- **First action within 5 seconds** -- do not make the player wait through loading screens, cutscenes, or UI pop-ups before they can do something. Let them move, click, or interact immediately.
- **First reward within 15 seconds** -- the player should earn something (coins, an item, XP) almost instantly. This establishes the reward loop and sets expectations.
- **First "wow" moment within 30 seconds** -- a visual spectacle, a surprising interaction, or a satisfying feedback moment that makes the player think "this is cool."

### Minimal Tutorial

- **Learn by doing** -- do not explain mechanics with text walls. Put the player in a situation where the only option is the correct action. A room with one door teaches "walk through doors" better than a tooltip.
- **Contextual hints** -- show control hints when relevant, not all at once. Show "tap to attack" when an enemy appears, not during a menu screen.
- **Fail safely** -- early challenges should be impossible to fail, or failure should have no cost. Let players experiment without anxiety.

### Progressive Disclosure

Do not show the player everything at once. A screen full of UI, currencies, shops, and systems is overwhelming and causes immediate exit.

- **Wave 1 (0-5 minutes):** Core loop only. One currency, one action, one goal.
- **Wave 2 (5-15 minutes):** Introduce the first upgrade path and a secondary mechanic.
- **Wave 3 (15-30 minutes):** Open up social features, the shop, and secondary currencies.
- **Wave 4 (30+ minutes):** Reveal advanced systems, guilds, trading, prestige.

### Clear First Objective

The player should always know what to do next. A quest tracker, arrow, or highlighted objective prevents the "now what?" moment that kills engagement.

- Make the first objective trivially easy ("collect 10 coins").
- Make the second objective slightly harder but still obvious ("buy your first pet").
- Make the third objective introduce a new mechanic ("explore the second zone").

### Immediate Reward

The first reward should feel disproportionately generous. Give the player a taste of what the game feels like when you are invested.

- A free starter pet/item that is visually exciting (not the boring gray default).
- A burst of currency that lets them immediately make a meaningful purchase.
- An early achievement/badge that validates their decision to try the game.

---

## 6. Difficulty Design

Getting difficulty right is the difference between a game that feels challenging and one that feels unfair. Roblox's broad audience makes this especially important.

### Difficulty Curves

- **Gradual ramp, not sudden spikes** -- difficulty should increase smoothly with occasional plateaus for the player to feel powerful. A sudden spike feels like a paywall or bug, not a challenge.
- **Sawtooth pattern** -- within each zone/world/chapter, start slightly easier than the previous zone's end, then ramp up to a new peak. This "reset and climb" pattern keeps players in flow.
- **Boss encounters** -- significant difficulty spikes are acceptable for bosses IF the player has been trained on the required skills and the reward matches the challenge.

### Skill-Based vs. Time-Based Progression

Every game exists on a spectrum between "you succeed because you are skilled" and "you succeed because you spent enough time."

- **Skill-heavy** (obbys, competitive): Respect player mastery. Do not gate skilled players behind time walls. Offer harder content, not more grind.
- **Time-heavy** (simulators, tycoons): Respect player time. Make progress feel meaningful per session. Do not require 100 hours to reach interesting content.
- **Hybrid** (RPGs, action games): Use skill to accelerate time-based progress. Skilled players clear content faster, but patient players still succeed.

### Avoiding Frustration

Frustrated players quit. Challenge motivates; frustration does not. The difference is whether the player understands why they failed and believes they can succeed.

- **Clear failure feedback** -- the player should always know what killed them and what to do differently.
- **Hints after repeated failure** -- if a player fails 3+ times, offer a subtle hint. After 5+ failures, offer a more direct hint or assistance option.
- **Skip options** -- for non-competitive content, let players skip with a time cost, currency cost, or ad watch. Never make skipping feel mandatory through artificial difficulty.
- **Difficulty settings** -- consider easy/normal/hard modes or adaptive difficulty that scales based on player performance. Not every game needs this, but broad-audience games benefit.

### Rewarding Mastery

Players who invest time developing skill should feel recognized.

- **Speed records** -- personal bests and leaderboards for time-based challenges.
- **Perfect run bonuses** -- extra rewards for no-death, no-hint, or no-damage completions.
- **Style/combo systems** -- reward creative or difficult play with multipliers.
- **Visible mastery indicators** -- titles, auras, or cosmetics that show other players "this person is skilled."

---

## 7. Social Systems

Roblox is a social platform that happens to have games, not a game platform that happens to be social. Every design decision should consider the social dimension.

### Why Social Matters

- **Discovery** -- the number one way players find games is through friends. A game with strong social features spreads organically.
- **Retention** -- players who form social bonds in a game are dramatically less likely to leave. The game becomes the place where their friends are.
- **Session length** -- social interaction extends play sessions. Players who would solo for 15 minutes will stay 45 minutes with friends.
- **Content generation** -- players create stories, drama, and experiences for each other. Social features multiply the value of your content.

### Multiplayer Interaction Design

- **Positive-sum interactions** -- design mechanics where helping others also helps you. Cooperative boss fights with shared loot. Group buffs that scale with party size.
- **Ambient social** -- even solo players should see and be seen by others. Shared spaces, visible achievements, and cosmetic expression create a sense of community without requiring interaction.
- **Opt-in competition** -- PvP and competitive features should be opt-in or zone-based, not forced. Players who want to compete should find each other; players who don't should not be victims.

### Guilds/Groups

- **Low barrier to entry** -- joining a guild should be easy. Creating one should be slightly harder.
- **Guild goals** -- weekly/monthly objectives that require collective effort. This creates mutual obligation and communication.
- **Guild progression** -- the guild itself levels up, unlocking perks for all members. This gives members a reason to stay and contribute.
- **Guild identity** -- custom names, logos, colors, and base areas. Pride in the group drives engagement.

### Leaderboards

- **Multiple leaderboards** -- all-time, weekly, daily, and friend-only boards. Players who can't compete globally can still compete locally.
- **Diverse metrics** -- total score, best run, collection completion, PvP rank, most helpful. Different leaderboards let different player types shine.
- **Visible but not oppressive** -- show leaderboards in the game world (hall of fame, statues) but do not force them in players' faces. Players who are motivated by competition will seek them out.
- **Anti-cheating** -- leaderboard integrity matters. A hacked leaderboard demotivates legitimate players.

### Cooperative Mechanics

- **Team dungeons/raids** -- content designed for groups of 2-6 players with complementary roles. This is one of the strongest social bonding experiences in gaming.
- **Shared goals** -- server-wide objectives (kill 10,000 enemies collectively to unlock a bonus) create a sense of community purpose.
- **Mentorship** -- give veterans incentives to help new players. Both benefit: the veteran gets rewards, the new player gets guidance.
- **Asymmetric cooperation** -- different players contribute different things (one mines, another builds, another defends). Interdependence creates social bonds.

### Trading as Social Glue

Trading is one of the most powerful social systems in Roblox games. It creates an economy, a social scene, and a metagame simultaneously.

- **Scarcity drives value** -- limited items create a functioning economy. Items must be rare enough to want but not so rare that trading is impossible.
- **Trading hubs** -- designated spaces for trading create social gathering points and emergent community.
- **Scam prevention** -- trade confirmation screens, value estimates, and trade history protect players and build trust in the system.
- **Trade chat/offers** -- let players advertise what they want and what they have. The negotiation itself is a game within the game.

---

## 8. Update Strategy

A live-service Roblox game must be continuously updated to maintain and grow its player base. The update cadence should be predictable, communicated clearly, and strategically planned.

### Content Cadence

- **Weekly (small):** Bug fixes, balance adjustments, quality-of-life improvements, minor new content (a new item, a daily challenge refresh). These show the game is alive and actively maintained.
- **Monthly (medium):** New feature additions, new zones or areas, new mechanics, significant content drops (new pets, new equipment tier, new quest line). These give players a reason to return and a reason for content creators to make videos.
- **Quarterly (big):** Major content updates, seasonal events, new game modes, system overhauls. These are marketing moments -- coordinate with content creators, social media, and community events.

### Seasonal Events

Plan seasonal events well in advance:

- **Pre-production (2-3 months before):** Concept, theme, exclusive items, event mechanics.
- **Production (1-2 months before):** Building, testing, balancing.
- **Hype phase (1-2 weeks before):** Teasers, countdown timers, community speculation.
- **Event launch:** Monitor server stability, engagement metrics, and community feedback.
- **Post-event:** Analyze what worked, preserve exclusive items in players' inventories, plan next event.

Major seasonal windows on Roblox: Halloween (October), Winter/Holiday (December-January), Valentine's (February), Easter/Spring (March-April), Summer (June-August), Back to School (August-September).

### Community Feedback Loops

- **DevForum** -- monitor the Roblox Developer Forum for bug reports, feature requests, and general sentiment about your game.
- **Discord** -- maintain an active Discord server with channels for suggestions, bug reports, and general discussion. Respond to feedback visibly.
- **In-game feedback** -- simple rating systems, suggestion boxes, or polls within the game. Low-friction feedback captures opinions from players who do not use external platforms.
- **Content creator relationships** -- YouTubers and streamers who play your game are both marketing and a feedback source. Their audiences amplify both praise and criticism.

### Feature Prioritization

When deciding what to build next, prioritize in this order:

1. **Critical bugs and exploits** -- always first. A broken game loses players faster than a stale one.
2. **Retention features** -- anything that makes existing players come back (daily rewards, social features, collection goals).
3. **New player experience** -- improvements to FTUE, onboarding, and accessibility. A wider funnel feeds the whole game.
4. **Content additions** -- new zones, items, and mechanics that extend playtime for engaged players.
5. **Monetization** -- new things to buy should come after the game is worth buying things in. Monetization built on a healthy game prints money; monetization forced into a struggling game accelerates decline.

---

## 9. Best Practices

### Test with Real Players Early

Do not wait until the game is "done" to show it to players. Roblox makes this easy: publish a beta, invite playtesters, and watch what they do.

- Watch new players without guiding them. Where do they get confused? Where do they get bored? Where do they leave?
- If you have to explain something, the design needs to communicate better.
- Track quantitative data (session length, drop-off points, purchase rates) alongside qualitative feedback (fun, confusion, frustration).

### Iterate on Analytics Data

Roblox provides analytics. Use them.

- **Session length** -- if average session length is under 10 minutes, the core loop is not engaging enough.
- **D1/D7/D30 retention** -- track these religiously. If D1 drops, your FTUE is broken. If D7 drops, your progression is too slow or too fast. If D30 drops, your endgame lacks depth.
- **Monetization per session** -- this tells you if players feel the game is worth spending in, not just playing.
- **Drop-off points** -- where do players quit? Map this to game content and fix the weak points.

### Balance Depth and Accessibility

The best Roblox games are "easy to learn, hard to master." A new player and a 1,000-hour veteran should both find something to enjoy.

- Surface-level simplicity: anyone can understand the core loop in seconds.
- Hidden depth: experienced players discover advanced strategies, optimizations, and build paths over time.
- Multiple engagement modes: casual players have fun playing 10 minutes. Hardcore players have fun optimizing for 10 hours.

### Respect Players' Time

Players are choosing to spend their limited time in your game. Honor that choice.

- Every session should deliver progress. Even a 5-minute session should yield something.
- Do not waste time with unnecessary animations, loading screens, or forced waits that serve no design purpose.
- AFK rewards at reduced rates are better than zero -- they acknowledge that life exists outside the game.
- If something takes a long time, clearly communicate the expected duration so players can plan.

### Make the First Minute Amazing

The first minute determines whether a player ever comes back. Invest disproportionate effort into this window.

- Frontload spectacle. The most visually impressive moment should happen early, not after hours of play.
- Give instant gratification. A quick reward, a cool item, a satisfying interaction.
- Create curiosity. Show the player something they cannot yet access -- a locked door, a high-level player's equipment, a teased zone in the distance.
- Remove all friction. No mandatory account linking, no required name entry, no forced tutorials. Let the player play.

---

## 10. Anti-Patterns

These are common design mistakes that kill Roblox games. Avoid them.

### Infinite Grind with No Variety

The problem: the player does the same action for hours with only numbers changing. No new mechanics, no new visuals, no new challenges -- just bigger numbers.

Why it fails: even players who enjoy grinding need novelty. The numbers stop feeling meaningful when the action is monotonous. Introduce new mechanics, areas, and challenges at regular intervals to keep the core loop fresh.

### Pay-to-Win

The problem: paying players have a significant competitive advantage over non-paying players in competitive contexts.

Why it fails: competitive integrity is sacred. When a player loses because their opponent spent money, not because they were better, the game feels unfair. In competitive or PvP games, monetization must be cosmetic-only or convenience-only (time savers that do not affect PvP). Even in PvE games, pay-to-win creates a sense of inequity that erodes community trust.

### Neglecting Mobile

The problem: the game is designed for PC first with mobile as an afterthought (or ignored entirely).

Why it fails: over 60% of Roblox players are on mobile. If your game is unplayable or significantly worse on mobile, you are locking out the majority of your potential audience.

- Test on mobile from day one.
- Design UI for thumb reach, not mouse precision.
- Simplify controls for touch. If a mechanic requires five simultaneous inputs, redesign it.
- Optimize performance. Mobile devices have less memory and weaker GPUs. Target 30fps on mid-range phones minimum.

### No Social Features

The problem: the game is a purely solo experience with no meaningful player interaction.

Why it fails: Roblox is a social platform. A game without social features is fighting against the platform's fundamental nature. Players discover games through friends, stay for social bonds, and leave when they feel alone.

Even primarily solo games should have: visible other players, leaderboards, chat, cosmetic expression, and at minimum the ability to invite and play alongside friends.

### Copying Without Understanding

The problem: cloning a successful game's surface-level features without understanding why those features work.

Why it fails: every successful game has an invisible design layer -- the tuning, the pacing, the emotional arc, the balancing -- that is not visible from playing. Copying Pet Simulator's egg system without understanding its drop rate curves, its dopamine pacing, or its long-tail collection design produces a hollow imitation that players see through immediately.

Study successful games deeply. Understand the principles behind the features. Then apply those principles to your unique vision instead of photocopying someone else's.

---

## Quick Reference: Design Checklist

Before launching or updating a Roblox game, verify:

- [ ] Core loop is satisfying within 10 seconds of first play
- [ ] First meaningful reward happens within 30 seconds
- [ ] A new player knows what to do without reading text
- [ ] Mobile experience is tested and functional
- [ ] At least one social feature is present (even if simple)
- [ ] Session delivers progress within 15-20 minutes
- [ ] A reason to return tomorrow exists (daily reward, streak, unfinished goal)
- [ ] Monetization is optional and does not feel required for fun
- [ ] Performance is acceptable on mid-range mobile devices
- [ ] No dead-end states where the player is stuck with no clear path forward
