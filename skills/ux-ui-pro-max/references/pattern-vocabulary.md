# Pattern Vocabulary

Named patterns the agent should know when designing UIs. Use these pattern names to communicate about design decisions and reach for them when the design read calls for them.

> Adapted from open-design's taste-skill reference vocabulary.

## Hero Paradigms

| Pattern | Description |
|---------|-------------|
| **Asymmetric Split Hero** | Text on one side, asset on the other, generous white space |
| **Editorial Manifesto Hero** | Large type, no asset, almost-poster |
| **Video / Media Mask Hero** | Type cut out as mask over video background |
| **Kinetic-Type Hero** | Animated typography as the primary visual |
| **Curtain-Reveal Hero** | Hero parts on scroll like a curtain |
| **Scroll-Pinned Hero** | Hero stays pinned while content scrolls behind |

## Navigation & Menus

| Pattern | Description |
|---------|-------------|
| **Magnetic Button** | Pulls toward cursor on hover |
| **Dynamic Island** | Morphing pill for status / alerts |
| **Contextual Radial Menu** | Circular menu expanding at click point |
| **Floating Speed Dial** | FAB springing into curved secondary actions |
| **Mega Menu Reveal** | Full-screen dropdown, stagger-fade content |

## Layout & Grids

| Pattern | Description |
|---------|-------------|
| **Bento Grid** | Asymmetric tile grouping (Apple Control Center style) |
| **Masonry Layout** | Staggered grid, no fixed row height |
| **Chroma Grid** | Borders / tiles with subtle animating gradients |
| **Split-Screen Scroll** | Two halves sliding in opposite directions |
| **Sticky-Stack Sections** | Sections that pin and stack on scroll |

## Cards & Containers

| Pattern | Description |
|---------|-------------|
| **Parallax Tilt Card** | 3D tilt tracking mouse coordinates |
| **Spotlight Border Card** | Borders illuminate under cursor |
| **Glassmorphism Panel** | Frosted glass with inner refraction |
| **Holographic Foil Card** | Iridescent rainbow shift on hover |
| **Morphing Modal** | Button expands into its own dialog |

## Scroll Animations

| Pattern | Description |
|---------|-------------|
| **Sticky Scroll Stack** | Cards stick and physically stack |
| **Horizontal Scroll Hijack** | Vertical scroll drives horizontal pan |
| **Zoom Parallax** | Central background image zooming on scroll |
| **Scroll Progress Path** | SVG line drawing along scroll |
| **Liquid Swipe Transition** | Page transition like viscous liquid |

## Galleries & Media

| Pattern | Description |
|---------|-------------|
| **Coverflow Carousel** | 3D carousel with angled edges |
| **Drag-to-Pan Grid** | Boundless draggable canvas |
| **Accordion Image Slider** | Narrow strips expanding on hover |
| **Hover Image Trail** | Mouse leaves popping image trail |
| **Glitch Effect Image** | RGB-channel shift on hover |

## Typography & Text

| Pattern | Description |
|---------|-------------|
| **Kinetic Marquee** | Endless text bands reversing on scroll |
| **Text Mask Reveal** | Massive type as transparent window to video |
| **Text Scramble Effect** | Matrix-style decoding on load / hover |
| **Circular Text Path** | Text curving along spinning circle |
| **Gradient Stroke Animation** | Outlined text with running gradient |

## Micro-Interactions & Effects

| Pattern | Description |
|---------|-------------|
| **Particle Explosion Button** | CTA shatters into particles on success |
| **Skeleton Shimmer** | Shifting light reflection across placeholders |
| **Directional Hover-Aware Button** | Fill enters from cursor's exact side |
| **Ripple Click Effect** | Wave from click coordinates |
| **Animated SVG Line Drawing** | Vectors drawing themselves in real time |
| **Mesh Gradient Background** | Organic lava-lamp blobs |
| **Lens Blur Depth** | Background UI blurred to focus foreground action |

## Animation Library Choice

| Library | Use for |
|---------|---------|
| **Motion (`motion/react`)** | Default for UI / Bento / state-change motion |
| **GSAP + ScrollTrigger** | Full-page scrolltelling and scroll hijacks. Isolate in dedicated leaf components |
| **Three.js / WebGL** | Canvas backgrounds and 3D scenes. Same isolation rule |
| **CSS scroll-driven animations** | Lightweight scroll-linked effects (`animation-timeline: view()`) |

**NEVER mix GSAP / Three.js with Motion in the same component tree.** They fight over the same frames.

## Canonical Code Skeletons

### Scroll-Reveal Stagger (lightweight, no GSAP needed)

```tsx
"use client";
import { motion, useReducedMotion } from "motion/react";

export function RevealStagger({ items }: { items: string[] }) {
  const reduce = useReducedMotion();
  return (
    <ul className="grid gap-6">
      {items.map((item, i) => (
        <motion.li
          key={item}
          initial={reduce ? false : { opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{
            duration: 0.6,
            delay: i * 0.06,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          {item}
        </motion.li>
      ))}
    </ul>
  );
}
```

Use for: feature lists, testimonial grids, logo walls - anything that just needs "enter on scroll." Save GSAP for actual pin/scrub work.

### Glassmorphism / Frosted Glass (web approximation)

```css
.glass-panel {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid rgb(255 255 255 / .32);
  background:
    linear-gradient(135deg, rgb(255 255 255 / .30), rgb(255 255 255 / .08)),
    rgb(255 255 255 / .12);
  backdrop-filter: blur(24px) saturate(180%) contrast(1.05);
  -webkit-backdrop-filter: blur(24px) saturate(180%) contrast(1.05);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / .48),
    inset 0 -1px 0 rgb(255 255 255 / .12),
    0 18px 60px rgb(0 0 0 / .18);
}

@media (prefers-color-scheme: dark) {
  .glass-panel {
    border-color: rgb(255 255 255 / .18);
    background:
      linear-gradient(135deg, rgb(255 255 255 / .16), rgb(255 255 255 / .04)),
      rgb(15 23 42 / .42);
  }
}

@media (prefers-reduced-transparency: reduce) {
  .glass-panel {
    background: rgb(255 255 255 / .96);
    backdrop-filter: none;
  }
}
```

**Important:** Not official Apple Liquid Glass. This is a web approximation using `backdrop-filter`. Always provide enough contrast even without blur.
