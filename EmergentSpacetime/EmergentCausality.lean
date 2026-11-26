import Mathlib.Data.Real.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma

open scoped BigOperators

namespace EmergentSpacetime

/-- Applying a column-normalized classical channel to one register preserves
the other register's marginal. This also applies to diagonal quantum laws. -/
theorem stochastic_local_channel_preserves_marginal
    {Input Output Remote : Type*} [Fintype Input] [Fintype Output]
    (joint : Input → Remote → ℝ) (channel : Input → Output → ℝ)
    (normalized : ∀ input, ∑ output, channel input output = 1) (remote : Remote) :
    (∑ output, ∑ input, joint input remote * channel input output) =
      ∑ input, joint input remote := by
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro input _
  rw [← Finset.mul_sum, normalized, mul_one]

end EmergentSpacetime
