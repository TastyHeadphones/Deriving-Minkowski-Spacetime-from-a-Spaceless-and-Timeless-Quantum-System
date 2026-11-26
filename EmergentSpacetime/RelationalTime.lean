import Mathlib.Logic.Function.Iterate
import Mathlib.Logic.Equiv.Defs

namespace EmergentSpacetime

/-- The shift moves the clock label and applies the system map together. -/
def shiftedHistory {Clock State : Type*} (tick : Clock ≃ Clock)
    (systemMap : State → State) (history : Clock → State) : Clock → State :=
  fun label => systemMap (history (tick.symm label))

theorem stationary_iff_conditional_step {Clock State : Type*}
    (tick : Clock ≃ Clock) (systemMap : State → State) (history : Clock → State) :
    shiftedHistory tick systemMap history = history ↔
      ∀ label, history (tick label) = systemMap (history label) := by
  constructor
  · intro stationary label
    have atNext := congrFun stationary (tick label)
    simpa [shiftedHistory] using atNext.symm
  · intro step
    funext label
    simpa [shiftedHistory] using (step (tick.symm label)).symm

theorem conditional_step_iterates {Clock State : Type*}
    (tick : Clock ≃ Clock) (systemMap : State → State) (history : Clock → State)
    (step : ∀ label, history (tick label) = systemMap (history label)) :
    ∀ (n : ℕ) label, history (tick^[n] label) = systemMap^[n] (history label) := by
  intro n
  induction n with
  | zero => intro label; rfl
  | succ n ih =>
    intro label
    rw [Function.iterate_succ_apply', Function.iterate_succ_apply', step, ih]

end EmergentSpacetime
