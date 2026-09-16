# Star Spec agent map

`star-spec` owns the protocol contract. StarLang is the authored source of truth;
JSON Schema, JSON-LD contexts, manifests, examples, and language bindings are
projections of that source. Do not make a generated projection the only place a
contract change exists.

## Release policy

- Work on a branch named exactly for the target release coordinate, for example
  `0.9.1.2`.
- This repository uses the four-number coordinate
  `MAJOR.MINOR.COMPAT.PATCH`. A backward-compatible document addition increments
  `PATCH`, the rightmost number. Reset lower-order numbers when moving a higher
  release coordinate.
- Keep the version axes distinct: `release_version` is `0.9.1.2`; the inherited
  base `schema_version` remains `0.9.0`; and the actor-configuration document's
  profile/type version is `0.9.2`. The actor-config version is not the repository
  release version.
- Use a minor release for a compatibility break that has a bounded migration.
  Use a major release when the protocol meaning, identity model, or wire contract
  is replaced. Never hide a breaking change in a patch release.
- A release is not complete until every authoritative version declaration,
  generated artifact, compatibility fixture, and release note agrees on the
  target coordinate.

## Agent ownership map

| Agent lane | Owns | Must hand off |
| --- | --- | --- |
| StarLang contract author | Canonical document/type definitions and invariants | Generated projections and compatibility evidence |
| Projection maintainer | JSON Schema, JSON-LD, manifests, examples, and bindings generated from StarLang | Generator inputs when a projection cannot express the contract |
| Compatibility reviewer | Old-fixture validation, discriminator stability, required-field and constraint diffs | Any detected break to release/migration owner |
| Migration owner | Explicit transforms, deprecation windows, and consumer notes for minor/major changes | A reversible migration test and upgrade notes |
| Release owner | Version branch, coordinated version bump, release notes, and green checks | Merge or publication only when explicitly authorized |

An agent may cover multiple lanes, but must keep the handoffs visible in the
change description. Parallel agents own only the files assigned to them; do not
discard or rewrite another agent's uncommitted changes.

## Working rules

1. Read the closest instructions and current release metadata before editing.
2. Classify compatibility before choosing a version. When uncertain, treat the
   change as breaking until a compatibility test proves otherwise.
3. Edit the StarLang source under `spec/` first, then run the repository
   generator or update workflow. Treat `canonical/0.9.0/` as the inherited base
   and `generated/0.9.1.2/` as release projections.
   Do not hand-edit generated files unless the generator is being repaired in
   the same change.
4. Preserve unknown fields and existing discriminator meanings. Never make an
   existing optional field required or narrow an accepted value in a patch.
5. Validate existing fixtures against the new release and add a fixture for the
   new document type. A successful new example alone is not compatibility proof.
6. Do not merge, publish, tag, or change external repositories unless the user
   explicitly authorizes that action.

For additive document types, load and follow
`.codex/skills/add-backward-compatible-document/SKILL.md`.
