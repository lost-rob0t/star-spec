# Version history and compatibility

| Layer | Version | Status |
| --- | --- | --- |
| Base document schema | `0.9.0` | Imported exactly from the commit pinned by `starintel-server` |
| Additive expansion profile | `0.9.1` | Imported with the canonical manifest and expansion registry |
| Repository release | `0.9.1.2` | StarLang source plus generated compatibility projection |
| `actor-config` profile | `0.9.2` | New additive document type within release `0.9.1.2` |

The canonical repository history begins with the `0.9.0` schema. Its `0.9.1`
profile is represented as an expansion registry rather than a replacement base
schema. Both are retained under `canonical/0.9.0/` because that is the layout
and commit referenced by the live server lock.

Patch compatibility means existing dtype discriminator values, their complete
`data` schemas, top-level required fields, and the base `schema_version` remain
unchanged. A new dtype may be added. Existing fields may not be removed, made
required, or narrowed on a four-part patch release.

`actor-config` documents use `credential_ref`; access tokens and client secrets
must remain in the server's credential store. `actor_group` is authorization
metadata only. Server policy calculates quotas per key and actor at runtime.
