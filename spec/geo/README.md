# StarIntel Geo Profile

Status: **Draft / implementation-authorizing**
Profile ID: `starintel.geo`
Profile version: `1.0.0-draft.1`
Parent StarIntel spec release: `0.9.1.2`

StarIntel Geo is the geographic projection profile for the StarIntel knowledge graph.

It does **not** create a second source of truth. Canonical StarIntel documents, assertions,
relations, evidence, provenance, capability policy, and temporal semantics remain authoritative.
Geo implementations derive rebuildable spatial projections from those canonical records.

## Normative documents

- `starintel-geo-v1.md` — normative architecture and behavior.
- `profile.json` — machine-readable profile metadata and capability declarations.
- `prolog/geo-v1.pl` — reference logical semantics for projection and relation classes.
- `fixtures/geo-projection.jsonld` — canonical example fixture.

## Core invariant

A document can participate in Geo in three distinct ways:

1. **direct geometry** — geometry is asserted on or directly evidenced for the document;
2. **anchored geometry** — the document is projected through an explicit relation to a
   geometry-bearing document;
3. **derived spatial relation** — the document is associated through a bounded, explainable
   reasoning path.

Clients MUST distinguish these cases visually and semantically. A derived or anchored
projection MUST NOT be serialized as direct location evidence.

## Rendering targets

The same semantic profile is intended to support:

- StarIntel web/Quasar map workspaces;
- Android/Zara map clients;
- ATAK/TAK Cursor-on-Target and compatible overlays;
- desktop command-center views;
- Quest/OpenXR experimental immersive clients;
- offline regional packs and disconnected operation.

The rendering layer is presentation. The graph and provenance model are authority.
