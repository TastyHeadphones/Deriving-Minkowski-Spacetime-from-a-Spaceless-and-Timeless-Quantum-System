import EmergentSpacetime.EmergentSpace
import Mathlib.Logic.Equiv.Defs

namespace EmergentSpacetime

def pathThree : CorrelationGraph (Fin 3) where
  adjacent a b := (a.val + 1 = b.val) ∨ (b.val + 1 = a.val)
  symmetric := by
    intro a b h
    exact h.symm
  irreflexive := by
    intro a h
    rcases h with h | h <;> exact Nat.ne_of_gt (Nat.lt_succ_self a.val) h

def triangleThree : CorrelationGraph (Fin 3) where
  adjacent a b := a ≠ b
  symmetric := by
    intro a b h
    exact Ne.symm h
  irreflexive := fun _ h => h rfl

theorem path_and_triangle_not_isomorphic :
    ¬ ∃ relabel : Fin 3 ≃ Fin 3,
      ∀ a b, pathThree.adjacent a b ↔ triangleThree.adjacent (relabel a) (relabel b) := by
  rintro ⟨relabel, preserves⟩
  have h : pathThree.adjacent 0 2 :=
    (preserves 0 2).mpr (fun equal => (by decide : (0 : Fin 3) ≠ 2) (relabel.injective equal))
  change (0 + 1 = 2 : Prop) ∨ (2 + 1 = 0 : Prop) at h
  exact (by decide : ¬ ((0 + 1 = 2 : Prop) ∨ (2 + 1 = 0 : Prop))) h

end EmergentSpacetime
