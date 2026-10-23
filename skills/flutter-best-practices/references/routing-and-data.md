# Routing and Data

Covers `go_router`, networking with `http`, JSON models, and localization. Check `pubspec.yaml` first; if the project uses `auto_route`, `Navigator 1.0`, `dio`, `retrofit` or `json_serializable`, extend that instead of introducing a second approach.

## 1. Declarative Routing with go_router

```bash
flutter pub add go_router
```

Concepts: `GoRouter` (route tree + redirect), `GoRoute` (path -> screen), `ShellRoute` / `StatefulShellRoute` (persistent shell such as a bottom bar), path URL strategy (no `#` on web).

### Setup
```dart
import 'package:flutter_web_plugins/url_strategy.dart';

void main() {
  usePathUrlStrategy();                 // web only effect; safe elsewhere
  runApp(const ProviderScope(child: App()));
}

final routerProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authProvider.notifier);      // a Listenable/refresh source
  return GoRouter(
    initialLocation: '/',
    refreshListenable: auth,                          // re-run redirect on login/logout
    redirect: (context, state) {
      final loggedIn = ref.read(authProvider).isAuthenticated;
      final atLogin = state.matchedLocation == '/login';
      if (!loggedIn && !atLogin) return '/login';
      if (loggedIn && atLogin) return '/';
      return null;                                    // no redirect
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      StatefulShellRoute.indexedStack(
        builder: (context, state, shell) => ScaffoldWithNav(shell: shell),
        branches: [
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/',
              builder: (_, __) => const HomeScreen(),
              routes: [
                GoRoute(
                  path: 'items/:id',
                  name: 'item',
                  builder: (_, state) => ItemScreen(id: state.pathParameters['id']!),
                ),
              ],
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
          ]),
        ],
      ),
    ],
  );
});

class App extends ConsumerWidget {
  const App({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) =>
      MaterialApp.router(routerConfig: ref.watch(routerProvider));
}
```

### Navigating
```dart
context.go('/items/42');             // replaces the stack to this location (declarative)
context.push('/items/42');           // pushes on top, back returns here
context.pop();
context.goNamed('item', pathParameters: {'id': '42'}, queryParameters: {'tab': 'reviews'});
```
Reading: `state.pathParameters['id']`, `state.uri.queryParameters['tab']`.

Rules:
- Use `go` for moving between destinations (tabs, deep links), `push` for modal/detail flows that should return.
- Keep auth/redirect logic in `redirect`, not in screens. Redirect must be fast, synchronous, and return `null` when nothing changes (otherwise redirect loops).
- Pass **ids** in the URL and load the object in the destination; do not pass large objects via `extra` (lost on web refresh/deep link).
- Keep route paths in constants; name routes if you navigate by name.
- Test redirects with a router built from a fake auth state.

### Platform Deep Links
Android (`AndroidManifest.xml`, inside the main activity):
```xml
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW"/>
  <category android:name="android.intent.category.DEFAULT"/>
  <category android:name="android.intent.category.BROWSABLE"/>
  <data android:scheme="https" android:host="example.com"/>
</intent-filter>
```
Host `/.well-known/assetlinks.json` for verified App Links.

iOS: add Associated Domains (`applinks:example.com`) in the Runner capabilities and host `apple-app-site-association`. For custom schemes use `CFBundleURLTypes` in `Info.plist`. Flutter handles deep links by default in recent SDKs; only set `FlutterDeepLinkingEnabled` explicitly if a plugin or old setup requires it.

## 2. Networking with `http`

```bash
flutter pub add http
```
Permissions: Android `<uses-permission android:name="android.permission.INTERNET"/>` in the main manifest (release builds need it); macOS add `com.apple.security.network.client` = true to `DebugProfile.entitlements` and `Release.entitlements`.

### Service Pattern
```dart
class ApiClient {
  ApiClient({http.Client? client, required this.baseUrl}) : _client = client ?? http.Client();
  final http.Client _client;
  final String baseUrl;

  Future<UserApiModel> fetchUser(String id, {String? token}) async {
    final res = await _client.get(
      Uri.parse('$baseUrl/users/$id'),
      headers: {if (token != null) HttpHeaders.authorizationHeader: 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw ApiException(res.statusCode, res.body);   // NEVER return null on failure
    }
    return UserApiModel.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<UserApiModel> createUser(NewUser u) async {
    final res = await _client.post(
      Uri.parse('$baseUrl/users'),
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: jsonEncode(u.toJson()),
    );
    if (res.statusCode != 201) throw ApiException(res.statusCode, res.body);
    return UserApiModel.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }
}
```

Rules:
- Always `Uri.parse` / `Uri.https(host, path, query)`; never string-concatenate query strings with user input.
- Success codes: 200 (GET/PUT/DELETE), 201 (POST). Throw a typed exception otherwise; null results leave `FutureBuilder`/UI stuck on loading.
- Inject `http.Client` so tests pass `MockClient` (`package:http/testing.dart`).
- Add timeouts (`.timeout(const Duration(seconds: 15))`) and map transport errors (`SocketException`, `TimeoutException`) to domain errors in the repository.
- Never log tokens. Store secrets with `flutter_secure_storage`, not `shared_preferences`.
- Create the future once (provider/ViewModel), not in `build()`.

## 3. JSON Serialization

Default to **manual** `fromJson`/`toJson` for small models; use `json_serializable` (+ `build_runner`) or `freezed` when the project already does or the model count is large.

```dart
class User {
  const User({required this.id, required this.name, this.email});

  final String id;
  final String name;
  final String? email;

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        name: json['name'] as String,
        email: json['email'] as String?,
      );

  Map<String, dynamic> toJson() => {'id': id, 'name': name, if (email != null) 'email': email};
}
```

Dart 3 pattern version, validating shape and destructuring in one step:
```dart
factory User.fromJson(Map<String, dynamic> json) => switch (json) {
      {'id': String id, 'name': String name} => User(id: id, name: name, email: json['email'] as String?),
      _ => throw FormatException('Invalid User JSON: $json'),
    };
```

Checklist:
- [ ] `final` fields, `const` constructor, `copyWith` and `==`/`hashCode` if used in state (or `freezed`).
- [ ] Cast `jsonDecode` to `Map<String, dynamic>` / `List<dynamic>` explicitly.
- [ ] Handle optional and missing keys deliberately; decide default vs error.
- [ ] Parse big payloads with `compute(parseFn, body)` (top-level function).
- [ ] Unit test `fromJson`, `toJson`, and a malformed input (see `testing.md`).
- [ ] Keep API models (data layer) separate from domain models when the API shape is not what the UI needs.

## 4. Localization (gen_l10n)

```bash
flutter pub add flutter_localizations --sdk=flutter
flutter pub add intl:any
```
`pubspec.yaml`: `flutter: { generate: true }`. `l10n.yaml`:
```yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
```
If `flutter pub get` reports the synthetic package/`flutter_gen` as deprecated for your SDK, follow its message (generated file lives in the source tree and is imported by normal path) instead of the older `package:flutter_gen/...` import.

```dart
MaterialApp(
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
  ...
);
Text(AppLocalizations.of(context).helloWorld);
```

ARB (`lib/l10n/app_en.arb`):
```json
{
  "helloUser": "Hello {name}",
  "@helloUser": { "description": "Greeting", "placeholders": { "name": { "type": "String", "example": "Ada" } } },
  "itemCount": "{count, plural, =0{No items} =1{1 item} other{{count} items}}",
  "@itemCount": { "placeholders": { "count": { "type": "int" } } }
}
```
Rules: new key goes in the template ARB first with a `description`; update every locale file when editing a key; plural `other` case is mandatory; never build sentences by concatenating translated fragments; use `DateFormat`/`NumberFormat` with the active locale; run `flutter pub get` (or `flutter gen-l10n`) and fix ARB syntax errors until it passes.
