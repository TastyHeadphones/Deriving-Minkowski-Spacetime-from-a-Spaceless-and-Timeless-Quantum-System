import EmergentSpacetime.Counterexamples

namespace EmergentSpacetime

/-- Even at fixed label count, the common token-preparation rule supports
nonisomorphic reconstructed relations. This is a scoped finite no-go result. -/
theorem preparation_allows_incompatible_relations :
    ∃ first second : CorrelationGraph (Fin 3),
      (∀ a b, a ≠ b →
        ((∃ t, HasToken first a t ∧ HasToken first b t) ↔ first.adjacent a b) ∧
        ((∃ t, HasToken second a t ∧ HasToken second b t) ↔ second.adjacent a b)) ∧
      ¬ ∃ relabel : Fin 3 ≃ Fin 3,
        ∀ a b, first.adjacent a b ↔ second.adjacent (relabel a) (relabel b) := by
  refine ⟨pathThree, triangleThree, ?_, path_and_triangle_not_isomorphic⟩
  intro a b distinct
  exact ⟨shared_token_iff_adjacent pathThree distinct,
    shared_token_iff_adjacent triangleThree distinct⟩

end EmergentSpacetime
