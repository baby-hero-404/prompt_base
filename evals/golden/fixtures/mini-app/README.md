# mini-app

A tiny in-memory key-value HTTP service. Three routes: `GET /get/:key`, `POST /set`, `GET /stats`.
Values are cached with a TTL so repeated reads of the same key are cheap.
