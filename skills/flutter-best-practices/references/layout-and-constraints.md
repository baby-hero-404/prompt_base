# Layout and Constraints

Core rule: **Constraints go down. Sizes go up. Parent sets position.** Every layout error is a failed negotiation: a parent passed unbounded (infinite) constraints, or a child asked for more than it was given.

## Error Signature Table

Diagnose from the **first** exception in the console. Cascading errors come later and can be ignored.

| Signature | Cause | Fix |
|---|---|---|
| `Vertical viewport was given unbounded height` | Scrollable (`ListView`, `GridView`) inside an unbounded vertical parent (`Column`) | Wrap the scrollable in `Expanded`, or give it a height with `SizedBox`/`ConstrainedBox` |
| `Horizontal viewport was given unbounded width` | Horizontal scrollable inside `Row` | Same fix on the horizontal axis |
| `An InputDecorator ... cannot have an unbounded width` | `TextField` / `TextFormField` inside `Row` | Wrap in `Expanded` or `Flexible`, or `SizedBox(width: ...)` |
| `A RenderFlex overflowed by N pixels` | A child of `Row`/`Column` wants more than the main axis offers (yellow-black stripes) | `Expanded` (fill), `Flexible` (may be smaller), `Text(overflow: TextOverflow.ellipsis)`, `Wrap` for chips and tags |
| `Incorrect use of ParentData widget` | `Expanded`/`Flexible` not a direct child of `Flex`; `Positioned` not a direct child of `Stack` | Move the widget so it is the direct child of its required parent |
| `RenderBox was not laid out` | **Cascading side effect** | Ignore; scroll up to the original constraint error |
| `BoxConstraints forces an infinite width/height` | Child with `double.infinity` inside unbounded parent | Bound the parent or use `LayoutBuilder` to read real constraints |
| `Bottom overflowed` when keyboard opens | Fixed-height body on a `Scaffold` | Put scrollable content in the body; keep `resizeToAvoidBottomInset` true |

## Fix Workflow (Task Progress)

- [ ] Run in debug mode and capture the exact exception text.
- [ ] Identify the primary error (skip `RenderBox was not laid out`).
- [ ] Open the widget named in the stack trace's "relevant error-causing widget".
- [ ] Apply the fix from the table for that signature.
- [ ] Hot reload.
- [ ] **Validator loop:** inspect the screen for red/grey error panel or stripes -> if a new error appears, repeat from step 2.
- [ ] Re-test at a narrow (320 px) and wide (1200 px) window.

## Before and After

```dart
// ERROR: Vertical viewport was given unbounded height
Column(children: [
  const Text('Header'),
  ListView(children: items),
])

// FIX: the list takes the remaining height
Column(children: [
  const Text('Header'),
  Expanded(child: ListView(children: items)),
])
```

```dart
// ERROR: InputDecorator cannot have an unbounded width
Row(children: [const Icon(Icons.search), TextField()])

// FIX
Row(children: [const Icon(Icons.search), Expanded(child: TextField())])
```

```dart
// ERROR: RenderFlex overflowed (long text)
Row(children: [const Icon(Icons.info), Text(longMessage)])

// FIX: text wraps inside remaining width
Row(children: [const Icon(Icons.info), Expanded(child: Text(longMessage))])
```

## Expanded vs Flexible

- `Expanded` = `Flexible(fit: FlexFit.tight)`: child **must** fill its share.
- `Flexible` (default `FlexFit.loose`): child may be smaller than its share but never larger.
- `flex` is the ratio among siblings: `Expanded(flex: 2)` + `Expanded(flex: 1)` is 2/3 and 1/3.

## Why Not `SingleChildScrollView`?

It removes the bound that was producing the error by giving the child infinite space. Side effects: lazy loading is lost for children, scroll position and performance degrade, and the real design problem (what should shrink?) stays hidden. Use it only when content is genuinely a short, variable-height page (a form) and wrap `Column` with `mainAxisSize: MainAxisSize.min` where needed. Never nest a `ListView` in a `SingleChildScrollView` with `shrinkWrap: true` for long data; use slivers (`CustomScrollView`).

## Responsive and Adaptive Layout

Measure the **window**, not the device.

| Need | Use |
|---|---|
| Size of the whole app window | `MediaQuery.sizeOf(context)` (rebuilds only when size changes) |
| Space the parent gives this widget | `LayoutBuilder` -> `constraints.maxWidth` |
| Safe areas, notches | `SafeArea`, `MediaQuery.paddingOf(context)` |

Rules:
- Do not branch on "phone" or "tablet", and do not use `OrientationBuilder` near the root to switch layouts. Windows resize, split-screen and foldables break both assumptions.
- Do not lock orientation unless required. If it is mandated, read screen size from the Display API, not `MediaQuery`, in compatibility mode.
- Support mouse, trackpad and keyboard shortcuts as well as touch.

### Breakpoint Pattern

```dart
const double compactMax = 600;   // phones
const double mediumMax = 840;    // small tablets, foldables

class AdaptiveScaffold extends StatelessWidget {
  const AdaptiveScaffold({super.key, required this.list, required this.detail});
  final Widget list;
  final Widget detail;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
        builder: (context, constraints) {
          if (constraints.maxWidth > mediumMax) {
            return Row(children: [
              SizedBox(width: 320, child: list),
              const VerticalDivider(width: 1),
              Expanded(child: detail),
            ]);
          }
          return list; // navigate to detail on tap
        },
      );
}
```

### Large-Screen Checklist

- [ ] Constrain readable content: `Center(child: ConstrainedBox(constraints: BoxConstraints(maxWidth: 800), child: ...))`.
- [ ] Prefer `GridView.builder` with `SliverGridDelegateWithMaxCrossAxisExtent` so column count follows width.
- [ ] Use a navigation rail or sidebar above the medium breakpoint, bottom bar below.
- [ ] Resize the window and confirm no overflow at every breakpoint boundary.

## Quick Layout Reference

```dart
Column(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.stretch, children: [...]);
Row(children: [Expanded(flex: 2, child: a), Expanded(flex: 1, child: b)]);
Stack(children: [Positioned.fill(child: background), Align(alignment: Alignment.bottomCenter, child: cta)]);
Wrap(spacing: 8, runSpacing: 8, children: chips);        // flows to next line instead of overflowing
```

Prefer `SizedBox` over `Container` for pure sizing/spacing, and `Gap`-style `SizedBox(height: 8)` over empty `Container`s.
