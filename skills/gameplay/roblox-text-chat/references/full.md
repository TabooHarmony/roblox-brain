# Roblox Text Chat: Full Reference

> **Code in this reference is illustrative. Adapt to your game and verify in Studio, with two clients, before production use.**

<!-- temporal: 2026-11 --> Chat policy and APIs moved quickly in late 2026 (platform-integrated chat, Quick Words, temporary text limits). Recheck the linked pages before relying on a date or limit.

## 1. Classify every text surface first

Roblox's chat guidelines split player-visible text into three kinds. Classify each surface before writing code, because the rules differ.

| Kind | Examples | Rule |
| :-- | :-- | :-- |
| **Chat** | chat window and bubbles, direct and team messages, custom chat UIs, radios, phones, messaging screens, admin tools that let people message each other, any field players can use to talk to each other in under 60 seconds | Must go through `TextChatService`. It applies privacy settings, age-based limits, filtering and abuse reporting for you. |
| **Editable text others can see** | signs, pet names, licence plates, bulletin boards, item names, comments | Allowed if it is filtered and limited to one submission per player per minute. Comments may not have replies; replies are conversation. |
| **Developer-set text** | menus, round status, one-way announcements, moderation logs | Static text you write needs no filtering. If several users can use it to talk, or admins chat through it, it counts as chat. |
| **Presets** | callout wheels, quick phrases | Must follow the preset guidelines; by May 2027 any preset phrases players use (especially in chat) must go through Quick Words. |

If players can converse in your game outside `TextChatService`, Roblox may take the game down. When that happens, remove or rate-limit the surface, then appeal and describe the change (replies typically take one to two weeks, per the guidelines page). Filtering alone is not enough: it does not stop a surface being used to talk, which is why the one-minute limit exists.

Users who repeatedly send violating messages are warned and then temporarily blocked from sending, by Roblox, without your code.

## 2. How TextChatService delivers a message

The objects:

- `TextChannel`: carries messages from client to server and on to receivers. Must be parented under `TextChatService`. With `CreateDefaultTextChannels = true` you get `RBXGeneral` and `RBXSystem`, and more default channels such as team and whisper channels appear as needed. Two channels with the same name confuse the default window.
- `TextSource`: one user's membership in one channel, with their permissions there. `TextChannel:AddUserAsync` creates it.
- `TextChatMessage`: sender, text, filtered text, timestamp, `Metadata`, status.
- `TextChatCommand`: a command matched by alias, parented under `TextChatService`. `CreateDefaultCommands = true` adds the default ones (mute, emotes, help, whisper, team and others).
- Configuration singletons: `ChatWindowConfiguration`, `ChatInputBarConfiguration`, `ChannelTabsConfiguration`, `BubbleChatConfiguration`.

The flow (client → server → receivers):

1. The sender calls `TextChannel:SendAsync()` (the default input bar does this). If the text matches a `TextChatCommand`, that command's `Triggered` fires and the message stops there unless the command delivers it.
2. Otherwise `TextChatService.SendingMessage` shows it to the sender immediately, and the message goes to the server.
3. On the server, `TextChannel.ShouldDeliverCallback` runs for each `TextSource` to decide who receives it.
4. The server filters it per receiver. `OnIncomingMessage` then fires on the sending client (replacing the local copy with the processed one through `MessageReceived`) and on each receiving client.

**Every callback must be non-yielding.** Yielding inside one blocks the chat system. Cache anything you need (attributes, team, role) before the callback runs.

| Callback | Where | Returns |
| :-- | :-- | :-- |
| `TextChannel.ShouldDeliverCallback` | server only | boolean |
| `TextChatService.OnIncomingMessage` | client only | `TextChatMessageProperties` |
| `TextChannel.OnIncomingMessage` | client only | `TextChatMessageProperties` |
| `TextChatService.OnBubbleAdded` | client only | `BubbleChatMessageProperties` |
| `TextChatService.OnChatWindowAdded` | client only | `ChatWindowMessageProperties` |

Client callbacks only change display. They are never a permission check: a modified client can skip them. Decide who receives what in `ShouldDeliverCallback` on the server, and validate anything a command does on the server (`roblox-security`).

## 3. Channels and delivery rules

### Custom channels (teams, squads, radios)

Create channels on the server, add the right users, and keep membership in sync with your game state. Radios and phones are chat, so they must be `TextChatService` channels, not a custom remote and label.

```luau
-- Server: one channel per squad, membership follows a "Squad" attribute.
-- Illustrative: adapt names and membership rules to your game.
local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local channels: { [string]: TextChannel } = {}

local function getChannel(squad: string): TextChannel
	local existing = channels[squad]
	if existing then
		return existing
	end
	local channel = Instance.new("TextChannel")
	channel.Name = "Squad_" .. squad
	channel.Parent = TextChatService
	channels[squad] = channel
	return channel
end

local function removeFromAll(player: Player)
	for _, channel in channels do
		for _, source in channel:GetChildren() do
			if source:IsA("TextSource") and source.UserId == player.UserId then
				source:Destroy()
			end
		end
	end
end

local function assign(player: Player)
	removeFromAll(player)
	local squad = player:GetAttribute("Squad")
	if typeof(squad) == "string" and squad ~= "" then
		local ok, err = pcall(function()
			getChannel(squad):AddUserAsync(player.UserId)
		end)
		if not ok then
			warn("Squad chat join failed:", err)
		end
	end
end

Players.PlayerAdded:Connect(function(player)
	player:GetAttributeChangedSignal("Squad"):Connect(function()
		assign(player)
	end)
	assign(player)
end)
Players.PlayerRemoving:Connect(removeFromAll)
```

`AddUserAsync` yields and can fail; call it outside chat callbacks and handle the failure. Users can only chat in a channel if their own settings and age-based rules allow it, which `TextChatService` applies on top of your membership.

### Conditional delivery (proximity, dead players, spectators)

`ShouldDeliverCallback` runs on the server for every receiver. Keep it cheap and non-yielding: read cached positions or state, not anything that waits.

```luau
-- Server: proximity chat on the general channel. Illustrative.
local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local RANGE = 60
local general = TextChatService:WaitForChild("TextChannels"):WaitForChild("RBXGeneral") :: TextChannel

local function rootPosition(userId: number): Vector3?
	local player = Players:GetPlayerByUserId(userId)
	local character = player and player.Character
	if character then
		return character:GetPivot().Position
	end
	return nil
end

general.ShouldDeliverCallback = function(message: TextChatMessage, receiver: TextSource): boolean
	local sender = message.TextSource
	if not sender then
		return true -- system messages
	end
	local a = rootPosition(sender.UserId)
	local b = rootPosition(receiver.UserId)
	if not a or not b then
		return false
	end
	return (a - b).Magnitude <= RANGE
end
```

Tell players the rule (a range ring, "nearby" in the tab name), or messages that silently fail to arrive read as a broken chat.

### Direct (private) chat

A custom private conversation between specific users must be marked with `TextChannel:SetDirectChatRequester()` (server only). Called on a channel with no `TextSource`s yet, it adds the requester and sets `DirectChatRequester`, and afterwards only messages between users who can direct-chat with the requester are delivered. Check eligibility first with `TextChatService:CanUsersDirectChatAsync()` and hide the "message" button for pairs who can't.

### Can these players chat at all?

- `TextChatService:CanUserChatAsync(userId)` and `CanUsersChatAsync(a, b)` tell you whether chat is possible, so the UI can hide chat buttons rather than show dead ones.
- `TextChatService:GetChatGroupsAsync()` (server only) returns chat group ids for many players at once; players sharing an id can chat together. It is meant for matchmaking and teleport grouping, avoids N² pairwise checks, needs **Chat & Voice Groups APIs** enabled in Experience Settings > Communication, and its ids must not be stored after the players leave.

## 4. Commands

- `PrimaryAlias` and optional `SecondaryAlias`; matching is case-insensitive, and the primary alias wins when both match.
- `Enum.TextChatCommandMatchMode`: `StartsWith` (the default: the alias then end of message or a space, so `/e` matches `/e dance` but not `/emote`), `Exact` (whole message equals the alias) and `WholeWord` (the alias as its own word anywhere). `Exact` and `WholeWord` skip aliases shorter than two bytes. The class page describes `MatchMode` and a `DeliverMessage` option (when false, a matched message is not delivered to others); check they are present in your Studio's property list before depending on them.
- `Triggered(originTextSource, unfilteredText)` fires on **the sending client and the server**, not on other clients. The text is unfiltered: never show it to other players without filtering.
- `AutocompleteVisible` and `Enabled` control the input bar suggestion and whether the command works.

Because `Triggered` also fires on the sender's client, put authority on the server copy of the handler and keep the client copy for local feedback only.

```luau
-- Server: an admin-only /endround command. Illustrative.
local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local command = Instance.new("TextChatCommand")
command.Name = "EndRoundCommand"
command.PrimaryAlias = "/endround"
command.AutocompleteVisible = false
command.Parent = TextChatService

local function isAdmin(player: Player): boolean
	return player:GetAttribute("IsAdmin") == true -- set by your server-side role system
end

command.Triggered:Connect(function(source: TextSource, _text: string)
	local player = Players:GetPlayerByUserId(source.UserId)
	if not player or not isAdmin(player) then
		return
	end
	-- end the round through your round service here
end)
```

Admin commands that only make one-way announcements are developer-set text; admin tools that let admins or players talk to each other are chat.

## 5. Customizing what players see

Display callbacks run per message on each client. Return a new properties object, or `nil` to leave the message as it is.

```luau
-- Client: chat tags and name colours from player attributes (set on the server).
-- Illustrative; replaces the legacy SetExtraData pattern.
local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local config = TextChatService.ChatWindowConfiguration

TextChatService.OnChatWindowAdded = function(message: TextChatMessage)
	local source = message.TextSource
	if not source then
		return nil
	end
	local player = Players:GetPlayerByUserId(source.UserId)
	if not player then
		return nil
	end
	local properties = config:DeriveNewMessageProperties()
	local nameColor = player:GetAttribute("NameColor")
	if typeof(nameColor) == "Color3" then
		properties.PrefixTextProperties = config:DeriveNewMessageProperties()
		properties.PrefixTextProperties.TextColor3 = nameColor
	end
	if player:GetAttribute("IsModerator") == true then
		properties.PrefixText = "<font color='#56B4E9'>[Mod]</font> " .. message.PrefixText
	end
	return properties
end
```

- `OnChatWindowAdded` styles the window only; `OnBubbleAdded` styles bubbles only.
- The default UI uses rich text. Rich text has no gradients; a `UIGradient` parented to the prefix text properties can colour a prefix.
- Default system messages are localized, so match them by `TextChatMessage.Metadata`, not by their text.
- Prefixes and message text are not available to code under platform-integrated chat (section 10). Plan role display around that.

### System and NPC messages

- `TextChannel:DisplaySystemMessage(text, metadata?)` shows a local message on one client (a guide line, a round notice). It is not filtered: static developer text is fine, but filter any player-supplied part (a pet name in "X joined") before including it (`roblox-networking`).
- To make a message look like it came from an NPC, pass a speaker name as metadata and style it in `OnIncomingMessage`, optionally adding a bubble with `DisplayBubble`.

## 6. Bubble chat

- Enable with `BubbleChatConfiguration.Enabled`. Common properties: `BubbleDuration`, `MaxBubbles`, `MaxDistance`, `MinimizeDistance`, `BubblesSpacing`, `TailVisible`, `TextColor3`, `TextSize`, `FontFace`, `BackgroundColor3`, `BackgroundTransparency`, `VerticalStudsOffset`, `LocalPlayerStudsOffset`, `AdorneeName`.
- Advanced looks: add an `ImageLabel` (background image, slice), `UIGradient`, `UICorner` or `UIPadding` as children of `BubbleChatConfiguration`.
- Per bubble: `TextChatService.OnBubbleAdded = function(message, adornee)` returns `BubbleChatMessageProperties`; children added to it override the same advanced settings for that bubble only. Don't yield inside it (read cached attributes).
- NPC lines: `TextChatService:DisplayBubble(partOrCharacter, text)` works only from client scripts. Trigger it from a client listener (for example a `ProximityPrompt.Triggered` connection in a LocalScript). `BubbleDisplayed` fires when a bubble shows.
- Bubbles sit in world space; check they don't hide prompts or nameplates at close range on phones.

## 7. Editable text others can see

Signs, pet names, plates, boards and item names are allowed when they are filtered on the server and limited to one submission per player per minute.

```luau
-- Server: filtered, rate-limited sign text. Illustrative.
local Players = game:GetService("Players")
local TextService = game:GetService("TextService")

local RATE_SECONDS = 60
local MAX_LENGTH = 60
local lastSubmit: { [number]: number } = {}

local function setSignText(player: Player, sign: TextLabel, raw: string): (boolean, string?)
	if typeof(raw) ~= "string" or #raw == 0 or #raw > MAX_LENGTH then
		return false, "invalid"
	end
	local now = os.clock()
	local last = lastSubmit[player.UserId]
	if last and now - last < RATE_SECONDS then
		return false, "wait"
	end
	lastSubmit[player.UserId] = now -- counts even if filtering fails
	local ok, result = pcall(function()
		return TextService:FilterStringAsync(raw, player.UserId, Enum.TextFilterContext.PublicChat)
	end)
	if not ok then
		return false, "filter-failed" -- never fall back to unfiltered text
	end
	local okText, filtered = pcall(function()
		return result:GetNonChatStringForBroadcastAsync()
	end)
	if not okText then
		return false, "filter-failed"
	end
	sign.Text = filtered
	return true, nil
end

Players.PlayerRemoving:Connect(function(player)
	lastSubmit[player.UserId] = nil
end)

return setSignText
```

- Filter on the server with the author's user id. `GetNonChatStringForBroadcastAsync` suits text everyone sees; `GetNonChatStringForUserAsync(toUserId)` filters for one viewer; `GetChatForUserAsync` is for chat-like messages to a specific user.
- When filtering fails, show nothing or a placeholder, never the raw text.
- Validate the remote (type, length, rate) before calling the filter (`roblox-networking`).
- Players can edit freely in their own text box; only the submission others see is limited. The one-minute rule frustrates fast-iteration features (one DevForum thread from 2026-10 objected to it: https://devforum.roblox.com/t/important-textchatservice-updates-how-to-test-and-what%E2%80%99s-next/4948433), so design around it: preview locally, submit once.

### Temporary text limits

<!-- temporal: 2026-11 --> When Roblox detects players holding conversations through a surface other than `TextChatService`, it temporarily limits the game's text features. While the limit is active, every feature that collects text, filters it and shows it to others is limited to one submission per player per 60 seconds, and over-limit text shows as ⏱️⏱️⏱️. You'll see notices on the game's Creator Hub page and an email to the owner. The limit lasts at least 24 hours and needs a game update before it lifts, and it can return if the behaviour continues. A Roblox weekly recap said enforcement of the 60-second non-chat text rule began on December 3, 2026 (https://devforum.roblox.com/t/weekly-recap-november-16%E2%80%9320-2026/4998199). Treat a limit as a bug report: find the surface people are using to talk, rate-limit or remove it, then publish.

## 8. Presets and Quick Words

Preset systems let players send fixed phrases to coordinate gameplay. They must express immediate gameplay intent ("Need help", "Reloading", "Enemy nearby"), not conversation ("Where are you from?", "Do you like me?"), and must not gain meaning when combined or sequenced (no alphabet or number wheels). If a custom preset system is used, the guidelines require it to be labelled as a system preset in chat, visually distinct from free chat, without terminal punctuation, passed through `TextService:FilterStringAsync`, rate-limited to one send per 10 seconds, and limited to 12 or fewer presets per universe.

**Quick Words** is Roblox's built-in, compliant preset system; prefer it over building your own.

- Creator Hub > your game > **Configure > Chat > Quick Words**.
- Up to three custom categories with three to ten Quick Words each, each under 25 characters. Custom categories replace the default ones, but **General** stays available.
- Enter them in English; Roblox translates them into each player's chat language.
- Publishing sends them for review: **Draft**, **Pending**, **Not approved** (revise and publish again) or **Published**. Approved words appear in the **Here** and **Global** chat tabs. You can save a draft or revert to the defaults.
- By May 2027 any presets players use must go through Quick Words. Under platform-integrated chat, presets sent with `TextChannel:SendAsync()` are unsupported, so a custom wheel has to move to Quick Words.

## 9. Cross-server chat

Cross-server chat adds a **Global** tab next to **Here**, connecting players across servers in the same universe. Roblox groups servers by age, language and occupancy; each global channel holds about 200 users, and fast senders are throttled (messages drop). It is on by default and can be turned off in Creator Dashboard > Audience > Communication Settings. The Global tab is disabled in private servers. It supports `/mute`, `/unmute`, `/help` and `/clear`. The Global channel can't be the target of a custom `TextChannelWindow`.

## 10. Platform-integrated chat

<!-- temporal: 2026-11 --> **Starting in May 2027, platform-integrated chat will be required for all games**; the unsupported APIs will be deprecated and custom chat must use the new `TextChatService` features. Nothing changes until you enable it, so you can migrate and test early.

When enabled:

- Roblox delivers and renders chat in the default window or in `TextChannelWindow`s you place. Custom UIs can no longer render messages themselves.
- Player message content is not available to any code, on client or server: you can't read, log or export it. APIs that returned message text return `""` (not `nil`) and log a warning, so scripts keep running with no content.
- Developer `TextChatService.OnIncomingMessage` and `TextChannel.OnIncomingMessage` callbacks are not invoked.
- Commands triggered from chat must be `TextChatCommand`s.

| Feature | Unsupported | Use instead |
| :-- | :-- | :-- |
| Messages and display | `TextChatMessage.Text`, `TextChatMessage.Translation` | `TextChannelWindow` with `Target` set to a `TextChannel` |
| Prefixes | `TextChatMessage.PrefixText` | Not supported; don't enable yet if your game needs prefixes |
| Presets, chat wheels | `TextChannel:SendAsync()` | Quick Words |
| Moderation, admin commands | `TextChatService.OnIncomingMessage`, `Player.Chatted` | `TextChatCommand`; read-only chat for moderators during live events |

### Enabling and testing

`TextChatService.PlatformIntegratedChat` is a `RolloutState` with `RobloxScript` security: set it to **Enabled** in Studio's Properties panel, not from a script. You can set it back to **Disabled** at any time. Games using the default chat with no customization need no changes. Signs, boards, notes, mail and comment systems are not affected by this switch; they still follow the editable-text rules.

### TextChannelWindow

- A `GuiObject` that renders one `TextChannel`'s messages. Place it under a `ScreenGui` (or another `LayerCollector`) and set `Target`. Setting `Target = nil` shows nothing.
- `ChatWindowConfiguration` properties don't apply to it; it has its own `FontFace` and `UseDefaultFont`.
- It accepts only `UICorner`, `UIAspectRatioConstraint`, `UISizeConstraint` and scripts as children.
- To show several channels, make one window per channel and switch between them yourself.
- By default the main window also shows every channel. To keep a custom channel only in its own window, set `ChatWindowConfiguration.TextChannelDisplayMode` to `DefaultTextChannels` (Studio or plugin only; scripts can read it). The platform-integrated chat guide documents this property, but it was not yet in the API reference on 2026-11-27, so confirm it in your Studio's Properties panel. Default channels created at runtime, such as team and whisper, still appear in the main window.

```luau
-- Client (LocalScript in StarterPlayerScripts): a squad radio window.
-- Prerequisite: TextChannelDisplayMode = DefaultTextChannels, set in Studio.
local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")
local channel = TextChatService:WaitForChild("Squad_Alpha", 30)

if channel and channel:IsA("TextChannel") then
	local screen = Instance.new("ScreenGui")
	screen.Name = "RadioChat"
	screen.ResetOnSpawn = false
	screen.Parent = playerGui

	local window = Instance.new("TextChannelWindow")
	window.Size = UDim2.fromOffset(320, 200)
	window.Position = UDim2.new(1, -330, 1, -260)
	window.Target = channel
	window.Parent = screen
end
```

Lay the window out with the same safe-area and mobile rules as any HUD (`roblox-gui`).

### What this means for design

- Roleplay radios, phones and faction chat should become `TextChannel`s with `TextChannelWindow`s, each bound to one channel; a radio that needs a custom look beyond the allowed children isn't possible under this model. Several DevForum posts (2026-10-21) objected to these limits for roleplay radios and fully custom chat UIs (https://devforum.roblox.com/t/important-textchatservice-updates-how-to-test-and-what%E2%80%99s-next/4948433); check that thread and the docs for changes before designing around them.
- Anything that inspects message text (keyword triggers, chat logs, swear counters, "type the answer in chat" games) must move to `TextChatCommand`s or a non-chat input (a filtered, rate-limited submission box, or buttons).
- Role prefixes and tags aren't supported yet; the docs say to hold off enabling if you need them.

## 11. Migrating from legacy Chat

The legacy `Chat` service is deprecated; `TextChatService` is the supported system. To switch: select `TextChatService` in Explorer and set `ChatVersion` to `TextChatService`.

| Legacy | TextChatService |
| :-- | :-- |
| Chat modules, `ChatService` speakers | `TextChannel`, `TextSource` |
| `Speaker:SetExtraData` (name colour, tags) | Player attributes plus `OnChatWindowAdded` / `OnBubbleAdded` |
| `Chat:Chat(part, text)` bubbles | `TextChatService:DisplayBubble` (client) |
| Manual chat filtering | Automatic per-receiver filtering |
| `Player.Chatted` command parsing | `TextChatCommand` |
| `Chat:FilterStringAsync` | Server `TextService:FilterStringAsync` for non-chat text |

The chat window and bubble customization options are the same in both systems, but `TextChatService` exposes them as configuration instances. Audit admin systems and third-party modules for `Player.Chatted` and raw message parsing; they break under platform-integrated chat.

## 12. Testing chat

- Test with at least two clients (Studio's Server & Clients mode, or a multiplayer playtest); a single client can't show delivery, filtering per receiver, or private channels (`roblox-studio-mcp`).
- For each channel, check who receives a message and who doesn't (wrong team, out of range, ineligible pair).
- Run every command as an authorized and an unauthorized player, and confirm the server rejects the second.
- For editable text, submit twice inside a minute and confirm the second is refused, then submit text that should be filtered.
- Turn on platform-integrated chat in a test copy and look for warnings from APIs that now return `""`: those are your migration list.
- On a phone, check that the chat window, bubbles and any `TextChannelWindow` don't cover controls (`roblox-gui`).

## 13. Checklist

- [ ] Every text surface classified (chat, editable, developer-set, preset).
- [ ] All player-to-player chat through `TextChatService`, including radios, phones and admin chat.
- [ ] Editable text filtered on the server, one submission per player per minute, no reply chains.
- [ ] Delivery rules in server `ShouldDeliverCallback`; client callbacks only style.
- [ ] No callback yields.
- [ ] Commands authorize on the server; `Triggered` text treated as unfiltered.
- [ ] Direct channels use `SetDirectChatRequester`; chat buttons follow `CanUser(s)ChatAsync`.
- [ ] Presets moved to Quick Words, or meet the preset requirements.
- [ ] Code that reads message text, prefixes or `Player.Chatted` listed for the platform-integrated chat migration before May 2027.
