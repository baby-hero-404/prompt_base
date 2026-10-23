# Camera, Tiled Maps, Audio, Particles (Flame 1.x)

## Camera and World

Flame 1.x uses `World` (game content) + `CameraComponent` (view). Add content to the world, never directly to the game, if you use a camera.

```dart
class MyGame extends FlameGame {
  late final Player player;

  @override
  Future<void> onLoad() async {
    final world = World();
    player = Player();
    await world.add(player);

    camera = CameraComponent.withFixedResolution(world: world, width: 800, height: 600);
    await addAll([world, camera]);

    camera.follow(player, maxSpeed: 300);                       // smooth follow
    camera.setBounds(Rectangle.fromLTRB(400, 300, mapW - 400, mapH - 300));   // keep view inside the map
  }
}
```
- `withFixedResolution` gives the same visible area on every screen size (letterboxed); use plain `CameraComponent(world: world)` when you want more area on bigger screens.
- Bounds are for the **camera centre**; shrink the map rectangle by half the viewport so edges are not shown.
- Zoom: `camera.viewfinder.zoom = 2.0;` or animate with an effect.
- HUD: `camera.viewport.add(hud)` (fixed on screen). World objects: `world.add(...)`.
- Parallax: `loadParallaxComponent([...ParallaxImageData...], baseVelocity: Vector2(50, 0), velocityMultiplierDelta: Vector2(1.5, 0))` added to the camera backdrop (`camera.backdrop.add(parallax)`) or the world.

## Tiled Maps (flame_tiled)

```dart
final map = await TiledComponent.load('map.tmx', Vector2.all(32));   // destination tile size
await world.add(map);

// spawn points and objects from an object layer
final objects = map.tileMap.getLayer<ObjectGroup>('objects')?.objects ?? const [];
for (final o in objects) {
  switch (o.name) {
    case 'player_spawn':
      player.position = Vector2(o.x, o.y);
    case 'enemy':
      await world.add(Enemy(position: Vector2(o.x, o.y)));
  }
}
```

Collision from the map: draw rectangle objects in a Tiled object layer named `collisions` and create passive hitboxes from them (cheap) instead of one component per solid tile.
```dart
for (final r in map.tileMap.getLayer<ObjectGroup>('collisions')?.objects ?? const []) {
  world.add(PositionComponent(position: Vector2(r.x, r.y), size: Vector2(r.width, r.height))
    ..add(RectangleHitbox()..collisionType = CollisionType.passive));
}
```
Rules:
- Put `.tmx` and tileset images under the registered asset folders; paths inside the `.tmx` are relative.
- Keep layer names as constants shared with the Tiled file.
- Embed tilesets in the map or ensure external `.tsx` files are bundled.
- Merge adjacent solid tiles into larger rectangles for big maps.

## Audio (flame_audio)

```dart
import 'package:flame_audio/flame_audio.dart';

class MyGame extends FlameGame {
  @override
  Future<void> onLoad() async {
    await FlameAudio.audioCache.loadAll(['jump.wav', 'coin.wav', 'bgm.mp3']);   // preload
    FlameAudio.bgm.play('bgm.mp3', volume: 0.5);
  }

  @override
  void onRemove() {
    FlameAudio.bgm.dispose();
    super.onRemove();
  }
}

FlameAudio.play('jump.wav', volume: 0.8);           // one-shot effect
```
Rules: preload everything you will play, use short WAV/OGG for effects and MP3/OGG for music, pause music on app background (`FlameAudio.bgm` observes lifecycle once `initialize()` is called on versions that require it; check the version), and expose a mute toggle.

## Particles

```dart
class Explosion extends ParticleSystemComponent {
  Explosion({required Vector2 position})
      : super(
          position: position,
          particle: Particle.generate(
            count: 20,
            lifespan: 0.5,
            generator: (i) => AcceleratedParticle(
              acceleration: Vector2.random() * 100,
              speed: Vector2.random() * 200,
              child: CircleParticle(radius: 4, paint: Paint()..color = Colors.orange),
            ),
          ),
        );
}
```
`ParticleSystemComponent` removes itself when the particle completes. Keep counts small on mobile; reuse `Paint` objects; for custom visuals use `ComputedParticle(renderer: (canvas, particle) { ... })` with `particle.progress` (0..1).

## Game Performance Checklist

- [ ] Movement and animation use `dt`.
- [ ] Images, sprites, audio loaded once in `onLoad`.
- [ ] No `Paint()`/`Vector2()` allocation inside `render`/`update` hot paths.
- [ ] Spawn/despawn rate high? Pool or reset objects.
- [ ] Off-screen components skip expensive work (compare against `camera.visibleWorldRect`).
- [ ] Profile with DevTools in profile mode on a low-end device; target stable 60 FPS.
