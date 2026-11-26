import Mathlib.Data.Nat.Find

namespace EmergentSpacetime

/-- Interface supplied by lengths of finite walks within one connected component. -/
structure PathCosts (Label : Type*) where
  available : Label → Label → ℕ → Prop
  reachable : ∀ a b, ∃ n, available a b n
  zero : ∀ a b, available a b 0 ↔ a = b
  reverse : ∀ {a b n}, available a b n → available b a n
  append : ∀ {a b c n m}, available a b n → available b c m → available a c (n + m)

noncomputable def PathCosts.distance {Label : Type*} (paths : PathCosts Label) (a b : Label) : ℕ := by
  classical
  exact Nat.find (paths.reachable a b)

theorem path_distance_is_metric {Label : Type*} (paths : PathCosts Label) :
    (∀ a b, 0 ≤ paths.distance a b) ∧
    (∀ a b, paths.distance a b = 0 ↔ a = b) ∧
    (∀ a b, paths.distance a b = paths.distance b a) ∧
    (∀ a b c, paths.distance a c ≤ paths.distance a b + paths.distance b c) := by
  classical
  have shortest (a b : Label) : paths.available a b (paths.distance a b) :=
    Nat.find_spec (paths.reachable a b)
  have lower (a b : Label) (n : ℕ) (witness : paths.available a b n) :
      paths.distance a b ≤ n := Nat.find_min' (paths.reachable a b) witness
  refine ⟨fun a b => Nat.zero_le _, ?_, ?_, ?_⟩
  · intro a b
    constructor
    · intro zero
      apply (paths.zero a b).mp
      simpa only [zero] using shortest a b
    · intro equal
      exact Nat.eq_zero_of_le_zero (lower a b 0 ((paths.zero a b).mpr equal))
  · intro a b
    exact le_antisymm (lower a b _ (paths.reverse (shortest b a)))
      (lower b a _ (paths.reverse (shortest a b)))
  · intro a b c
    exact lower a c _ (paths.append (shortest a b) (shortest b c))

end EmergentSpacetime
