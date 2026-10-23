# Collision and Input (Flame 1.x)

Verify signatures against the installed `flame` version; these match the current 1.x event API.

## Collision Detection

### Setup
```dart
class MyGame extends FlameGame with HasCollisionDetection {
  @override
  Future<void> onLoad() async {
    await addAll([Player(), Enemy(), ScreenHitbox()]);   // ScreenHitbox = world edges
  }
}

class Player extends PositionComponent with CollisionCallbacks {
  Player() : super(size: Vector2.all(48));

  @override
  Future<void> onLoad() async {
    add(RectangleHitbox());             // sized to the parent by default
    // add(CircleHitbox(radius: 20));
    // add(PolygonHitbox([Vector2(0, 0), Vector2(20, 10), Vector2(0, 20)]));
  }

  @override
  void onCollisionStart(Set<Vector2> points, PositionComponent other) {
    super.onCollisionStart(points, other);
    if (other is Enemy) takeDamage();
    if (other is ScreenHitbox) {/* hit the edge */}
  }

  @override
  void onCollision(Set<Vector2> points, PositionComponent other) {}   // every frame while overlapping

  @override
  void onCollisionEnd(PositionComponent other) {}
}
```
Always call `super` in callbacks.

### Collision Types
| Type | Behaviour | Use for |
|---|---|---|
| `CollisionType.active` (default) | Checks against active and passive | Player, projectiles, enemies |
| `CollisionType.passive` | Can be hit, does not check others | Walls, pickups, triggers |
| `CollisionType.inactive` | Ignored | Temporarily disabled hitbox |

```dart
add(RectangleHitbox()..collisionType = CollisionType.passive);
```
Two passive hitboxes never collide with each other. Prefer one active mover against many passive objects.

### Tips
- Hitbox smaller than the sprite feels fairer (`RectangleHitbox.relative(Vector2.all(0.8), parentSize: size)`).
- Use `triggersParentCollision = false` on hitboxes that should not notify the parent.
- Resolve overlap by moving the mover back using the `points` or by separating along the smaller overlap axis; do not rely on the callback frequency.
- For many bodies, use the `HasQuadTreeCollisionDetection` game mixin instead of `HasCollisionDetection`.
- For physics, consider `flame_forge2d` instead of hand-rolled collision response.

## Input

### Keyboard
```dart
class Player extends SpriteComponent with KeyboardHandler {
  final Vector2 _dir = Vector2.zero();
  static const double speed = 200;

  @override
  bool onKeyEvent(KeyEvent event, Set<LogicalKeyboardKey> keysPressed) {
    _dir
      ..x = (keysPressed.contains(LogicalKeyboardKey.keyD) ? 1 : 0) -
            (keysPressed.contains(LogicalKeyboardKey.keyA) ? 1 : 0)
      ..y = (keysPressed.contains(LogicalKeyboardKey.keyS) ? 1 : 0) -
            (keysPressed.contains(LogicalKeyboardKey.keyW) ? 1 : 0);
    return true;                        // true: keep propagating to other handlers
  }

  @override
  void update(double dt) {
    if (!_dir.isZero()) position += _dir.normalized() * speed * dt;
  }
}
```
The game needs `HasKeyboardHandlerComponents`. Map keys to **actions** in one place if you support rebinding or gamepads.

### Tap
```dart
class GameButton extends SpriteComponent with TapCallbacks {
  @override void onTapDown(TapDownEvent e) => scale = Vector2.all(0.9);
  @override void onTapUp(TapUpEvent e) { scale = Vector2.all(1); onPressed(); }
  @override void onTapCancel(TapCancelEvent e) => scale = Vector2.all(1);
  void onPressed() {}
}
```
The component needs a non-zero `size`; events use its bounds. For screen-wide taps, add `TapCallbacks` to the game (`FlameGame with TapCallbacks`).

### Drag
```dart
class Draggable extends PositionComponent with DragCallbacks {
  @override void onDragUpdate(DragUpdateEvent e) => position += e.localDelta;
}
```
Use `e.localDelta` for movement relative to the component's parent; the camera zoom is already accounted for.

### Virtual Joystick (mobile)
```dart
late final JoystickComponent joystick;

@override
Future<void> onLoad() async {
  joystick = JoystickComponent(
    knob: CircleComponent(radius: 20, paint: Paint()..color = Colors.red.withAlpha(200)),
    background: CircleComponent(radius: 50, paint: Paint()..color = Colors.black.withAlpha(100)),
    margin: const EdgeInsets.only(left: 40, bottom: 40),
  );
  camera.viewport.add(joystick);        // HUD layer: does not move with the world
}

@override
void update(double dt) {
  super.update(dt);
  if (!joystick.delta.isZero()) player.position += joystick.relativeDelta * player.speed * dt;
}
```
Add HUD components (joystick, buttons, score text) to `camera.viewport`, not the world, so they stay fixed on screen.

### Input Rules
- Process input into **intent** (direction, jump pressed) and apply it in `update(dt)`; do not move directly in event callbacks.
- Normalize diagonal movement.
- Support the platforms you ship: touch controls for mobile, keyboard for desktop/web, optionally gamepad.
- Debounce or cooldown actions (shoot) with `Timer` from `package:flame/components.dart`, ticked in `update`.
