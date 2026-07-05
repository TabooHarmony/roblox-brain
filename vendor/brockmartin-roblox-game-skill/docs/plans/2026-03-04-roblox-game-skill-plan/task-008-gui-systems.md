# Task 008: Write gui-systems.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/gui-systems.md`

## Description

Write a comprehensive reference for building user interfaces in Roblox covering ScreenGui, SurfaceGui, BillboardGui, TweenService animations, and cross-platform input handling.

## What To Do

1. **Overview** — When to load (building menus, HUDs, shops, notifications, any UI work)
2. **GUI Hierarchy** — ScreenGui (2D overlay), SurfaceGui (on parts), BillboardGui (floating above objects), placement in StarterGui vs PlayerGui
3. **Core UI Elements** — Frame, TextLabel, TextButton, ImageLabel, ImageButton, ScrollingFrame, UIListLayout, UIPadding, UICorner, UIStroke, UIGradient
4. **Layout Systems** — UIListLayout (lists), UIGridLayout (grids), UIPageLayout (pages), UITableLayout (tables), absolute positioning vs layout-driven
5. **Responsive Design** — Scale vs Offset (use Scale for responsive), UISizeConstraint, UIAspectRatioConstraint, adapting to different screen sizes
6. **Animation with TweenService** — TweenInfo (time, easing, direction, repeat), tweening UI properties (Position, Size, Transparency, BackgroundColor3), chaining tweens, spring-like animations
7. **Input Handling** — UserInputService vs ContextActionService, when to use each, mobile touch vs keyboard/mouse, cross-platform button generation with ContextActionService
8. **Common UI Patterns** — Shop interface, inventory grid, health bar, notification toast, dialog system, loading screen, settings menu
9. **Best Practices** — Use Scale for positioning, consistent UI theme/style, accessibility (readable text sizes, contrast), GUI pooling for performance
10. **Anti-Patterns** — Hardcoded pixel positions, creating new GUIs every frame, not cleaning up connections, blocking UI thread

Include complete Luau code for at least 2 common UI patterns (shop and health bar).

## Verification

- File exists at `references/gui-systems.md`
- Covers all GUI types (ScreenGui, SurfaceGui, BillboardGui)
- TweenService animation patterns included with code
- Input handling covers both mobile and desktop
- At least 2 complete UI pattern implementations
