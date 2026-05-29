# Design System

## Overview

R90's captured source is a GitHub repository page, so the visual identity is dark, technical, and document-led. The composition should feel like a calm developer tool rather than a consumer sleep app: structured panels, monospaced command blocks, thin borders, and restrained color. Product warmth comes from the sleep-cycle motif and soft glow asset, not from changing the core GitHub-like interface language.

## Colors

- **Primary Surface**: `#0D1117` — main dark canvas.
- **Deep Surface**: `#010409` — lower-depth background and scene edges.
- **Panel Surface**: `#151B23` — code panels and UI cards.
- **Raised Surface**: `#212830` — elevated cards and repo-window chrome.
- **Border Quiet**: `#3D444D` — one-pixel dividers and window outlines.
- **Primary Content**: `#F0F6FC` — headings and high-priority text.
- **Muted Content**: `#9198A1` — captions, secondary labels, timestamps.
- **Blue Accent**: `#4493F8` — R90 name, timeline strokes, active tabs.
- **Action Blue**: `#1F6FEB` — strong call-to-action accents.
- **Success Green**: `#238636` — passing tests and completed check-ins.

## Typography

- **Primary Sans**: Mona Sans VF, weights 400, 500, 600. Use for headings, interface labels, and body copy.
- **Monospace**: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace. Use for commands, JSON, times, and deterministic CLI readouts.
- **Hierarchy**: Product titles can reach 126px, scene headlines 68-88px, body 30-38px, code 24-30px, labels 18-22px. Keep all text crisp and high contrast.

## Elevation

Depth comes from layered panels, subtle 1px borders, and localized radial glow. Avoid heavy drop shadows; use quiet outlines, inner highlights, and soft blue/purple bloom from `glow-1.png` to create nighttime depth without leaving the technical identity.

## Components

- **Repository Window**: Large bordered dark panel with a file-list header, muted metadata, and compact rows.
- **README Code Blocks**: Monospaced command panels with `#151B23` background, thin borders, and syntax-colored tokens.
- **Cycle Timeline**: Custom circular 90-minute cycle marks connected by blue strokes, anchored to a wake time.
- **Test Result Panel**: JSON-like block showing `"ok": true` and named tests in blue/green.
- **Platform Chips**: Small rounded tags for Codex, OpenClaw, MiClaw, and CLI using blue-tinted surfaces.

## Do's and Don'ts

### Do's

- Use exact captured colors and Mona Sans-style typography.
- Keep the design calm, structured, and technical.
- Show real R90 concepts: 90-minute cycles, wake anchoring, wind-down, CLI, skill, weekly check-ins.
- Use captured screenshots and code panels as moving visual evidence.
- Let soft glow and cycle lines add warmth without overpowering the product.

### Don'ts

- Do not make medical or sleep-quality guarantees.
- Do not make it look like a consumer meditation app.
- Do not use bright full-screen gradients or saturated wellness colors.
- Do not invent unsupported product surfaces like a finished mobile app.
- Do not hide the developer-tool nature; this is a skill and CLI today.
