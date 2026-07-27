---
name: roblox-localization
description: "Use when implementing Roblox multi-language support, translation tables, auto-translation, locale-specific content, or region detection."
last_reviewed: 2026-07-26
sources:
  - https://create.roblox.com/docs/reference/engine/classes/LocalizationService
  - https://create.roblox.com/docs/reference/engine/classes/LocalizationTable
  - https://create.roblox.com/docs/reference/engine/classes/Player
---

# Roblox Localization

## When to Load

Load when implementing multi-language support, translation systems, locale-specific content, or region detection. Covers LocalizationService, LocalizationTable, auto-translation, and country/region detection.

## Quick Reference

### Locale Detection
- `player.LocaleId` — locale the player set for their Roblox account (e.g. `en-us`, `pt-br`, `ja-jp`)
- `LocalizationService.RobloxLocaleId` — locale for core/internal features
- `LocalizationService.SystemLocaleId` — player's OS locale
- `LocalizationService:GetCountryRegionForPlayerAsync(player)` — country code from IP geolocation (e.g. `US`, `BR`, `JP`)

### Translation Tables
- `LocalizationTable` — stores translation entries (key → translations per locale)
- Parent `LocalizationTable` under `LocalizationService` for auto-translation
- Set `GuiBase2d.RootLocalizationTable` on GUI objects for per-element tables
- Studio can auto-extract strings into a table via the Localization Tools plugin

### Auto-Translation
- Auto-translation requires `AutoLocalize = true` on the GUI and its ancestors, plus a matching table entry
- Set `TextLabel.Text` normally — the engine replaces it with the translated string for the player's locale
- Missing translations fall back to the source text

### Manual Translation
```luau
local translator = LocalizationService:GetTranslatorForPlayerAsync(player)
local translated = translator:Translate(game, "Welcome!")
local formatted = translator:FormatByKey("coins_count", {count})
```

### Country/Region Detection
```luau
local country = LocalizationService:GetCountryRegionForPlayerAsync(player)
if country == "US" then -- USD pricing
    -- US offer
elseif country == "GB" then
    -- UK offer
end
```

### Key Rules
- `GetCountryRegionForPlayerAsync` is async — wrap in pcall, may fail
- `GetTranslatorForPlayerAsync` is async — cache the translator
- Set `RootLocalizationTable` to choose a table; keep `AutoLocalize` true through the ancestor chain
- Translation entries: `SourceText`, `SourceLocaleId`, then `en-us`, `pt-br`, etc. columns
- Export/import tables as CSV from Studio for bulk editing
- Test with different locales using Studio's locale simulator

### Pitfalls
- Not all locales supported — check `player.LocaleId`
- Auto-translation does NOT work on non-GUI text — use manual `Translator:Translate`
- `GetCountryRegionForPlayerAsync` uses IP geolocation — VPNs give wrong results
- Missing entries fall back to source text silently

**Need more detail?** Load `references/full.md`.
