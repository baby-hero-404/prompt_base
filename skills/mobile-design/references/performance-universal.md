# Universal Mobile Performance (Memory, Battery, Network)

## 1. Frame Budget (60fps/120fps)

- **60fps** → 16.6ms per frame.
- **120fps (ProMotion)** → 8.3ms per frame.
- **Rule**: If a calculation takes longer than the budget, move it to a background thread or a web worker (if available).

---

## 2. Animation Performance (GPU vs CPU)

| GPU Accelerated (FAST) | CPU Bound (SLOW) |
|-------------------------|------------------|
| `transform` (Translate, Scale, Rotate) | `width`, `height` |
| `opacity` | `top`, `bottom`, `left`, `right` |
| | `margin`, `padding`, `border-radius` |

**Mandate**: Only animate `transform` and `opacity`.

---

## 3. Battery & Hardware Optimization

- **OLED Dark Mode**: Use true black (#000000) to save battery; black pixels are literally turned off.
- **Sensors**: Batch GPS/Sensor updates. Use "Significant Change" instead of "Continuous" when possible.
- **Network**: Batch API requests. The mobile radio consumes most power during the transition from "idle" to "active".

---

## 4. Network Performance (Offline-First)

1. **Read Cache FIRST**: Show available data instantly.
2. **Fetch Network**: Update in background.
3. **Optimistic UI**: Update UI immediately on action, rollback if network fails.
- **Mitigation**: Use Brotli/Gzip compression and ETag headers to reduce payload transfer.

---

## 5. Memory Management (The 8MB Rule)

One 1080p RGBA image takes ~8.3MB (1920x1080x4).
- **Rule**: Never load images larger than display size.
- **Leak Prevention**: Clear subscriptions and timers on screen unmount.
