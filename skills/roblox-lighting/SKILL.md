---
name: roblox-lighting
description: "Use for Roblox lighting, atmosphere, day/night, or post-processing effects."
last_reviewed: 2026-07-12
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/environment/lighting.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/environment/atmosphere.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/environment/post-processing-effects.md
---

# Roblox Lighting & Atmosphere

## When to Load

Load for Roblox lighting, atmosphere, day/night, or post-processing (Bloom, ColorCorrection, DepthOfField).

## Quick Reference

### Lighting Service
```luau
Lighting.ClockTime = 14            -- 0-24 numeric
Lighting.Brightness = 2            -- 0-10, default 2
Lighting.Ambient = Color3.fromRGB(70, 70, 70)        -- shadow fill
Lighting.OutdoorAmbient = Color3.fromRGB(128, 128, 128)
Lighting.GlobalShadows = true
Lighting.ShadowSoftness = 0.2      -- 0=sharp, 1=soft
-- Current Studio uses LightingStyle and PrioritizeLightingQuality instead of Technology.
-- Verify enum values and device behavior against current Creator Hub docs before setting them.
```

### Atmosphere
```luau
local atmo = Instance.new("Atmosphere")
atmo.Density = 0.3    -- 0=clear, 1=opaque (keep <0.5)
atmo.Offset = 0.25    -- 0=ground, 1=sky
atmo.Color = Color3.fromRGB(199, 199, 199)   -- near fog
atmo.Decay = Color3.fromRGB(92, 92, 92)      -- far/horizon
atmo.Glare = 0        -- 0-10
atmo.Haze = 0         -- 0-10
atmo.Parent = Lighting
```

### Post-Processing (all parented to Lighting)
| Effect | Key Properties |
|--------|---------------|
| `BloomEffect` | Intensity (0-1), Size (px), Threshold (>0.7 recommended) |
| `ColorCorrectionEffect` | Brightness, Contrast, Saturation (-1 to 1), TintColor |
| `DepthOfFieldEffect` | FarIntensity, FocusDistance, InFocusRadius, NearIntensity |
| `SunRaysEffect` | Intensity (0-1), Spread (0-1) |

### Day/Night Cycle
```luau
local CYCLE_SPEED = 1  -- minutes per full day
task.spawn(function()
    while true do
        Lighting.ClockTime += (task.wait() / 60) * (24 / CYCLE_SPEED)
        if Lighting.ClockTime >= 24 then Lighting.ClockTime -= 24 end
    end
end)
```

### Local Lights
| Light | Use | Key Props |
|-------|-----|-----------|
| `PointLight` | Lamps, torches | Range, Brightness, Color |
| `SpotLight` | Flashlights | Range, Angle, Face |
| `SurfaceLight` | Screens, panels | Range, Angle, Face |

**Perf:** Limit shadow-casting lights to 4-6 visible. Use `Shadows=false` on most. Neon material = cheap glow.

**MCP:** Inspect, change minimally, capture, check performance.

### Common Pitfalls
- Brightness >3 washes out. Density >0.5 = soup. Max 2-3 post effects.
- Ambient should not be black. Use LightingStyle/PrioritizeLightingQuality; never set deprecated Technology.

### References
- Mood presets (Day, Golden Hour, Night, Horror, Underwater, Sci-Fi), zone tweens, full examples: `references/full.md`
