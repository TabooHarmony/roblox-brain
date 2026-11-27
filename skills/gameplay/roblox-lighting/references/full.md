# Roblox Lighting & Atmosphere


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Use this skill when configuring lighting, atmosphere, time of day, post-processing effects, or creating visual mood for a game.

## Lighting Service Properties

```luau
local Lighting = game:GetService("Lighting")

-- Time of day (24-hour format as string)
Lighting.ClockTime = 14          -- 2 PM (numeric, 0-24)
Lighting.TimeOfDay = "14:00:00"  -- same thing as string

-- Core lighting
Lighting.Brightness = 2          -- sun intensity (0-10, default 2)
Lighting.Ambient = Color3.fromRGB(70, 70, 70)      -- shadow color
Lighting.OutdoorAmbient = Color3.fromRGB(128, 128, 128) -- outdoor shadow fill
Lighting.ColorShift_Top = Color3.fromRGB(0, 0, 0)  -- sky color tint
Lighting.ColorShift_Bottom = Color3.fromRGB(0, 0, 0) -- ground bounce tint

-- Shadows
Lighting.GlobalShadows = true
Lighting.ShadowSoftness = 0.2    -- 0 = sharp, 1 = very soft
-- Environment
Lighting.EnvironmentDiffuseScale = 1  -- how much skybox colors affect surfaces
Lighting.EnvironmentSpecularScale = 1 -- skybox reflections on shiny surfaces
-- Technology remains deprecated and not script-writable.
-- LightingStyle and PrioritizeLightingQuality are script-writable; verify device behavior in Studio.
```

## Atmosphere

The `Atmosphere` object controls fog, haze, and sky color blending:

```luau
local atmo = Instance.new("Atmosphere")
atmo.Density = 0.3       -- fog thickness (0 = clear, 1 = opaque)
atmo.Offset = 0.25       -- how high fog starts (0 = ground, 1 = sky)
atmo.Color = Color3.fromRGB(199, 199, 199)  -- fog color (near)
atmo.Decay = Color3.fromRGB(92, 92, 92)     -- fog color (far/horizon)
atmo.Glare = 0           -- sun glare intensity (0-10)
atmo.Haze = 0            -- atmospheric haze (0-10)
atmo.Parent = Lighting
```

## Post-Processing Effects

All post-processing goes as children of Lighting:

### BloomEffect
```luau
local bloom = Instance.new("BloomEffect")
bloom.Intensity = 0.5    -- glow strength (0-1)
bloom.Size = 24          -- glow spread (pixels)
bloom.Threshold = 0.8    -- brightness threshold to bloom (0-1)
bloom.Parent = Lighting
```

### ColorCorrectionEffect
```luau
local cc = Instance.new("ColorCorrectionEffect")
cc.Brightness = 0        -- -1 to 1
cc.Contrast = 0.1        -- -1 to 1
cc.Saturation = 0.1      -- -1 to 1 (negative = desaturated)
cc.TintColor = Color3.fromRGB(255, 255, 255) -- color overlay
cc.Parent = Lighting
```

### DepthOfFieldEffect
```luau
local dof = Instance.new("DepthOfFieldEffect")
dof.FarIntensity = 0.3   -- blur at far distance
dof.FocusDistance = 50    -- studs where focus is sharpest
dof.InFocusRadius = 30   -- studs of sharp focus range
dof.NearIntensity = 0    -- blur at near distance
dof.Parent = Lighting
```

### SunRaysEffect
```luau
local rays = Instance.new("SunRaysEffect")
rays.Intensity = 0.1     -- ray visibility (0-1)
rays.Spread = 0.5        -- ray spread angle (0-1)
rays.Parent = Lighting
```

## Mood Presets

### Bright Day (default/casual)
```luau
Lighting.ClockTime = 14
Lighting.Brightness = 2
Lighting.Ambient = Color3.fromRGB(128, 128, 128)
Lighting.OutdoorAmbient = Color3.fromRGB(128, 128, 128)
-- Atmosphere: light haze
atmo.Density = 0.2
atmo.Offset = 0.5
atmo.Color = Color3.fromRGB(200, 220, 255)
```

### Golden Hour (warm, cinematic)
```luau
Lighting.ClockTime = 17.5
Lighting.Brightness = 2
Lighting.Ambient = Color3.fromRGB(80, 60, 40)
Lighting.OutdoorAmbient = Color3.fromRGB(150, 120, 80)
Lighting.ColorShift_Top = Color3.fromRGB(255, 200, 100)
-- Atmosphere: warm fog
atmo.Density = 0.3
atmo.Offset = 0.3
atmo.Color = Color3.fromRGB(255, 200, 150)
atmo.Decay = Color3.fromRGB(200, 100, 50)
-- Post: warm tint
cc.TintColor = Color3.fromRGB(255, 240, 220)
cc.Contrast = 0.1
bloom.Intensity = 0.4
bloom.Threshold = 0.7
```

### Night (dark, moody)
```luau
Lighting.ClockTime = 0
Lighting.Brightness = 0.5
Lighting.Ambient = Color3.fromRGB(30, 30, 50)
Lighting.OutdoorAmbient = Color3.fromRGB(20, 20, 40)
-- Atmosphere: dark blue fog
atmo.Density = 0.4
atmo.Offset = 0.1
atmo.Color = Color3.fromRGB(20, 20, 50)
-- Post: blue tint, low saturation
cc.TintColor = Color3.fromRGB(180, 190, 255)
cc.Saturation = -0.2
cc.Brightness = -0.05
```

### Horror (oppressive, claustrophobic)
```luau
Lighting.ClockTime = 22
Lighting.Brightness = 0.3
Lighting.Ambient = Color3.fromRGB(10, 10, 15)
Lighting.OutdoorAmbient = Color3.fromRGB(5, 5, 10)
Lighting.GlobalShadows = true
Lighting.ShadowSoftness = 0.1 -- sharp shadows = scarier
-- Atmosphere: thick dark fog
atmo.Density = 0.5
atmo.Offset = 0
atmo.Color = Color3.fromRGB(10, 10, 10)
-- Post: desaturated, dark
cc.Saturation = -0.4
cc.Contrast = 0.2
cc.Brightness = -0.1
-- No bloom (bloom = cheerful)
```

### Underwater
```luau
Lighting.ClockTime = 12
Lighting.Brightness = 1
Lighting.Ambient = Color3.fromRGB(20, 60, 80)
-- Atmosphere: heavy blue-green
atmo.Density = 0.7
atmo.Offset = 0
atmo.Color = Color3.fromRGB(30, 100, 120)
atmo.Decay = Color3.fromRGB(10, 40, 60)
-- Post: blue tint, blur
cc.TintColor = Color3.fromRGB(150, 200, 255)
cc.Saturation = -0.3
-- DepthOfField for murky distance
dof.FarIntensity = 0.5
dof.FocusDistance = 30
dof.InFocusRadius = 20
```

### Sci-Fi (clean, high-tech)
```luau
Lighting.ClockTime = 12
Lighting.Brightness = 3
Lighting.Ambient = Color3.fromRGB(100, 100, 120)
-- Atmosphere: minimal, clean
atmo.Density = 0.1
atmo.Color = Color3.fromRGB(200, 210, 255)
-- Post: slight blue, high contrast
cc.TintColor = Color3.fromRGB(230, 240, 255)
cc.Contrast = 0.15
bloom.Intensity = 0.6
bloom.Threshold = 0.6
bloom.Size = 30
```

## Dynamic Lighting

### Day/Night Cycle

```luau
local CYCLE_SPEED = 1 -- minutes per full day (1 = fast, 24 = real-time)

task.spawn(function()
    while true do
        Lighting.ClockTime += (task.wait() / 60) * (24 / CYCLE_SPEED)
        if Lighting.ClockTime >= 24 then
            Lighting.ClockTime -= 24
        end
    end
end)
```

### Zone-Based Lighting (indoor/outdoor)

```luau
-- Client: tween lighting when entering zones
local function transitionToIndoor()
    TweenService:Create(Lighting, TweenInfo.new(1), {
        Brightness = 1,
        Ambient = Color3.fromRGB(100, 90, 70),
    }):Play()
    TweenService:Create(atmo, TweenInfo.new(1), {
        Density = 0,
    }):Play()
end

local function transitionToOutdoor()
    TweenService:Create(Lighting, TweenInfo.new(1), {
        Brightness = 2,
        Ambient = Color3.fromRGB(128, 128, 128),
    }):Play()
    TweenService:Create(atmo, TweenInfo.new(1), {
        Density = 0.3,
    }):Play()
end
```

## Local Lights

### Light Types

| Light | Use for | Key properties |
|-------|---------|---------------|
| `PointLight` | Lamps, torches, orbs | Range, Brightness, Color |
| `SpotLight` | Flashlights, stage lights | Range, Angle, Face |
| `SurfaceLight` | Screens, panels, signs | Range, Angle, Face |

### Practical Light Setup

```luau
local function createTorch(part: BasePart)
    -- Neon glow (visual only, no actual light)
    part.Material = Enum.Material.Neon
    part.Color = Color3.fromRGB(255, 150, 50)

    -- Actual light emission
    local light = Instance.new("PointLight")
    light.Color = Color3.fromRGB(255, 170, 80)
    light.Brightness = 2
    light.Range = 20
    light.Shadows = true -- expensive, use sparingly
    light.Parent = part
end
```

### Performance Note

- Shadows on lights are expensive. Limit to 4-6 shadow-casting lights visible at once.
- PointLight.Shadows = false is much cheaper than true.
- Use Neon material for visual glow without the performance cost of actual lights, in dark tones (it blooms to white).
- Light `Range` is clamped to 120 studs.
- On mobile, consider disabling light shadows entirely.

## Current engine facts (2026-11)

- **Light range is capped at 120 studs.** `PointLight`, `SpotLight` and `SurfaceLight` `Range` is always clamped to 120; `Lighting.ExtendLightRangeTo120` is unused, hidden and non-scriptable.
- **`LightingStyle` and `PrioritizeLightingQuality` are script-writable; `Technology` is deprecated.** `Soft` is the stylized look and `Realistic` the naturalistic one, and the shadowing path also depends on `PrioritizeLightingQuality` (for example, `Soft` with it enabled uses shadow maps rather than voxel lighting). Check both on desktop and phone.
- **Graphics quality levels:** the engine scales rendering per device and keeps at least 500 studs of draw distance even at the lowest level. Preview with Studio Settings → Rendering → Editor Quality Level at the lowest and highest levels. The docs advise against changing visuals from scripts based on `UserGameSettings.SavedQualityLevel`. If raising the level doesn't reveal more scene, check `StreamingTargetRadius` before blaming lighting.
- **`Lighting.LightingChanged(skyChanged)`:** `skyChanged` is true when a `Sky` is added or removed or a Sky property other than `SkyboxOrientation` changes; false for Lighting, Atmosphere and `SkyboxOrientation` changes.
- **Decal and Texture emissive masks:** `Decal.EmissiveMaskContent` (a grayscale mask), `EmissiveStrength` (multiplier, default 1, 0 turns glow off, large values clamp to white) and `EmissiveTint` make a decal or texture glow without a light. `Texture` inherits them from `Decal`. <!-- temporal: 2026-11 -->

## Field-tested lighting lessons

From individual projects; judge every change from an in-game screenshot at play distance under the final lighting stack.

- **Roofed interiors: leave `ClockTime` alone.** Sky light still tints a fully roofed room (14.5 → 17.4 turned one blue). Tune interiors with `Lighting.Ambient` and one `ColorCorrectionEffect`. A brightly lit white ceiling over a white interior read clinical; a dark open ceiling with lower Ambient (around 54, 58, 72) did most of the fix in one step. In-game colors land well below Blender renders under dim indoor ambient.
- **Lamp pools stack.** Values that look right on one light burn a room white when several overlap: 32 PointLights at Brightness 1.5 blew a room out, Brightness 0.25 with Range 16 read right. Outdoor lamps in daylight tint surfaces (a driveway went pink at noon); light only lamps with something overhead.
- **Imported lamp data often lists several bulbs per fixture** a fraction of a stud apart. Merge bulbs within about 2 studs into one light and dim crowded areas (for example by `sqrt(3 / lightsWithin10Studs)`).
- **Tie each light to its fixture.** Lights parented to a separate holder outlive a destroyed lamp. Parent the light to the lamp part, or probe the lamp point with `GetPartBoundsInRadius` and put the light out after two empty probes.
- **Neon blooms to near-white at ordinary bright colors** (150, 190, 255 read as white); a lit surface that must keep its hue needs dark values (45, 70, 120 read as saturated blue). Many Neon parts plus bright lights blow rooms out. Small Neon pickups read as blobs; `SmoothPlastic` read better.
- **Materials and tonemapping shift palettes.** `Fabric` greyed out bright awning colors, the Retro tonemapper washed out light colors, and exposure changes did nothing while color grading was on (`ColorCorrectionEffect` plus dimmer lights worked). Check palette-critical surfaces under the final material and lighting.
- **Two-sided panes go black on the shaded face.** A `Texture` on both faces of a thin plant part rendered the side away from the sun near black. `Texture.Color3` values above 1 brighten, so tint each face by `1 + k * max(0, -normal:Dot(Lighting:GetSunDirection()))` with `k` about 1.2, leaving the sunny face at 1; a uniform tint washes out the sunny side. The emissive mask properties above are the documented alternative to test.
- **Skybox faces:** in one project `Sky.SkyboxLf` faced +X and `SkyboxRt` faced -X, the opposite of what the names suggest (the reference only says "left" and "right"). When generating faces, verify with a debug render that paints each pixel's direction on a 15-degree grid; a turned or mirrored face breaks the grid at its edges. Show the sun with `Sky.CelestialBodiesShown` rather than painting it, so faces don't depend on time of day.

```luau
-- Illustrative: brighten the shaded face of a two-sided texture pane.
local Lighting = game:GetService("Lighting")

local K = 1.2

local function shadeTwoSided(texture: Texture, faceNormalWorld: Vector3)
    local away = math.max(0, -faceNormalWorld:Dot(Lighting:GetSunDirection()))
    local gain = 1 + K * away
    texture.Color3 = Color3.new(gain, gain, gain)
end
```

## Common Mistakes

- **Brightness too high**: Values above 3 wash out everything. Start at 2.
- **Atmosphere Density too high**: Above 0.5 makes everything look like soup. Subtle is better.
- **Too many post-processing effects**: Each one costs frame time. Pick 2-3 max.
- **Bloom on everything**: High bloom + low threshold = everything glows. Use threshold > 0.7.
- **No Ambient light**: Setting Ambient to black makes shadows pitch black (unrealistic). Always have some fill.
- **Lighting technology settings**: `Technology` is deprecated and not script-writable. `LightingStyle` and `PrioritizeLightingQuality` are script-writable according to current Creator Hub metadata. Configure them deliberately and check the result on desktop and mobile.
- **Stacking ColorCorrection**: Multiple ColorCorrectionEffects multiply. Use one and tween its properties.
- **Not testing on mobile**: Lighting that looks great on desktop can be invisible or washed out on mobile screens.
