# star-spec

The canonical StarIntel document contract, authored in StarLang and projected
to JSON Schema for existing StarIntel consumers.

The current release coordinate is `0.9.1.2`. It intentionally differs from
the inherited document `schema_version` (`0.9.0`) and the new `actor-config`
profile version (`0.9.2`). These values are separate compatibility axes.

## Layout

- `spec/starintel-doc-v0.9.1.2.star` — authored type registry and additive profiles.
- `canonical/0.9.0/` — immutable files pinned by `starintel-server`'s schema lock.
- `generated/0.9.1.2/` — reproducible portable manifest and JSON Schemas.
- `spec/release.lock.json` — hashes, upstream commits, and the three version axes.
- `spec/geo/` — additive StarIntel Geo profile, projection semantics, reference rules,
  fixtures, rendering contracts, TAK/XR/offline projections, and conformance requirements.

The old JSON Schema contains nested constraints that current StarLang expresses
as typed `map` boundaries. Generation overlays new declarations onto that exact
immutable schema; it does not rebuild or weaken old branches. The compatibility
test compares every inherited dtype branch byte-for-byte as parsed JSON.

## Update flow

Edit the `.star` source, bump the four-part release coordinate according to
`AGENTS.md`, then run:

```sh
python3 tools/spec_pipeline.py lock
make generate check test
```

The `Update generated spec` workflow performs the same operation on an explicit
four-part release branch. `Spec CI` additionally compiles the source with the
pinned official Common Lisp StarLang compiler and compares its portable manifest
with the checked-in projection.

## Actor configuration

`actor-config` v0.9.2 is tenant scoped and supports actor-specific profile and
hashtag targets, persistent scheduling/parameters, credential references, and
one-run execution. It stores stable authorization groups (`basic`, `plus`,
`professional`, `enterprise`) but no prices, secrets, or effective quota values.
Servers own effective quota policy and secret resolution.

## StarIntel Geo

The Geo profile is an additive compatibility axis and does not change the inherited
document `schema_version`.

Its central rule is that geography is a **projection of the canonical StarIntel
knowledge graph**, not a parallel map database. Direct geometry, explicit geo anchors,
and rule-derived spatial associations remain distinct through storage, APIs, tiles,
TAK projections, Android/web clients, offline packs, and XR rendering.

See `spec/geo/starintel-geo-v1.md`.
