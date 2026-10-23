# Design System, Redesign, Search Tool, Pre-Flight

Sections 5-8 of `SKILL.md`. Loaded on demand.

## 5. Design System Selection

When the brief matches an official design system, use it. Do not recreate existing CSS by hand.

### When to use official packages

| Brief reads as... | Reach for | Why |
|---|---|---|
| Microsoft / enterprise SaaS | `@fluentui/react-components` | Official Fluent UI |
| Google-ish UI, Material-flavored | `@material/web` + Material 3 tokens | Official, theme-able |
| IBM-style B2B / analytics | `@carbon/react` + `@carbon/styles` | Carbon, mature data-density |
| GitHub-style devtool | `@primer/css` or `@primer/react-brand` | Official Primer |
| Modern SaaS, own components | shadcn/ui (`npx shadcn@latest add ...`) | Customizable, never ship default state |
| Tailwind-based modern SaaS | Tailwind v4 utilities + dark: variant | Default for indie builds |
| Fast local-business MVP | Bootstrap 5.3 | Boring, fast, works |
| Accessible React foundation | `@radix-ui/themes` | Primitives + polished theme |

**Rules:**
- One system per project. Do not mix Fluent with Carbon in the same tree.
- If using shadcn/ui, customize radii, colors, shadows, and typography before shipping. Default shadcn reads as "developer prototype" — acceptable only for internal tools or rapid MVPs where brand identity is deferred.

### When the brief is an aesthetic, not a system

| Aesthetic | Implementation |
|---|---|
| Glassmorphism | `backdrop-filter`, layered borders, highlight overlays. Provide solid fallback for `prefers-reduced-transparency`. |
| Bento (Apple-style tile grids) | CSS Grid with mixed cell sizes. No single library. |
| Brutalism | Native CSS, monospace, raw borders. |
| Editorial / magazine | Serif type, asymmetric grid, generous whitespace. |
| Dark tech / hacker | Mono + accent neon, terminal motifs. |

---

## 6. Redesign Protocol

### Detect the Mode

- **Greenfield** - No existing site, or full overhaul approved. Use dial baseline from Section 1.
- **Preserve** - Modernize without breaking the brand. Audit first, extract brand tokens, evolve gradually.
- **Overhaul** - New visual language on existing content. Treat as greenfield for visuals; preserve content and IA.

### Audit Before Touching

Document: brand tokens, information architecture, content blocks, patterns to preserve, patterns to retire, current dial reading, SEO baseline.

### Modernization Levers (priority order - stop when brief is satisfied)

1. **Typography refresh** - biggest visual lift per unit of risk
2. **Spacing & rhythm** - increase section padding, fix vertical rhythm
3. **Color recalibration** - desaturate, unify neutrals, keep brand accent
4. **Motion layer** - add MOTION_INTENSITY-appropriate micro-interactions
5. **Hero & key-section recomposition** - restructure top-of-funnel
6. **Full block replacement** - only when existing block is unsalvageable

### Never Change Silently

- URL structure / route slugs
- Primary nav labels
- Form field names or order (breaks analytics + autofill)
- Brand logo or wordmark
- Legal / consent / cookie copy

---

## 7. How to Use the Search Tool

When user requests UI/UX work (design, build, create, implement, review, fix, improve), follow this workflow:

### Prerequisites

```bash
python3 --version || python --version
```

### Workflow

1. **Brief Inference** - Read the room (Section 0), set dials (Section 1)
2. **Generate Design System** (REQUIRED):
```bash
python3 skills/ux-ui-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```
3. **Supplement with detailed searches** as needed (see [extended-reference.md](references/extended-reference.md))
4. **Get stack guidelines** (default: html-tailwind):
```bash
python3 skills/ux-ui-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```
5. **Apply Anti-AI defaults** (Section 4) and **run Pre-Flight Checklist** (Section 8) before delivery

---

## 8. Pre-Flight Checklist

Run this matrix before outputting code. **THIS IS NOT OPTIONAL.** If any box fails, the output is not done.

### Brief & Configuration
- [ ] Brief inference declared (Section 0.B one-liner)?
- [ ] Dial values explicit and reasoned from the brief?
- [ ] Design system chosen from Section 5 if applicable?

### Anti-AI-Slop
- [ ] No AI-purple/indigo as accent (#6366f1 family)?
- [ ] No three-column equal feature cards?
- [ ] No emoji icons (use SVG libraries)?
- [ ] No filler copy or invented metrics?
- [ ] No generic names (John Doe, Acme)?
- [ ] No div-based fake screenshots?

### Typography & Color
- [ ] ALL CAPS have letter-spacing >= 0.06em?
- [ ] Display text (>=32px) has negative tracking?
- [ ] Color Consistency Lock: one accent used identically across all sections?
- [ ] Shape Consistency Lock: one corner-radius system applied consistently?
- [ ] Button text readable against button background (WCAG AA 4.5:1)?
- [ ] Form inputs, placeholders, labels pass WCAG AA contrast?

### Layout
- [ ] Hero fits viewport: headline <=2 lines, subtext <=20 words, CTA visible without scroll?
- [ ] Navigation renders on ONE line at desktop, height <=80px?
- [ ] No 3+ consecutive sections with same image+text-split layout?
- [ ] Section layouts varied (at least 4 different families across 8 sections)?
- [ ] Mobile collapse explicit for every multi-column layout?
- [ ] Viewport stability: min-h-[100dvh], never h-screen?

### States & Interaction
- [ ] All 5 states provided (Loading, Empty, Error, Populated, Edge)?
- [ ] Empty/loading/error states are designed, not afterthoughts?
- [ ] All clickable elements have cursor-pointer?
- [ ] Hover/focus/active/disabled states implemented?

### Motion
- [ ] Every animation motivated (hierarchy/storytelling/feedback/state)?
- [ ] No `window.addEventListener('scroll')` - using proper scroll APIs?
- [ ] Reduced motion honored for everything above MOTION_INTENSITY 3?
- [ ] Motion claimed = motion shown (if MOTION_INTENSITY > 4, page actually animates)?

### Accessibility & Performance
- [ ] Dark mode tokens defined and tested in both modes?
- [ ] Color contrast passes WCAG AA for all text?
- [ ] Core Web Vitals plausibly hit (LCP < 2.5s, INP < 200ms, CLS < 0.1)?
- [ ] Icons from allowed library only, no hand-rolled SVG paths?

If a single checkbox cannot be honestly ticked, the page is not done. Fix it before delivering.

---

