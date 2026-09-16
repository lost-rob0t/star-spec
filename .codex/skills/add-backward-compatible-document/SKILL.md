---
name: add-backward-compatible-document
description: Add a document type to star-spec without breaking existing producers or consumers, including the StarLang source, generated projections, compatibility tests, and patch-coordinate release bump. Use for additive document or dtype requests; do not use to disguise required-field, discriminator, identity, or semantic changes as compatible.
---

# Add a backward-compatible document

Add the contract in StarLang, refresh every derived representation, and leave
machine-checkable evidence that existing documents remain valid.

## Establish the release

Read `AGENTS.md`, the current release manifest, the StarLang definitions, and the
generation/validation workflow. Work on a branch named exactly for the target
four-number release coordinate.

For an additive, backward-compatible document, increment the rightmost `PATCH`
coordinate in `MAJOR.MINOR.COMPAT.PATCH`. Do not reuse a published coordinate.
If the change alters an existing discriminator, removes or renames a field,
makes a field required, narrows accepted input, changes identity or tenancy
meaning, or makes an old valid document invalid, stop treating it as a patch.
Move it to a minor or major release and add a migration.

Do not collapse independent version axes. For the current line,
`release_version` is `0.9.1.2`, the inherited base `schema_version` is `0.9.0`,
and the actor-configuration document's profile/type version is `0.9.2`.
Changing a document's profile/type version does not rename the repository
release.

## Add the document contract

1. Find the nearest analogous document and reuse shared vocabulary rather than
   cloning common fields under new names.
2. Define the new document in the StarLang source under `spec/`. Give it a unique,
   stable type/discriminator and state its required fields, optional fields,
   invariants, tenancy behavior, and extension points.
3. Preserve forward tolerance: consumers must be able to retain unknown fields,
   and existing document meanings must not change because the new type exists.
4. Run the repository's generator/update workflow to refresh JSON Schema,
   JSON-LD, manifests, examples, and supported language bindings under
   `generated/<release_version>/`. Fix the source or generator when outputs
   disagree; do not patch generated drift by hand. Preserve `canonical/0.9.0/`
   as the inherited base unless a higher-order release explicitly replaces it.
5. Update every authoritative version declaration to the same target
   coordinate. Keep older versioned artifacts available unless repository
   policy explicitly replaces them with a deterministic compatibility bundle.

## Prove compatibility

Add at least one minimal valid fixture and one representative full fixture for
the new document. Add invalid fixtures for its meaningful invariants.

Run the repository validation workflow and verify all of these properties:

- every fixture accepted by the prior release is still accepted;
- its discriminator resolves to the same pre-existing document definition;
- required fields and accepted values for existing types are unchanged;
- the new fixtures validate through the generated projections, not only the
  StarLang compiler;
- generated files are reproducible from a clean invocation; and
- manifests, hashes, counts, and release metadata match generated content.

If any old valid fixture fails, reclassify the change as minor or major. Do not
weaken the fixture or delete compatibility evidence to make a patch pass.

## Hand off

Summarize the new type, compatibility argument, target coordinate, generated
artifacts, and exact validation commands. Commit the coherent change when
authorized. Merging, tagging, publishing, and changing downstream repositories
remain separate actions that require explicit authorization.
