---
name: ux-ui-pro-max
description: "Use when generating UI/UX designs, choosing color palettes, typography, or building modern responsive web components."
---

# UX/UI Pro Max - Design Intelligence

Comprehensive design guide for web and mobile applications. Contains 50+ styles, 97 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 9 technology stacks. Searchable database with priority-based recommendations. Enhanced with anti-AI-slop rules, brief inference workflow, and research-grounded craft rules.

## When to Apply

Reference these guidelines when:
- Designing new UI components or pages
- Choosing color palettes and typography
- Reviewing code for UX issues
- Building landing pages or dashboards
- Implementing accessibility requirements
- Redesigning or modernizing existing UIs

---

## 0. Brief Inference (Read the Room Before Anything Else)

Before touching code or choosing styles, **infer what the user actually wants**. Most LLM design output is bad because the model jumps to a default aesthetic instead of reading the room.

### 0.A Read these signals first

1. **Page kind** - landing (SaaS / consumer / agency / event), portfolio (dev / designer / studio), redesign (preserve vs overhaul), editorial / blog, dashboard, mobile app
2. **Vibe words** the user used - "minimalist", "calm", "Linear-style", "Awwwards", "brutalist", "premium consumer", "Apple-y", "playful", "serious B2B", "editorial", "agency-y", "glassy", "dark tech"
3. **Reference signals** - URLs they linked, screenshots they pasted, products they named, brands they're competing with
4. **Audience** - B2B procurement panel vs. design-conscious consumer vs. recruiter scanning a portfolio. The audience picks the aesthetic, not your taste.
5. **Brand assets that already exist** - logo, color, type, photography. For redesigns, these are starting material, not optional input.
6. **Quiet constraints** - accessibility-first audiences, public-sector, regulated industries, trust-first commerce, kids' products. These constraints OVERRIDE aesthetic preference.

### 0.B Output a one-line "Design Read" before generating

Before any code, state in one line: **"Reading this as: \<page kind\> for \<audience\>, with a \<vibe\> language, leaning toward \<design system or aesthetic family\>."**

Example reads:
- *"Reading this as: B2B SaaS landing for technical buyers, with a Linear-style minimalist language, leaning toward Tailwind utilities + Geist + restrained motion."*
- *"Reading this as: solo designer portfolio for hiring managers, with an editorial / kinetic-type language, leaning toward native CSS + scroll-driven animation + custom typography."*

### 0.C If the brief is ambiguous, ask one question, do not guess

Ask exactly **one** clarifying question - never a multi-question dump - and only when the design read genuinely diverges. If you can confidently infer from context, **do not ask**. Just declare the design read and proceed.

---

## 1. Three Dials (Core Configuration)

After the design read, set three dials. Every layout, motion, and density decision is gated by these.

* **`DESIGN_VARIANCE: 8`** - 1 = Perfect Symmetry, 10 = Artsy Chaos
* **`MOTION_INTENSITY: 6`** - 1 = Static, 10 = Cinematic / Physics
* **`VISUAL_DENSITY: 4`** - 1 = Art Gallery / Airy, 10 = Cockpit / Packed Data

**Baseline:** `8 / 6 / 4`. Use these unless the design read overrides them.

### Dial Inference (design read to dial values)

| Signal | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| "minimalist / clean / calm / editorial / Linear-style" | 5-6 | 3-4 | 2-3 |
| "premium consumer / Apple-y / luxury / brand" | 7-8 | 5-7 | 3-4 |
| "playful / wild / Dribbble / Awwwards / experimental" | 9-10 | 8-10 | 3-4 |
| "landing page / portfolio / marketing site (default)" | 7-9 | 6-8 | 3-5 |
| "trust-first / public-sector / regulated / a11y-critical" | 3-4 | 2-3 | 4-5 |
| "dashboard / data-heavy / analytics" | 3-5 | 3-4 | 7-9 |
| "redesign - preserve" | match existing | +1 | match existing |
| "redesign - overhaul" | +2 | +2 | match existing |

### Use-Case Presets

| Use case | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| Landing (SaaS, mainstream) | 7 | 6 | 4 |
| Landing (Agency / creative) | 9 | 8 | 3 |
| Landing (Premium consumer) | 7 | 6 | 3 |
| Portfolio (Designer / studio) | 8 | 7 | 3 |
| Portfolio (Developer) | 6 | 5 | 4 |
| Dashboard (Analytics / Admin) | 4 | 3 | 8 |
| Editorial / Blog | 6 | 4 | 3 |
| Public-sector service | 3 | 2 | 5 |
| Mobile app | 6 | 5 | 5 |

### How the Dials Drive Output

- **DESIGN_VARIANCE:** `1-3` (symmetrical grids, equal padding) → `4-7` (offset overlaps, asymmetric) → `8-10` (masonry, huge empty zones).
- **MOTION_INTENSITY:** `1-3` (hover/active only) → `4-7` (CSS transitions, opacity+transform) → `8-10` (scroll reveals, parallax, physics).
- **VISUAL_DENSITY:** `1-3` (airy whitespace, py-32+) → `4-7` (standard web app spacing) → `8-10` (tight padding, 1px separators, font-mono).

---

## 2. Rule Categories & Craft Reference

> 📖 **Deep Craft Specifications**: Detailed craft standards are maintained in [`references/quick-reference.md`](references/quick-reference.md) and [`references/craft/`](references/craft/).

| Priority | Category | Critical Checks | Reference Doc |
|---|---|---|---|
| 1 | **Accessibility (CRITICAL)** | 4.5:1 text contrast (3:1 large), visible focus rings, aria-labels on icon buttons, honor `prefers-reduced-motion` | [Accessibility Baseline](references/craft/accessibility-baseline.md) |
| 2 | **Touch & Interaction (CRITICAL)** | 44x44px min target size, `cursor-pointer` on clickables, single line desktop CTA, clear error feedback | [Form Validation](references/craft/form-validation.md) |
| 3 | **Performance (HIGH)** | Animate transform/opacity ONLY, LCP < 2.5s, reserve layout space (CLS < 0.1), WebP/lazy images | [Quick Reference](references/quick-reference.md) |
| 4 | **Layout & Responsive (HIGH)** | `min-h-[100dvh]` over `h-screen`, CSS Grid over calc math, declare <768px fallback explicitly | [Quick Reference](references/quick-reference.md) |
| 5 | **Typography & Color (HIGH)** | Max 2 typefaces, positive tracking on ALL CAPS, negative tracking on display (>=32px), 60-30-10 palette | [Typography](references/craft/typography.md), [Color](references/craft/color.md) |
| 6 | **Animation (MEDIUM)** | 150-300ms micro-interactions, motivated motion only, max 1 marquee, reduced-motion fallback | [Animation Discipline](references/craft/animation-discipline.md) |
| 7 | **Style Selection (MEDIUM)** | Standard SVG icon library (Phosphor, Radix, Tabler), never emojis or hand-rolled SVG paths | [Pattern Vocabulary](references/pattern-vocabulary.md) |
| 8 | **Charts & Data (LOW)** | Accessible palettes, provide semantic table alternative for screen readers | [Extended Reference](references/extended-reference.md) |

---

## 3. Five Required States

Every surface that fetches, transforms, or accepts data must render ALL five states. Shipping only the "populated" state is the #1 AI design failure.

| State | Triggered when | Must contain |
|---|---|---|
| **Loading** | Data is in flight | Skeleton/spinner + 15s "taking longer" fallback |
| **Empty** | No records yet | Headline, explanation, primary CTA |
| **Error** | Fetch/validation failed | Plain-language cause, recovery action, preserved input |
| **Populated** | Data present | The primary design |
| **Edge** | Extreme volume, long strings, missing fields | Layout that does not break |

---

## 4. Anti-AI Defaults (Taste Filter)

### The 7 Cardinal Sins (P0 - Must Fix)

1. **Default AI-purple/indigo as accent** - `#6366f1`, `#4f46e5`, `#4338ca`, `#8b5cf6`, `#7c3aed`, `#a855f7` signal "AI-generated" to trained eyes. Use purposeful brand colors. OK if the brief explicitly specifies indigo/purple as brand color.
2. **Two-stop "trust" gradient on hero** - purple-to-blue, blue-to-cyan, indigo-to-pink. A flat surface + intentional type beats this every time.
3. **Emoji as feature icons** - No `sparkles`, `rocket`, `target`, `zap`, `fire`, `lightbulb` inside headings, buttons, or list items. Use 1.6-1.8px stroke monoline SVG.
4. **Inter/system-ui as display font** - Use the design system's display font. If none specified, use Geist, Outfit, Cabinet Grotesk, or Satoshi.
5. **Rounded card with colored left-border accent** - The "AI dashboard tile" shape. Drop either the radius or the left border.
6. **Invented metrics** - "10x faster", "99.9% uptime", "3x more productive". Use real data or labeled placeholders.
7. **Filler copy** - "Lorem ipsum", "Feature one/two/three". Design around real or realistic content.

### Production-Test Tells & Adding Soul

- **Avoid 3-column equal feature cards** when DESIGN_VARIANCE > 4 (prefer 2-column zig-zag, asymmetric grid, or horizontal-scroll).
- **NO centered hero** when DESIGN_VARIANCE > 4 (prefer split-screen or asymmetric).
- **NO startup-slop names/verbs** (Acme, Elevate, Revolutionize) or generic placeholders (John Doe).
- **NO div-based fake screenshots** (use real or generated images).
- For complete P1/P2 soft tells, token leak audits, and the 80/20 soul guide, see [`references/craft/anti-ai-slop.md`](references/craft/anti-ai-slop.md).

---

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

## Extended References

For deeper detail, see these reference files:
- [`references/extended-reference.md`](references/extended-reference.md) - Search tool usage, stack guidelines, example workflows
- [`references/pattern-vocabulary.md`](references/pattern-vocabulary.md) - 50+ named UI patterns with descriptions
- [`references/craft/`](references/craft/) - Research-grounded craft rules for typography, color, animation, state coverage, accessibility, laws of UX
