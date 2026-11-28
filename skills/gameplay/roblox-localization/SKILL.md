---
name: roblox-localization
description: "Use when adding or fixing Roblox translation: localization tables, auto-translation, locale-specific content, or region detection."
when_to_use: "Also when text isn't translated, translated text overflows UI, or when auditing strings before supporting more languages."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/LocalizationService
  - https://create.roblox.com/docs/reference/engine/classes/LocalizationTable
  - https://create.roblox.com/docs/reference/engine/classes/Player
  - https://create.roblox.com/docs/production/localization/image-translations
---

# Roblox Localization

## When to Load

Load when implementing multi-language support, translation systems, locale-specific content, or region detection. Covers LocalizationService, LocalizationTable, auto-translation, and country/region detection.

## Quick Reference

### Locale Detection
- `player.LocaleId`: locale the player set for their Roblox account (e.g. `en-us`, `pt-br`, `ja-jp`)
- `LocalizationService.RobloxLocaleId`: core features' locale
- `LocalizationService.SystemLocaleId`: player's OS locale
- `GetCountryRegionForPlayerAsync(player)`: country code from IP (e.g. `US`)

### Translation Tables
- `LocalizationTable`: stores translation entries (key → translations per locale)
- Parent `LocalizationTable` under `LocalizationService` for auto-translation
- Set `GuiBase2d.RootLocalizationTable` on GUI objects for per-element tables

### Auto-Translation
- Auto-translation requires `AutoLocalize = true` on the GUI and its ancestors, plus a matching table entry
- Set `TextLabel.Text` normally; the engine swaps in the translation, or falls back to source text
- **Images (beta):** Creator Hub image translation for French, German, Indonesian, Italian, Korean, Portuguese, Spanish; enable per language + Automatic Image Capture + Use Translated Content. `AutoLocalize = false` rejects one image.
- TTS (`AudioTextToSpeech.AutoLocalize`) and Quick Words auto-translate too

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
- `GetCountryRegionForPlayerAsync` is async; wrap in pcall, may fail
- `GetTranslatorForPlayerAsync` is async; cache the translator
- Set `RootLocalizationTable` to choose a table; keep `AutoLocalize` true through the ancestor chain
- Translation entries: `SourceText`, `SourceLocaleId`, then `en-us`, `pt-br`, etc. columns
- Test with different locales using Studio's locale simulator

### Pitfalls
- Auto-translation does NOT work on non-GUI text; use manual `Translator:Translate`
- `GetCountryRegionForPlayerAsync` uses IP geolocation, so VPNs give wrong results

**Need more detail?** Load `references/full.md`.
