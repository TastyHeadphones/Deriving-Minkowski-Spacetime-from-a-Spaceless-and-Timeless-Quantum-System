import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset

open scoped BigOperators

namespace EmergentSpacetime

/-- Diagonal entries of a density operator in a chosen finite basis. -/
structure DiagonalState (Basis : Type*) [Fintype Basis] where
  weight : Basis → ℝ
  nonnegative : ∀ x, 0 ≤ weight x
  normalized : ∑ x, weight x = 1

/-- The real quadratic form of the diagonal density operator. -/
def DiagonalState.quadratic {Basis : Type*} [Fintype Basis]
    (state : DiagonalState Basis) (vector : Basis → ℂ) : ℝ :=
  ∑ x, state.weight x * Complex.normSq (vector x)

theorem diagonal_quadratic_nonnegative {Basis : Type*} [Fintype Basis]
    (state : DiagonalState Basis) (vector : Basis → ℂ) :
    0 ≤ state.quadratic vector := by
  unfold DiagonalState.quadratic
  exact Finset.sum_nonneg fun x _ =>
    mul_nonneg (state.nonnegative x) (Complex.normSq_nonneg _)

end EmergentSpacetime
