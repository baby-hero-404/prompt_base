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

- **DESIGN_VARIANCE 1-3:** Symmetrical grids, equal paddings, centered alignment
- **DESIGN_VARIANCE 4-7:** Offset overlaps, varied aspect ratios, asymmetric alignment
- **DESIGN_VARIANCE 8-10:** Masonry layouts, fractional grid units, massive empty zones
- **MOTION_INTENSITY 1-3:** No auto-animations. CSS :hover/:active only
- **MOTION_INTENSITY 4-7:** Fluid CSS transitions, animation-delay cascades, transform + opacity
- **MOTION_INTENSITY 8-10:** Scroll-triggered reveals, parallax, scroll-driven animation, physics
- **VISUAL_DENSITY 1-3:** Lots of white space, huge section gaps (py-32 to py-48)
- **VISUAL_DENSITY 4-7:** Standard web app spacing (py-16 to py-24)
- **VISUAL_DENSITY 8-10:** Tight paddings, 1px line separators, font-mono for numbers

---

## 2. Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | HIGH | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |

## Quick Reference

### 1. Accessibility (CRITICAL)

- `color-contrast` - Minimum 4.5:1 ratio for normal text, 3:1 for large text (>18px or 14px bold)
- `focus-states` - Visible focus rings on interactive elements
- `alt-text` - Descriptive alt text for meaningful images
- `aria-labels` - aria-label for icon-only buttons
- `keyboard-nav` - Tab order matches visual order
- `form-labels` - Use label with for attribute
- `reduced-motion` - Motion above MOTION_INTENSITY 3 should honor `prefers-reduced-motion`. Exception: opacity crossfades under 200ms are safe to keep for state-change feedback

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` - Minimum 44x44px touch targets
- `hover-vs-tap` - Use click/tap for primary interactions
- `loading-buttons` - Disable button during async operations
- `error-feedback` - Clear error messages near problem
- `cursor-pointer` - Add cursor-pointer to clickable elements
- `button-contrast` - Button text must be readable against button background (WCAG AA 4.5:1)
- `cta-wrap-ban` - Button text should fit on one line at desktop. If wrapping is unavoidable (e.g., i18n long labels), ensure min-height and padding accommodate it gracefully
- `no-duplicate-cta` - One label per intent on a page ("Get in touch" + "Contact us" = duplicate)

### 3. Performance (HIGH)

- `image-optimization` - Use WebP, srcset, lazy loading
- `reduced-motion` - Check prefers-reduced-motion
- `content-jumping` - Reserve space for async content (CLS < 0.1)
- `lcp-target` - LCP < 2.5s. Hero image must be priority/preloaded
- `inp-target` - INP < 200ms. Heavy work off main thread
- `hardware-accel` - Animate ONLY transform and opacity. Never animate top, left, width, height

### 4. Layout & Responsive (HIGH)

- `viewport-meta` - width=device-width initial-scale=1
- `readable-font-size` - Minimum 16px body text on mobile
- `horizontal-scroll` - Ensure content fits viewport width
- `z-index-management` - Define z-index scale (10, 20, 30, 50)
- `viewport-stability` - Prefer `min-h-[100dvh]` over `h-screen` — `h-screen` causes iOS Safari address-bar jumps. `h-screen` is acceptable in desktop-only admin/dashboard views where mobile Safari is not a target
- `grid-over-flex-math` - Use CSS Grid, not `w-[calc(33%-1rem)]`
- `mobile-collapse` - For every multi-column layout, declare the <768px fallback explicitly
- `hero-viewport-fit` - Hero headline max 2 lines, subtext max 20 words, CTAs visible without scroll

### 5. Typography & Color (HIGH)

#### Typography Rules

| Context | Letter-spacing |
|---------|---------------|
| Body text (14-18px) | `0` (default) |
| Small text (11-13px) | `0.01em` to `0.02em` (positive) |
| UI labels and button text | `0.02em` |
| **ALL CAPS** | **`0.06em` to `0.1em` (required)** |
| Headings 32px+ | `-0.01em` to `-0.02em` |
| Display 48px+ | `-0.02em` to `-0.03em` |

ALL CAPS without positive tracking looks cramped and amateur. Display text without negative tracking looks loose and weak. These are the most reliable AI-slop tells.

#### Type Scale

| Role | Range |
|------|-------|
| Display | 48-72px |
| H1 | 32-48px |
| H2 | 24-32px |
| H3 | 20-24px |
| Body | 15-18px |
| Small | 13-14px |
| Caption | 11-12px |

#### Line Height

| Text size | Line height |
|-----------|-------------|
| Display / H1 (>=32px) | `1.0`-`1.2` (tight) |
| Body (15-18px) | `1.5`-`1.6` |
| Small (<=14px) | `1.5` |

#### Three-Weight System

Most well-crafted UIs use exactly 3 weights:
- **Read** (400/450) - body copy
- **Emphasize** (510/550) - UI text, labels, navigation
- **Announce** (590/600) - headlines, buttons

Weight 700+ is rarely needed.

- `line-length` - Limit to 50-75 characters per line (`max-width: 65ch`)
- `font-pairing` - Maximum 2 typefaces per artifact (display + body)
- `font-defaults` - AVOID Inter as default display font. Prefer Geist, Outfit, Cabinet Grotesk, Satoshi

#### Color Rules

**Palette structure (plan all 4 layers before writing CSS):**

| Layer | Share of pixels | Purpose |
|-------|----------------|---------|
| **Neutrals** | 70-90% | Background, surface, text, muted, border |
| **Accent** (one) | 5-10% | One accent color only |
| **Semantic** | 0-5% | Success, warning, danger |
| **Effect** | <1% | Gradients, glows (rarely justified) |

**Accent discipline:**
- At most 2 visible uses of accent per screen
- Links count as accent; demote to underline if you also have a CTA on the same screen

**Contrast minimums:**

| Pair | Minimum |
|------|---------|
| Body text (<=16px) on background | 4.5:1 |
| Large text (>18px or 14px bold) | 3:1 |
| UI components against adjacent surfaces | 3:1 |

**Dark themes:** Avoid pure #000000 and #ffffff. Use off-black (e.g., #0f0f0f) and off-white (e.g., #fafafa).

**Semantic naming:** Name tokens by purpose (--accent, --success), never by hue (--blue-500, --green-500).

- `60-30-10` - 60% Background, 30% Structure, 10% Accent
- `color-consistency-lock` - Once accent chosen, use it on the WHOLE page. No random color changes mid-page
- `shape-consistency-lock` - Pick ONE corner-radius scale and stick to it across all components

### 6. Animation (MEDIUM)

| Duration | Use |
|----------|-----|
| 50-100ms | Instant feedback (button press, toggle, hover) |
| 150ms | Default for state-confirmation |
| 200-300ms | Entering UI (modals, sheets, dropdowns) |
| 300-500ms | Cross-screen transitions, container morphs |
| >500ms | Reserved for cross-screen, staged transitions |

- `transform-performance` - Use transform/opacity, not width/height
- `loading-states` - Skeleton screens matching final layout shape (not generic spinners)
- `motion-must-be-motivated` - Every animation needs a reason: hierarchy, storytelling, feedback, or state transition. "It looked cool" is not a reason.
- `marquee-max-one` - Maximum one horizontal marquee per page
- `no-window-scroll-listener` - Prefer IntersectionObserver, CSS scroll-driven animations, or library hooks over raw `window.addEventListener('scroll')`. Raw scroll listeners are acceptable when throttled via rAF for scroll-position-dependent logic (e.g., parallax math) that IO/CSS can't express
- `reduced-motion-mandatory` - Motion above MOTION_INTENSITY 3 should honor `prefers-reduced-motion`. Keep opacity/color crossfades as state-change substitutes

### 7. Style Selection (MEDIUM)

- `style-match` - Match style to product type (use dial system from Section 1)
- `consistency` - Use same style across all pages
- `no-emoji-icons` - Use SVG icons (Phosphor, HugeIcons, Radix, Tabler), not emojis
- `one-icon-family` - One icon library per project, standardize strokeWidth globally
- `no-hand-rolled-svg` - Do not hand-draw SVG icons. Use icon libraries.

### 8. Charts & Data (LOW)

- `chart-type` - Match chart type to data type
- `color-guidance` - Use accessible color palettes
- `data-table` - Provide table alternative for accessibility

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

### Production-Test Tells (P1 - Should Fix)

- **Avoid three-column equal feature cards** when DESIGN_VARIANCE > 4. The generic "three identical cards" row reads as template. Prefer 2-column zig-zag, asymmetric grid, or horizontal-scroll. Acceptable for DENSITY >= 7 data-heavy UIs (pricing tiers, plan comparison).
- **NO centered hero** when DESIGN_VARIANCE > 4. Use split-screen, left-aligned, or asymmetric layouts.
- **Avoid generic placeholder names** - "John Doe", "Jane Smith" read as placeholder. Use contextually appropriate names. Exception: form field examples where generic names are conventional (e.g., placeholder text in a name input).
- **NO startup-slop brand names** - "Acme", "Nexus", "SmartFlow", "Cloudly". Invent contextual, premium names.
- **NO filler verbs** - "Elevate", "Seamless", "Unleash", "Next-Gen", "Revolutionize". Use concrete verbs.
- **Avoid section-number eyebrows** - `001 Capabilities`, `002 Featured` are an AI tell in most contexts. Acceptable for portfolio/case-study pages where numbered sections serve as deliberate editorial structure.
- **Avoid decorative scroll cues** - "Scroll", "arrow-scroll", "Scroll to explore" are usually unnecessary. Acceptable on immersive full-screen experiences (galleries, scrollytelling) where below-fold content is not visually implied.
- **NO div-based fake screenshots** - Never build fake product UI from styled divs. Use real images or generated images.

### Soft Tells (P2 - Nice to Fix)

- Standard "Hero - Features - Pricing - FAQ - CTA" sequence with no variation
- More than 12 raw hex values outside `:root`
- Accent color used 6+ times in the rendered body (cap at 2 per screen)
- Decorative blob/wave SVG backgrounds with no functional purpose
- Perfect symmetric layout with no visual tension

### How to Add Soul (the 80/20 rule)

Aim for 80% proven patterns + 20% distinctive choice. The 20% should live in:
- One bold visual move - a typography choice, a single color decision, an unexpected proportion
- Voice and microcopy - a button that says "Start tracking" beats "Get started"
- One micro-interaction the user will remember
- One detail that could only have been put there by someone who used the product

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
