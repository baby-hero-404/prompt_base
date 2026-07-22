# React Native Performance Optimization

## 1. List Optimization (The #1 AI Mistake)

### 🚫 ScrollView for Long Lists (FORBIDDEN)
Renders all items immediately. Memory explodes.
- ✅ **ALWAYS** use `FlatList` or `FlashList` (@shopify/flash-list).

### 2. FlatList Optimization Checklist

```javascript
// 1. Memoize the item component
const ListItem = React.memo(({ item }: { item: Item }) => {
  return (
    <Pressable style={styles.item}>
      <Text>{item.title}</Text>
    </Pressable>
  );
});

// 2. Memoize renderItem with useCallback
const renderItem = useCallback(
  ({ item }: { item: Item }) => <ListItem item={item} />,
  [] 
);

// 3. Stable keyExtractor (NEVER use index!)
const keyExtractor = useCallback((item: Item) => item.id, []);

// 4. getItemLayout for fixed-height items
const getItemLayout = useCallback(
  (data: Item[] | null, index: number) => ({
    length: ITEM_HEIGHT, offset: ITEM_HEIGHT * index, index,
  }),
  []
);

// 5. Apply with Performance Props
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={keyExtractor}
  getItemLayout={getItemLayout}
  removeClippedSubviews={true} 
  maxToRenderPerBatch={10} 
  windowSize={5} 
/>
```

---

## 3. Animation Performance

### Native Driver vs JS Thread
- ✅ `useNativeDriver: true` for `transform` and `opacity`.
- ❌ Animating `width`, `height`, `margin`, `padding` or `borderRadius` on the JS thread.

### Reanimated 3 (The Standard)
Use for complex, gesture-driven animations that run 100% on the UI thread.
```javascript
const animatedStyles = useAnimatedStyle(() => ({
  transform: [{ translateX: withSpring(offset.value) }],
}));
```

---

## 4. Memory Hygiene

- **Cleanup**: Always `clearInterval`, `clearTimeout`, and remove event listeners in `useEffect` return.
- **Async Guards**: Use `AbortController` or `isMounted` ref to prevent state updates after unmount.
- **Images**: Use `react-native-fast-image` for better caching and memory handling.

---

## 5. Summary Checklist

- [ ] `FlatList`/`FlashList` used for all lists?
- [ ] List items wrapped in `React.memo`?
- [ ] `useNativeDriver: true` or Reanimated for animations?
- [ ] `console.log` removed (critical for production speed)?
