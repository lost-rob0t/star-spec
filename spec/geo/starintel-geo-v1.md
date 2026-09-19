# StarIntel Geo Profile v1

Status: **Draft / implementation-authorizing**
Profile ID: `starintel.geo`
Profile version: `1.0.0-draft.1`
Parent StarIntel spec release: `0.9.1.2`

Keywords **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY**
are normative.

---

## 1. Purpose

StarIntel Geo defines a common geographic projection plane for the StarIntel knowledge
graph. Its purpose is to answer a deceptively simple question:

> What does StarIntel know that is relevant to this place, region, route, observation,
> time window, or geometry?

The answer is not limited to documents that directly contain latitude/longitude.

A geometry-bearing place, event, observation, route, building, sensor, image, network
observation, or region can act as an anchor into the wider StarIntel graph. Documents
without intrinsic geometry MAY therefore appear in geographic interfaces when there is
an explicit, explainable, authorized relationship path connecting them to geographic
evidence.

StarIntel Geo is a projection and query system. It is not a second semantic authority,
identity authority, or evidence store.

---

## 2. Design principles

### 2.1 One graph, many projections

Canonical StarIntel documents remain authoritative. Geo implementations MUST be
rebuildable from canonical documents, assertions, relations, evidence, provenance,
temporal facts, and policy.

A map marker MUST NOT become a parallel mutable fact that can drift independently from
the underlying graph.

### 2.2 Geography has provenance

Every geographic assertion or projection MUST identify where its geometry came from.

Examples:

- operator-entered geometry;
- GPS observation;
- EXIF metadata;
- public map dataset;
- address geocoding result;
- network-reported location;
- relation to a geometry-bearing object;
- bounded expert-rule inference;
- imported external layer.

### 2.3 Derived geography is not direct geography

Implementations MUST preserve the distinction between:

- direct geometry;
- explicit relation-based anchoring;
- rule-derived spatial association.

Clients MUST NOT flatten these categories into the same semantic claim.

### 2.4 Time is part of geography

A location without time can be dangerously misleading. Geometry and relations MAY be
stable, observed, historical, predicted, or time-bounded. Geo implementations MUST
support temporal validity and observation time.

### 2.5 Explainability before spectacle

Immersive, cinematic, and graph-heavy interfaces are encouraged, but every rendered
relationship MUST be inspectable back to evidence, source, rule profile, and canonical
object identifiers.

### 2.6 Capability scoped

Map rendering does not grant data authority. Geo operations MUST respect the same
tenant, dataset, principal, purpose, capability, and field-level visibility constraints
as canonical StarIntel access.

### 2.7 Offline is first-class

The profile supports disconnected regional packs. A client MAY operate on a bounded,
signed snapshot and later reconcile with canonical services.

---

## 3. Terminology

### 3.1 Canonical document

A validated StarIntel record governed by the parent document contract.

### 3.2 Geometry-bearing document

A document with direct geometry or direct evidence supporting geometry.

### 3.3 Geo anchor

A geometry-bearing document used as the spatial anchor for one or more other documents.

### 3.4 Geo projection

A rebuildable spatial representation derived from canonical records.

### 3.5 Direct projection

A projection whose rendered document itself has supported geometry.

### 3.6 Anchored projection

A projection where the rendered document is connected through an explicit canonical
relation to a geometry-bearing anchor.

### 3.7 Derived projection

A projection produced through a named, bounded expert rule over canonical facts.

### 3.8 Spatial relation

A relationship such as inside, intersects, near, crosses, covers, adjacent-to,
observed-at, route-through, visible-from, or contained-by.

### 3.9 Geo layer

A named view over a set of authorized projections and rendering rules.

### 3.10 Geo pack

A bounded offline package containing map assets, styles, data snapshots, indexes,
policy metadata, and integrity information.

---

## 4. Canonical participation model

Every document rendered through StarIntel Geo MUST have one of these participation
kinds.

### 4.1 Direct

A direct participant has geometry supported on the document or by direct evidence.

Examples:

- a building polygon;
- an event point;
- a GPS observation;
- a vehicle track;
- a camera location and pose;
- an administrative boundary.

### 4.2 Anchored

An anchored participant has no direct geometry but has an explicit relation to a
geometry-bearing document.

Examples:

- a PDF linked to a facility;
- a person record explicitly associated with a place;
- an organization occupying a building;
- an image associated with an event;
- a source record linked to a sensor location.

The map MAY render the non-geo document at or near the anchor for interaction, but the
projection MUST retain `participationKind=anchored` and MUST NOT write the anchor's
coordinates back as the document's own geometry.

### 4.3 Derived

A derived participant is projected by a named expert rule using one or more relationship
paths.

Derived projection MUST include:

- rule profile id;
- rule version;
- path;
- evidence refs;
- input object refs;
- confidence or other rule result metadata;
- resource bounds used;
- timestamp of derivation;
- temporal scope;
- visibility scope.

A weak co-occurrence or spatial proximity result MUST NOT assert identity, ownership,
employment, residence, or other high-impact semantic conclusions without independent
evidence satisfying the corresponding ontology/rule contract.

---

## 5. Geometry model

StarIntel Geo adopts GeoJSON-compatible geometry semantics for exchange.

Required geometry families:

- Point;
- MultiPoint;
- LineString;
- MultiLineString;
- Polygon;
- MultiPolygon;
- GeometryCollection.

Implementations SHOULD support:

- altitude;
- heading;
- pitch;
- roll;
- horizontal accuracy;
- vertical accuracy;
- covariance or uncertainty envelope;
- field of view;
- range;
- route direction;
- movement speed;
- observation bearing.

Geometry MUST carry CRS assumptions explicitly when not WGS84 geographic coordinates.

A geometry object SHOULD expose:

```text
geometry
geometry_source
accuracy_meters?
altitude_meters?
heading_degrees?
observed_at?
valid_from?
valid_to?
source_ref
evidence_refs[]
confidence?
```

---

## 6. Geographic document families

The following semantic families are recommended first-class Geo participants:

- Place
- Address
- Building
- Parcel
- Site
- Region
- AdministrativeArea
- Road
- Route
- Track
- Event
- Observation
- Sensor
- Camera
- Infrastructure
- NetworkObservation
- RadioObservation
- Imagery
- GeoDataset
- Geofence
- CoverageArea
- WeatherObservation
- HazardArea

Implementations MAY extend the vocabulary through parent-spec extension mechanisms.

---

## 7. GeoProjection object

A projection SHOULD expose a normalized object equivalent to:

```json
{
  "@type": "star:GeoProjection",
  "document": "star:document:...",
  "anchor": "star:place:...",
  "participationKind": "direct|anchored|derived",
  "geometrySource": "direct_geometry|explicit_relation|expert_rule",
  "geometry": {},
  "geometryAccuracyMeters": 15,
  "relationPath": [],
  "evidenceRefs": [],
  "sourceRefs": [],
  "ruleProfile": "geo-explicit-v1",
  "ruleVersion": "1",
  "confidence": 0.91,
  "observedAt": "...",
  "validFrom": "...",
  "validTo": null,
  "tenantRef": "...",
  "datasetRef": "...",
  "projectionOnly": true
}
```

`projectionOnly=true` means the object is not itself canonical evidence.

---

## 8. Spatial graph

### 8.1 Goal

StarIntel Geo MUST support navigation in both directions:

```text
map -> canonical document -> graph -> related documents

graph -> geographic anchors -> map
```

### 8.2 Relation paths

A geographic relationship path MUST be explainable as a sequence of canonical refs and
predicates.

Example:

```text
person
  -> memberOf
organization
  -> occupies
building
  -> geometry
```

The renderer MAY place the person in the building's context, but MUST label the
projection as derived or anchored according to the relation source.

### 8.3 Path limits

Implementations MUST configure explicit limits for:

- maximum hops;
- maximum branch factor;
- maximum result count;
- maximum wall time;
- maximum intermediate facts;
- allowed predicate families;
- allowed document classes;
- tenant/dataset scope.

Unbounded graph expansion is non-conformant.

### 8.4 Path preference

When multiple valid anchors exist, clients MAY rank candidates using:

- explicit relation strength;
- evidence quality;
- temporal relevance;
- hop count;
- source independence;
- geometry accuracy;
- rule profile priority.

The ranking algorithm MUST be inspectable and SHOULD be deterministic.

---

## 9. Temporal model

Each geometry or spatial relationship can carry:

- observed time;
- recorded time;
- valid-from;
- valid-to;
- ingestion time;
- derivation time.

Map queries MUST support an `asOf` or equivalent temporal view.

Clients SHOULD provide a global time control capable of:

- instant snapshot;
- bounded range;
- playback;
- event trail;
- first-seen / last-seen;
- historical graph reconstruction.

Temporal playback MUST respect the historical validity of both geometry and relations.

A relation discovered today about a historical event MUST distinguish:

- when the underlying event occurred;
- when StarIntel recorded the relation;
- when the relation was derived.

---

## 10. Uncertainty

StarIntel Geo MUST NOT imply false precision.

Supported uncertainty representations SHOULD include:

- accuracy radius;
- bounding polygon;
- candidate geometry set;
- confidence;
- source disagreement;
- stale location;
- approximate region only.

Where only city-level evidence exists, clients MUST NOT silently render an exact street
point.

When multiple incompatible candidate locations exist, the projection layer SHOULD show
the competing claims rather than pick one without policy.

---

## 11. Provenance

Every map-visible projection MUST be traceable to canonical provenance.

Required provenance access:

- source id;
- evidence id;
- collector/actor id where applicable;
- source timestamp;
- ingest timestamp;
- transformation chain;
- rule profile/version for derived data;
- upstream dataset/source;
- license/usage metadata for external layers where applicable.

Imported layers MUST preserve attribution requirements.

---

## 12. Authorization and capability model

Geo requires explicit capabilities. Suggested capability family:

```text
geo.read
geo.query
geo.layers.read
geo.layers.write
geo.provenance.read
geo.derived.expand
geo.offline.export
geo.offline.import
geo.tak.publish
geo.xr.render
geo.admin
```

Capabilities MUST narrow, never broaden, parent authority.

A user authorized to see a building but not a linked private document MUST NOT learn the
private document exists merely because a hidden relationship produced a map count.

Aggregations MUST therefore also be visibility-aware.

---

## 13. Sensitive relationship rules

StarIntel Geo can expose powerful cross-document context. Implementations MUST preserve
the parent system's authorization boundaries and evidence semantics.

Specifically:

- proximity alone MUST NOT assert identity;
- co-location alone MUST NOT assert ownership or affiliation;
- a network-reported location MUST remain distinct from physical observation;
- historical addresses MUST retain validity intervals;
- inferred relationships MUST remain marked as inferred;
- source disagreement MUST remain representable;
- private/sensitive layers MUST require explicit capability;
- export MUST honor the same field and relation visibility constraints as interactive
  views.

---

## 14. Spatial relation vocabulary

Recommended predicates:

```text
inside
contains
intersects
overlaps
adjacentTo
near
crosses
touches
observedAt
originatesAt
terminatesAt
routeThrough
covers
visibleFrom
withinFOV
withinRange
containedByRegion
reportedInRegion
associatedWithPlace
occupies
locatedAt
serviceArea
hazardAffects
```

These predicates SHOULD distinguish asserted relations from computational relations.

---

## 15. Prolog reference semantics

Named expert profiles MAY derive candidate spatial relations.

Example classes:

- point-in-polygon containment;
- region ancestor/descendant;
- building/address containment;
- observation-in-region;
- route intersection;
- camera visibility envelope;
- repeated observation pattern;
- bounded time/space co-occurrence;
- likely-same-place candidate;
- proximity candidate.

All rule execution MUST be bounded.

Clients MUST call symbolic, registered queries. They MUST NOT submit raw Prolog source
or arbitrary goals.

Example query contract:

```json
{
  "query": "geo.relatedDocuments",
  "args": {
    "anchorRef": "star:place:...",
    "maxDepth": 3,
    "asOf": "2026-09-19T02:00:00-04:00",
    "ruleProfile": "geo-related-v1",
    "limit": 200
  }
}
```

Results SHOULD include proof metadata.

---

## 16. Query API

A conforming server SHOULD implement the following logical operations.

### 16.1 Spatial

- bbox
- polygon
- nearest
- contains
- intersects
- within
- route-crossing
- coverage
- region ancestors
- region descendants

### 16.2 Entity-centric

- geometry for entity
- anchors for entity
- documents related to anchor
- geographic context for document
- spatial history
- nearby observations
- visible layers

### 16.3 Temporal

- as-of snapshot
- range query
- changed-since
- first-seen
- last-seen
- trajectory / track

### 16.4 Provenance

- explain projection
- evidence for projection
- competing geometry claims
- derivation proof

---

## 17. Layer system

A Geo layer is a named query + style + policy contract.

A layer definition SHOULD include:

```text
layerId
version
title
description
sourceQuery
geometryKinds[]
documentClasses[]
minZoom
maxZoom
clusterPolicy
timePolicy
styleRef
capabilityRequirements[]
provenanceMode
offlineEligibility
refreshPolicy
```

Suggested initial layer families:

### World
- conflicts
- civil events
- disasters
- weather
- infrastructure incidents
- aviation
- maritime
- cyber/internet disruptions
- communications outages

### Infrastructure
- roads
- rail
- power
- telecom
- towers
- ports
- airports
- public facilities

### StarIntel
- documents
- events
- observations
- targets
- actors
- sensors
- sources
- alerts
- derived relations

### Radio / network
- access-point observations
- cellular observations
- radio coverage
- network observations
- source-reported IP geography

Layer visibility MUST respect authorization.

---

## 18. External source adapters

External map/event sources MUST be implemented as adapters, not embedded authority.

An adapter MUST declare:

- source id;
- upstream URI;
- retrieval timestamp;
- parser/version;
- license/attribution metadata;
- original feature id;
- original geometry;
- normalization mapping;
- confidence semantics;
- refresh policy.

Third-party datasets with restrictive licensing SHOULD remain separable from
commercial/internal canonical assets.

---

## 19. Vector tiles and map publication

The projection service SHOULD support vector tiles for large-scale rendering.

Preferred forms include:

- MVT for online tiled rendering;
- PMTiles for packaged/static distribution;
- GeoJSON for debugging/interchange;
- JSON-LD for semantic exchange.

Tile features MUST preserve stable canonical refs sufficient to hydrate the corresponding
StarIntel object without duplicating sensitive document payloads into every tile.

A vector tile is a rendering optimization, not an authority layer.

---

## 20. Offline regional packs

A StarIntel Geo pack SHOULD contain:

```text
manifest.json
style/
tiles/
terrain/
documents/
projections/
indexes/
rules/
icons/
attribution/
integrity/
```

The manifest MUST specify:

- region geometry;
- build time;
- source snapshot sequence/checkpoint;
- parent StarIntel spec version;
- Geo profile version;
- included datasets/layers;
- capability/export policy;
- hashes;
- signature metadata where available.

Offline mutation MUST retain an operation log suitable for later reconciliation.

Conflicts MUST NOT silently overwrite newer canonical evidence.

---

## 21. TAK / ATAK projection

StarIntel Geo SHOULD define an adapter to TAK-compatible Cursor-on-Target and compatible
data packages.

The adapter MUST preserve stable StarIntel identifiers using extension metadata where
possible.

Not all StarIntel semantics fit CoT. Therefore:

- CoT is a transport/rendering projection;
- canonical StarIntel docs remain authority;
- unsupported relations remain available through deep links or side-channel metadata;
- round-trip loss MUST be documented.

The TAK adapter SHOULD support:

- points;
- tracks;
- routes;
- areas;
- alerts;
- document/entity deep links;
- layer identity;
- provenance summary;
- freshness/validity.

---

## 22. Android and Zara

Android clients SHOULD support:

- full-screen map workspace;
- local offline packs;
- canonical entity selection;
- graph-to-map and map-to-graph handoff;
- time scrubber;
- provenance inspector;
- layer manager;
- search;
- route/area selection;
- quick capture of authorized observations;
- remote StarIntel/Zara worker-stack session.

Android share/capture flows MAY create geo-aware draft observations when explicit
location permission is available.

---

## 23. Quasar web workspace

A web implementation SHOULD expose a first-class map workspace, not a tiny embedded
widget.

Required interaction concepts:

- map viewport;
- layer tree;
- selected object panel;
- related documents;
- graph expansion;
- timeline;
- provenance;
- query/filter controls;
- deep link to canonical document;
- deep link from canonical document to map context.

Map state SHOULD be URL-addressable where practical.

---

## 24. XR / immersive rendering

XR is a presentation target over the same Geo profile.

A thin client MAY render:

- 2D floating map;
- 3D terrain/city model;
- document cards anchored to map objects;
- graph relations in world space;
- event pulses;
- tracks;
- timelines;
- street-level panorama transitions.

The headset SHOULD NOT be required to run canonical indexing, heavy graph reasoning,
or large-model inference locally.

Remote services MAY perform computation while XR renders authorized projections.

---

## 25. Gotham presentation profile

The normative semantics are style-independent. A recommended StarIntel presentation
profile named **Gotham** MAY provide a cinematic dark intelligence-console aesthetic.

Suggested characteristics:

- near-black basemap;
- restrained labels;
- architectural/building outlines;
- muted terrain;
- pale cool relationship edges;
- warm alert accents;
- pulse animation for recent events;
- temporal movement trails;
- graph bloom around selected anchors;
- optional atmospheric fog/rain in 3D;
- high contrast selection halos;
- sparse default mode;
- dense investigation mode.

Presentation MUST encode semantic distinctions.

Recommended edge grammar:

```text
solid       explicit canonical relation
dashed      named-rule inference
dotted      weak/candidate association
halo        uncertainty/accuracy envelope
pulse       recent event or alert
trail       time-ordered movement/observations
```

A cinematic visual language MUST NOT erase provenance or uncertainty.

---

## 26. Investigation mode

Clients SHOULD support an investigation mode centered around a geographic anchor.

Selecting an anchor SHOULD make it possible to inspect:

- direct documents;
- related documents;
- people/entity records visible to the principal;
- organizations;
- events;
- observations;
- media;
- sensors;
- sources;
- alerts;
- relation paths;
- temporal changes.

Counts MUST be authorization-aware.

The interface MAY visually expand related documents around the selected geometry.

---

## 27. Detective-view mode

A reduced visual mode MAY suppress decorative map information and emphasize:

- entities;
- relationship paths;
- confidence;
- time;
- movement;
- active alerts;
- provenance state.

This mode is purely a rendering transformation.

---

## 28. Street-level imagery

StarIntel Geo MAY integrate street-level panoramas or imagery sources.

Each imagery source MUST retain:

- provider/source;
- image id;
- capture time;
- location/pose;
- attribution/license;
- quality metadata.

The system MUST NOT assume that imagery rights permit arbitrary caching or redistribution.
Offline use MUST follow source-specific terms.

Street imagery MUST link back to canonical StarIntel imagery/source objects rather than
becoming an opaque map-only asset.

---

## 29. 3D and terrain

3D renderers MAY use:

- terrain meshes;
- building extrusions;
- point clouds;
- photogrammetry;
- scene models;
- camera frusta;
- coverage volumes.

3D assets MUST maintain stable geographic registration and source provenance.

Approximate building height or model geometry SHOULD be labeled as approximate when not
directly sourced.

---

## 30. Camera and sensor geometry

A sensor projection MAY include:

- point location;
- heading;
- pitch;
- FOV;
- effective range;
- coverage polygon/volume;
- operational validity period.

Visibility computations SHOULD be exposed as derived relations with a named algorithm or
rule profile.

A `visibleFrom` relation MUST NOT silently imply that an object was actually observed.

---

## 31. Radio/network geography

Network-derived geography is evidence, not certainty.

The model SHOULD support:

- reported country/region/city;
- provider/ASN context;
- optional coordinates;
- accuracy;
- source;
- retrieval time;
- confidence.

Radio observations SHOULD support:

- observation point;
- transmitter identifier ref;
- signal metrics;
- observation time;
- source/device;
- uncertainty.

Derived radio coverage MAY be rendered but MUST remain distinguishable from actual
observations.

---

## 32. Correlation

Geo MAY offer bounded correlation queries such as:

- observations within X meters and Y minutes;
- events intersecting a route;
- documents related to entities inside a region;
- sensors covering an area;
- sources reporting the same event;
- repeated observations of the same canonical entity.

Correlation output MUST retain reasons and MUST NOT silently promote candidate
association into stronger semantic identity.

---

## 33. Alerts and geofences

Authorized users MAY define geofences and alert rules.

A geofence SHOULD include:

- geometry;
- validity;
- subject/layer scope;
- event predicates;
- delivery policy;
- owner/tenant;
- capability requirements.

Alert execution MUST be idempotent and auditable.

---

## 34. Search

Geo search SHOULD support:

- place/address;
- document/entity;
- coordinate;
- bounding area;
- region;
- layer;
- event;
- source;
- temporal range.

Search results SHOULD preserve the distinction between direct and projected geography.

---

## 35. Change stream

Geo projections SHOULD consume canonical change streams rather than polling complete
datasets when durable incremental feeds exist.

Projection processing MUST be:

- idempotent;
- checkpointed;
- replayable;
- rebuildable;
- resilient to out-of-order events;
- safe under duplicate delivery.

Tombstones/retractions MUST remove or invalidate projections without erasing historical
provenance when policy permits history.

---

## 36. Spatial storage

Implementations MAY use PostGIS or another spatial engine as a projection backend.

The spatial database MUST NOT become the canonical document authority.

A full rebuild from canonical StarIntel data MUST be supported and tested.

Projection rows SHOULD retain:

- canonical document ref;
- canonical revision/event sequence;
- projection profile version;
- rule version;
- source/evidence refs;
- visibility partition.

---

## 37. Cache model

Caches MAY exist at server, client, tile, and offline-pack layers.

Cache keys MUST include enough context to avoid cross-tenant or cross-capability leakage.

Sensitive map results MUST NOT be cached in globally shared public caches unless the data
is itself explicitly public.

---

## 38. Conflict handling

Conflicting geometry claims MUST be representable simultaneously.

Suggested states:

- asserted;
- corroborated;
- contested;
- superseded;
- stale;
- retracted;
- approximate.

A conflict-resolution policy MAY choose a preferred projection for display but MUST make
competing claims inspectable when authorized.

---

## 39. Performance targets

Implementations SHOULD define explicit SLOs for:

- first map paint;
- tile latency;
- bbox query;
- entity context query;
- graph expansion;
- time scrub;
- offline search;
- projection replay.

Heavy graph expansion SHOULD be asynchronous at the protocol level only when required;
the client MUST receive a stable job/ref rather than hanging an unbounded request.

---

## 40. Conformance suites

A conforming implementation SHOULD pass at least the following suites.

### 40.1 Projection

1. direct geometry renders as direct;
2. explicit relation renders as anchored;
3. named rule result renders as derived;
4. derived coordinates are never written back as direct geometry;
5. projection rebuild is deterministic for the same canonical snapshot.

### 40.2 Provenance

6. every visible feature can resolve its canonical ref;
7. imported layer features retain source attribution;
8. derived projection returns rule id/version and input evidence.

### 40.3 Temporal

9. as-of query excludes future-valid relationships;
10. historical geometry remains queryable when permitted;
11. discovery time and event-valid time remain distinct.

### 40.4 Authorization

12. hidden document does not leak through map counts;
13. hidden relation does not produce a visible derived edge;
14. offline export excludes fields/layers outside export authority;
15. cache partitioning prevents cross-tenant leakage.

### 40.5 Uncertainty

16. city-level claim does not render as exact address;
17. accuracy envelope survives serialization;
18. competing location claims remain distinguishable.

### 40.6 Reasoning

19. max-depth is enforced;
20. resource exhaustion returns typed partial/resource-limit status;
21. proximity alone does not create identity;
22. derived relations are retractable/recomputable.

### 40.7 Rendering contract

23. stable canonical selection survives map-to-document transition;
24. graph-to-map handoff resolves a geographic anchor;
25. layer metadata declares provenance and capability requirements.

### 40.8 Offline

26. pack integrity hashes verify;
27. stale pack is visibly marked;
28. offline mutation log reconciles without blind overwrite.

### 40.9 TAK

29. supported CoT object round-trips stable StarIntel refs;
30. unsupported semantic data remains available through linked StarIntel context.

### 40.10 XR

31. XR client can select a rendered entity and resolve canonical document context;
32. XR rendering never requires direct database authority.

---

## 41. RED-first acceptance fixtures

Implementations SHOULD begin with failing fixtures for:

- a non-geo person explicitly linked to a geo organization;
- a non-geo report linked two hops from a building;
- two competing building coordinates;
- a time-expired relation;
- a private related document hidden from a map viewer;
- an approximate city-only network location;
- a camera FOV relation;
- a moving track with temporal playback;
- a derived proximity candidate that does not become identity;
- an offline pack rebuild;
- a TAK projection;
- an XR selection/deep-link event.

---

## 42. Versioning

Geo profile versions are independent from the inherited StarIntel document
`schema_version`.

Breaking Geo semantic changes require a major profile version.

Additive fields or optional rendering capabilities may use a minor profile version.

Rule packs and layer styles MUST be independently versioned.

A projection SHOULD therefore identify at least:

```text
parentSpecRelease
geoProfileVersion
rulePackVersion
layerVersion
styleVersion
```

---

## 43. Implementation boundaries

The following are explicitly non-authoritative projections/adapters:

- PostGIS projection tables;
- vector tiles;
- PMTiles;
- map-client local indexes;
- CoT streams;
- XR scene graphs;
- style layers;
- street-view presentation state.

The following remain canonical:

- StarIntel documents;
- evidence;
- provenance;
- explicit relations/assertions;
- authorization/capability policy;
- canonical temporal facts.

---

## 44. Initial implementation decomposition

### Phase A — semantic contract

- profile manifest;
- GeoProjection schema;
- geometry evidence;
- relation path representation;
- temporal fields;
- uncertainty model;
- layer contract;
- conformance fixtures.

### Phase B — projection service

- durable change consumer;
- PostGIS projection;
- bbox/nearest/intersection;
- entity-to-anchor lookup;
- related-document expansion;
- deterministic rebuild.

### Phase C — map publication

- MVT;
- PMTiles/offline pack;
- layer metadata;
- style contract;
- provenance hydration.

### Phase D — Quasar

- full-screen map;
- related-document panel;
- graph handoff;
- timeline;
- layer manager;
- Gotham profile;
- screenshots.

### Phase E — Android / TAK

- Android map workspace;
- offline packs;
- CoT bridge;
- capture/share integration;
- deep links.

### Phase F — XR

- Quest/OpenXR thin client;
- floating map;
- 3D anchor selection;
- relation bloom;
- timeline;
- server-backed reasoning.

---

## 45. Non-goals

This profile does not define:

- a replacement document database;
- an arbitrary Prolog execution API;
- an identity-merging engine;
- a universal geocoder;
- a proprietary map-provider dependency;
- permission bypasses;
- silent conversion of inferred associations into asserted facts.

---

## 46. Final invariant

The defining StarIntel Geo invariant is:

> **Geography is a lens over the knowledge graph, not a shortcut around the knowledge
> graph.**

Every point, line, polygon, track, card, relationship edge, alert, and immersive object
must remain traceable to the canonical StarIntel world model, with the difference between
fact, explicit relation, and inference preserved all the way to the pixels.
