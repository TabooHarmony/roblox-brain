# Roblox Localization — Full Reference

> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## LocalizationService

### Overview

LocalizationService handles automated translation in Roblox. It stores LocalizationTable objects and provides methods for locale detection, translator creation, and country/region lookup.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `RobloxLocaleId` | string | Locale for core/internal features (e.g. `en-us`) |
| `SystemLocaleId` | string | Player's OS locale |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `GetTranslatorForPlayerAsync(player)` | `Translator` | Get translator for player's locale |
| `GetTranslatorForLocaleAsync(localeId)` | `Translator` | Get translator for a specific locale |
| `GetCountryRegionForPlayerAsync(player)` | `string` | Country/region code from IP geolocation |
| `GetCorescriptLocalizations()` | `Instances` | LocalizationTables for core scripts |

## LocalizationTable

### Overview

LocalizationTable stores translation entries. Each entry maps a source string to translations in multiple locales.

### Structure

Each entry in a LocalizationTable has:
- `Key` — unique identifier (optional, can use source text as key)
- `Source` — the original text string
- `Context` — optional context string for disambiguation
- `Example` — optional example with argument placeholders
- Locale columns — `en-us`, `pt-br`, `ja-jp`, `es-es`, etc.

### Setup

```luau
-- Create a LocalizationTable
local locTable = Instance.new("LocalizationTable")
locTable.Name = "GameTranslations"
locTable.Parent = game:GetService("LocalizationService")

-- Add entries programmatically (rare — usually done via CSV import in Studio)
locTable:SetEntries({
    {
        Key = "welcome",
        Source = "Welcome to the game!",
        ["en-us"] = "Welcome to the game!",
        ["pt-br"] = "Bem-vindo ao jogo!",
        ["ja-jp"] = "ゲームへようこそ！",
        ["es-es"] = "¡Bienvenido al juego!",
    },
    {
        Key = "coins_count",
        Source = "You have {0} coins",
        Example = "You have 100 coins",
        ["en-us"] = "You have {0} coins",
        ["pt-br"] = "Você tem {0} moedas",
        ["ja-jp"] = "{0}コイン持っています",
    },
})
```

## Auto-Translation (GUI)

### How It Works

1. Set `RootLocalizationTable` on a GUI object (or an ancestor)
2. When `TextLabel.Text` is set, the engine looks up the source text in the table
3. If a translation exists for the player's locale, it replaces the displayed text
4. If no translation exists, the source text is shown

```luau
-- Set up auto-translation on a ScreenGui
local screenGui = player.PlayerGui:WaitForChild("MainMenu")
local locTable = game.LocalizationService:WaitForChild("GameTranslations")
screenGui.RootLocalizationTable = locTable

-- Text auto-translates based on player's locale
local welcomeLabel = screenGui:WaitForChild("WelcomeLabel")
welcomeLabel.Text = "Welcome to the game!" -- engine replaces with translation
```

### Scope
- Auto-translation ONLY works on `GuiBase2d` descendants (TextLabel, TextButton, Frame, etc.)
- Does NOT work on chat messages, toasts, or any non-GUI text
- For non-GUI text, use manual `Translator:Translate()`

## Manual Translation

### Getting a Translator

```luau
local LocalizationService = game:GetService("LocalizationService")

-- For the local player (client-side)
local translator = LocalizationService:GetTranslatorForPlayerAsync(game.Players.LocalPlayer)

-- For a specific locale
local translator = LocalizationService:GetTranslatorForLocaleAsync("pt-br")
```

### Translating Strings

```luau
-- Simple translation
local welcome = translator:Translate(game, "Welcome to the game!")

-- With format arguments
local coinsMsg = translator:FormatTranslate(game, "You have {0} coins", {coinCount})

-- Using a specific LocalizationTable (not the default hierarchy)
local customTable = game.LocalizationService:WaitForChild("QuestTranslations")
local questName = translator:Translate(customTable, "Dragon Slayer Quest")
```

## Country/Region Detection

### Use Cases
- Region-specific pricing (USD vs BRL vs JPY)
- Compliance (age ratings, content restrictions by country)
- Region-locked events or features

```luau
-- Server-side country detection
game.Players.PlayerAdded:Connect(function(player)
    local success, country = pcall(function()
        return game:GetService("LocalizationService"):GetCountryRegionForPlayerAsync(player)
    end)
    if success then
        print(player.Name .. " is from " .. country)
        if country == "US" then
            -- show USD pricing
        elseif country == "BR" then
            -- show BRL pricing
        end
    end
end)
```

### Key Rules
- `GetCountryRegionForPlayerAsync` is async and can fail — always pcall
- Uses IP geolocation — VPNs/proxies give wrong results
- Returns ISO 3166-1 alpha-2 country codes (US, GB, JP, BR, etc.)

## Locale List

Common Roblox-supported locales:

| Code | Language |
|------|----------|
| `en-us` | English (US) |
| `en-gb` | English (UK) |
| `pt-br` | Portuguese (Brazil) |
| `es-es` | Spanish (Spain) |
| `es-mx` | Spanish (Mexico) |
| `ja-jp` | Japanese |
| `ko-kr` | Korean |
| `zh-cn` | Chinese (Simplified) |
| `zh-tw` | Chinese (Traditional) |
| `fr-fr` | French |
| `de-de` | German |
| `it-it` | Italian |
| `ru-ru` | Russian |
| `tr-tr` | Turkish |
| `id-id` | Indonesian |
| `th-th` | Thai |
| `vi-vn` | Vietnamese |

Check `player.LocaleId` against this list to determine which translations to provide.

## Workflow

1. **Extract strings**: Use Studio's Localization Tools plugin to auto-extract GUI text into a LocalizationTable
2. **Export CSV**: Export the table as CSV for translators
3. **Import CSV**: Import translated CSV back into the LocalizationTable
4. **Test**: Use Studio's locale simulator to preview different locales
5. **Ship**: Parent LocalizationTable under LocalizationService, set RootLocalizationTable on GUIs

## Pitfalls

- **Missing translations**: fall back to source text silently. Log missing keys during development.
- **Non-GUI text**: auto-translation doesn't work on chat messages, notifications, or any non-GuiBase2d element. Use `Translator:Translate()` manually.
- **Async calls**: `GetTranslatorForPlayerAsync` and `GetCountryRegionForPlayerAsync` are async — cache results, don't call per-frame.
- **VPN/proxy**: country detection via IP is unreliable behind VPNs. Don't use for security-critical decisions.
- **Argument formatting**: use `{0}`, `{1}` placeholders in source text. `FormatTranslate` replaces them in order.
- **Locale coverage**: not all locales are supported. Check `player.LocaleId` and handle unsupported locales gracefully.
