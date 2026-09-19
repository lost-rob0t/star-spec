:- module(starintel_geo_v1, [
    geo_participation/3,
    projection_kind/2,
    direct_geo/1,
    anchored_geo/3,
    derived_geo/4,
    projection_explainable/1
]).

/*
  Reference semantics only.

  Implementations MUST bind these predicates to canonical, authorized StarIntel facts.
  They MUST NOT expose arbitrary Prolog execution to clients.
*/

direct_geo(Doc) :-
    document_geometry(Doc, _Geometry),
    geometry_evidence(Doc, _Evidence).

anchored_geo(Doc, Anchor, Relation) :-
    relation(RelationId, Doc, Relation, Anchor),
    relation_status(RelationId, active),
    document_geometry(Anchor, _).

derived_geo(Doc, Anchor, Path, RuleProfile) :-
    named_rule_profile(RuleProfile),
    bounded_geo_path(Doc, Anchor, Path, RuleProfile),
    document_geometry(Anchor, _),
    authorized_projection_path(Doc, Anchor, Path).

geo_participation(Doc, direct, Doc) :-
    direct_geo(Doc).

geo_participation(Doc, anchored, Anchor) :-
    \+ direct_geo(Doc),
    anchored_geo(Doc, Anchor, _).

geo_participation(Doc, derived, Anchor) :-
    \+ direct_geo(Doc),
    \+ anchored_geo(Doc, _, _),
    derived_geo(Doc, Anchor, _, _).

projection_kind(Projection, direct) :-
    projection_source(Projection, direct_geometry).

projection_kind(Projection, anchored) :-
    projection_source(Projection, explicit_relation).

projection_kind(Projection, derived) :-
    projection_source(Projection, expert_rule).

projection_explainable(Projection) :-
    projection_document(Projection, Doc),
    projection_anchor(Projection, Anchor),
    projection_kind(Projection, Kind),
    projection_path(Projection, Path),
    projection_evidence_refs(Projection, Evidence),
    projection_rule_profile(Projection, RuleProfile),
    nonvar(Doc),
    nonvar(Anchor),
    nonvar(Kind),
    is_list(Path),
    is_list(Evidence),
    nonvar(RuleProfile).

/*
  Mandatory implementation constraints:

  - bounded_geo_path/4 MUST enforce max hops, max solutions, wall clock limits,
    tenant/dataset scope, capability scope, and temporal validity.
  - weak proximity alone MUST NOT assert identity or ownership.
  - inferred relationships MUST retain the rule id/version and source evidence.
  - projection facts are rebuildable and MUST NOT mutate canonical evidence.
*/
