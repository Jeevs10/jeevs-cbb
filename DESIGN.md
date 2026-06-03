---
name: Jeevs CBB
description: College basketball analytics with Pokemon-style player cards
colors:
  court-sage: "#C7D0B8"
  court-sage-light: "#E7E8D1"
  court-sage-dark: "#B8C0A8"
  black: "#000000"
  white: "#FFFFFF"
  terminal-green: "#4ade80"
typography:
  body:
    fontFamily: "monospace"
    fontSize: "12px"
    fontWeight: "400"
    lineHeight: "1.5"
  label:
    fontFamily: "monospace"
    fontSize: "12px"
    fontWeight: "700"
    lineHeight: "1.5"
    letterSpacing: "0.05em"
    textTransform: "uppercase"
rounded:
  none: "0px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
components:
  panel:
    backgroundColor: "{colors.court-sage}"
    textColor: "{colors.black}"
    rounded: "{rounded.none}"
    padding: "{spacing.md}"
  panel-dark:
    backgroundColor: "{colors.black}"
    textColor: "{colors.terminal-green}"
    rounded: "{rounded.none}"
    padding: "{spacing.md}"
  button:
    backgroundColor: "{colors.court-sage}"
    textColor: "{colors.black}"
    rounded: "{rounded.none}"
    padding: "{spacing.xs} {spacing.sm}"
  button-hover:
    backgroundColor: "{colors.court-sage-dark}"
    textColor: "{colors.black}"
    rounded: "{rounded.none}"
    padding: "{spacing.xs} {spacing.sm}"
---

# Design System: Jeevs CBB

## 1. Overview

**Creative North Star: "The Trading Card Binder"**

This system treats players as collectible characters with distinct visual identities, like Pokemon cards in a binder. The interface balances analytical depth with game-like discovery, making data exploration feel like collecting and understanding player archetypes. The aesthetic is intentionally tactile—hard shadows, thick borders, and monospace typography create a physical, game-like quality that makes stats feel like character attributes rather than abstract numbers.

The system explicitly rejects the dense, purely numerical interfaces of hoop-reference and BartTorvik. Every metric has a visual counterpart; every data point lives in a context that explains what it means. The monospace font and hard-edged shadows reference retro sports games and trading cards, but the execution is clean and modern rather than dated.

**Key Characteristics:**
- Tactile, game-like UI with hard shadows and thick borders
- Pokemon-style player cards as the primary visual metaphor
- Monospace typography for a technical, analytical feel
- Sage green palette that references basketball courts without being literal
- Progressive disclosure: quick lookups first, deep analysis on demand

## 2. Colors

A restrained sage green palette with high-contrast black borders, inspired by basketball courts and vintage trading cards.

### Primary
- **Court Sage** (#C7D0B8): The primary surface color for panels, headers, and backgrounds. Used across 60-70% of the interface to create visual consistency.
- **Court Sage Light** (#E7E8D1): Hover states and secondary backgrounds. Provides subtle depth without introducing new hues.
- **Court Sage Dark** (#B8C0A8): Active states and darker accents. Used sparingly for emphasis.

### Neutral
- **Black** (#000000): All borders, text, and shadows. The hard-edged contrast that gives the system its game-like feel.
- **White** (#FFFFFF): Dropdown backgrounds and card backs. Creates contrast against the sage surfaces.
- **Terminal Green** (#4ade80): Accent color for the dark mode variant (PanelDark). References retro computer terminals.

### Named Rules
**The Hard Border Rule.** All borders are 2px solid black, no exceptions. No gray borders, no hairlines, no rounded corners. The thickness and color are intentional—they make the interface feel physical and game-like.

**The Trading Card Shadow Rule.** Shadows are always hard-edged (3px 3px 0px black), never blurred. This creates the feel of physical cards stacked on a surface, not floating UI elements.

## 3. Typography

**Display Font:** Monospace (with system fallback)
**Body Font:** Monospace (with system fallback)
**Label/Mono Font:** Monospace (with system fallback)

**Character:** The monospace pairing gives the interface a technical, analytical quality—like reading stat sheets or game code. It reinforces the "data as character attributes" metaphor from the Pokemon brand personality.

### Hierarchy
- **Label** (700 weight, 12px, 1.5 line-height, 0.05em letter-spacing, uppercase): Section headers, panel headers, navigation items. Used for all UI chrome and categorization.
- **Body** (400 weight, 12px, 1.5 line-height): All data values, descriptions, and content text. The single size creates a uniform, data-dense feel appropriate for analytics.

### Named Rules
**The Single Size Rule.** Typography uses only two sizes: 12px for body and labels, with larger sizes reserved for the logo/title. This creates a uniform, tabular feel that emphasizes data density over hierarchy.

**The Uppercase Label Rule.** All labels, headers, and navigation items are uppercase with 0.05em letter-spacing. This creates a consistent, technical voice across the interface.

## 4. Elevation

This system uses hard-edged shadows instead of blurred ones to create a trading card aesthetic. Depth is conveyed through layering (cards stacked on cards) rather than atmospheric blur. The 3px 3px 0px black shadow is the only elevation token—no graduated shadow scale.

### Shadow Vocabulary
- **Trading Card Shadow** (`box-shadow: 3px 3px 0px black`): Used on all panels, cards, and dropdowns. Creates the feel of physical cards resting on a surface.

### Named Rules
**The No Blur Rule.** Shadows are never blurred. The hard edge is intentional—it makes elements feel physical and game-like, like cards in a binder or pieces on a board.

## 5. Components

### Panels
- **Corner Style:** Sharp (0px radius)
- **Background:** Court Sage (#C7D0B8)
- **Shadow Strategy:** Trading Card Shadow (3px 3px 0px black)
- **Border:** 2px solid black
- **Internal Padding:** 12px (spacing-md)
- **Variants:** PanelDark uses black background with Terminal Green text for high-contrast sections

### Buttons
- **Shape:** Sharp (0px radius)
- **Primary:** Court Sage background, black text, 4px 8px padding, 2px black border
- **Hover / Focus:** Court Sage Dark background, instant color shift (no transition duration specified)
- **Character:** Feels like game UI buttons—tactile, responsive, intentionally chunky

### Cards
- **Corner Style:** Sharp (0px radius)
- **Background:** Court Sage with hover to Court Sage Dark
- **Shadow Strategy:** Trading Card Shadow
- **Border:** 2px solid black
- **Internal Padding:** 12px (inherited from Panel)
- **Behavior:** Hover state provides instant feedback, reinforcing the game-like feel

### Navigation
- **Style:** Monospace, 12px, uppercase with 0.05em letter-spacing
- **Default:** Gray-600 text, underline on hover
- **Active:** Black text (current page indicator)
- **Dropdowns:** White background, 2px black border, Trading Card Shadow, 16px padding per item
- **Mobile Treatment:** Not specified in current code

### Chips / Badges
- **Style:** Based on Badge component—uses Panel styling with monospace text
- **State:** Not fully specified in current code

## 6. Do's and Don'ts

### Do:
- **Do** use 2px solid black borders on all interactive elements and containers.
- **Do** use the Trading Card Shadow (3px 3px 0px black) for all elevation needs.
- **Do** keep typography at 12px for body and labels unless it's the logo/title.
- **Do** use uppercase with 0.05em letter-spacing for all labels and headers.
- **Do** balance numbers with visual explanations—never show raw data without context.
- **Do** treat players as characters with visual identities (cards, badges, archetypes).

### Don't:
- **Don't** use blurred shadows or graduated elevation scales.
- **Don't** use rounded corners—everything is sharp-edged.
- **Don't** use gray borders or hairlines—black 2px only.
- **Don't** create interfaces that look like hoop-reference or BartTorvik (dense numbers without visual context).
- **Don't** use more than two font sizes—keep the uniform, tabular feel.
- **Don't** introduce new colors beyond the sage palette and black/white/terminal-green.
