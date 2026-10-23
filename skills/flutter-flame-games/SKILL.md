---
name: flutter-flame-games
description: "Use when building or refactoring 2D games with Flutter and the Flame engine: game loop, components, sprites, collision, input, camera, Tiled maps. Triggers on flame engine, flame game, flame_audio, flame_tiled, FlameGame."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
references: [collision-and-input.md, camera-tiled-audio.md]
---

# Flutter Flame Games

> **Philosophy:** Everything is a `Component`. Logic runs in `update(dt)`, drawing in `render(canvas)`. Movement is always multiplied by `dt`.
> **Scope:** Flame (1.x) 2D games. For general Flutter code (state, tests, layout of menus), see the flutter-best-practices skill. For game design, genre, and art, see the game-development skill.

## Step 0: Check versions

Read `pubspec.yaml` for `flame`, `flame_audio`, `flame_tiled`, and the Dart SDK. Flame APIs changed across minor versions (camera, input events, `HasGameReference` replaced `HasGameRef`). If a snippet does not analyze, check the package changelog before rewriting.

## Selective Loading Rule

| Task | Load |
|---|---|
| Hitboxes, collision callbacks, keyboard, tap, drag, joystick | `references/collision-and-input.md` |
| Camera follow/bounds/zoom, Tiled maps, audio, particles, parallax | `references/camera-tiled-audio.md` |

## Setup

```bash
flutter pub add flame
flutter pub add flame_audio   # optional
flutter pub add flame_tiled   # optional
```
Register assets in `pubspec.yaml` (`assets/images/`, `assets/audio/`, `assets/tiles/`). Flame loads images from `assets/images/` and audio from `assets/audio/` by default.

```dart
void main() => runApp(GameWidget(game: MyGame()));
```
Use `GameWidget.controlled(gameFactory: MyGame.new)` when the game must be recreated (hot restart friendly) and wrap with `overlayBuilderMap` for Flutter UI (HUD, pause menu).

## Architecture

```dart
class MyGame extends FlameGame with HasCollisionDetection, HasKeyboardHandlerComponents {
  @override
  Future<void> onLoad() async {
    await add(Player());
  }
}
```

| Mixin | Purpose |
|---|---|
| `HasCollisionDetection` | Enables the collision system for the whole game |
| `HasKeyboardHandlerComponents` | Routes keyboard events to components using `KeyboardHandler` |
| `HasGameReference<MyGame>` (on a component) | Typed access to `game` |
| `TapCallbacks` / `DragCallbacks` / `HoverCallbacks` | Pointer input on a component |
| `CollisionCallbacks` | Receive collision events on a component |

Component tree: `Component` -> `PositionComponent` (`SpriteComponent`, `SpriteAnimationComponent`, `TextComponent`, `ShapeComponent`), plus `ParticleSystemComponent`, `ParallaxComponent`, `World`, `CameraComponent`.

Lifecycle:
```dart
class Enemy extends PositionComponent with HasGameReference<MyGame> {
  @override Future<void> onLoad() async { /* once: load assets, add children/hitboxes */ }
  @override void onMount() { /* every time it is added to the tree */ }
  @override void update(double dt) { /* every frame; dt in seconds */ }
  @override void render(Canvas canvas) { /* custom drawing */ }
  @override void onRemove() { /* cleanup */ }
}
```

## Sprites and Animation

```dart
class Player extends SpriteAnimationComponent with HasGameReference<MyGame> {
  Player() : super(size: Vector2.all(64), anchor: Anchor.center);

  @override
  Future<void> onLoad() async {
    final image = await game.images.load('player_run.png');   // cached by Flame
    animation = SpriteAnimation.fromFrameData(
      image,
      SpriteAnimationData.sequenced(amount: 8, stepTime: 0.1, textureSize: Vector2.all(64)),
    );
  }
}
```
Use `SpriteSheet` for grids, one `SpriteAnimation` per state, and swap `animation` (or use `SpriteAnimationGroupComponent` with a state enum) instead of creating new components.

## Hard Rules

| ID | Rule |
|---|---|
| G1 | **Frame-rate independence.** `position += velocity * speed * dt`; never add a constant per frame |
| G2 | **No allocation churn in `update`/`render`.** Reuse `Vector2`, `Paint`, `TextPaint`; preload images in `onLoad` |
| G3 | **Pool frequent objects** (bullets, particles) or reuse via `removeFromParent` + reset when spawn rate is high |
| G4 | **Cleanup.** Cancel timers, dispose audio (`FlameAudio.bgm.dispose()`), clear listeners in `onRemove` |
| G5 | **Keep Flutter UI out of the game loop.** HUD/menus are overlays driven by `ValueNotifier`, not by `setState` per frame |
| G6 | **Game state outside components** (score, lives, level) in the game or a small state class, so tests and overlays can read it |
| G7 | **Test logic without rendering.** Use `flame_test` (`testWithFlameGame`) for components; extract pure functions for rules |
| G8 | **Mark hitboxes passive** when they only need to be hit (walls, pickups) to save collision work |

## Overlays (HUD / Pause)

```dart
GameWidget(
  game: game,
  overlayBuilderMap: {
    'Hud': (context, MyGame g) => HudOverlay(score: g.score),         // ValueNotifier<int>
    'Pause': (context, MyGame g) => PauseMenu(onResume: g.resume),
  },
  initialActiveOverlays: const ['Hud'],
);

// in the game
void pause()  { overlays.add('Pause');    pauseEngine(); }
void resume() { overlays.remove('Pause'); resumeEngine(); }
```

## Anti-Patterns

- Moving by pixels per frame (speed changes with device refresh rate).
- Loading images or audio inside `update`/`render`.
- Putting game rules in widgets (overlays should only display state and send commands).
- Using `setState` to update the HUD every frame.
- Adding hitboxes to everything as `active`; only the mover needs to be active.
- One giant `FlameGame` subclass holding all logic instead of components with their own behaviour.

## Task Progress

- [ ] Read `pubspec.yaml` versions (Step 0)
- [ ] Game class with needed mixins; `GameWidget` in `main`
- [ ] Assets registered and preloaded in `onLoad`
- [ ] Components for player/enemies with `update(dt)` movement
- [ ] Hitboxes + collision callbacks (`references/collision-and-input.md`)
- [ ] Input for target platforms (touch joystick for mobile, keyboard for desktop)
- [ ] Camera/world/map (`references/camera-tiled-audio.md`)
- [ ] Overlays for HUD/pause
- [ ] **Validator loop:** `flutter analyze` -> `flutter test` -> run on a low-end device and watch FPS -> fix -> repeat
