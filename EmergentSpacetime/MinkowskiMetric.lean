import Mathlib.Algebra.Order.Field.Basic

namespace EmergentSpacetime

/-- A nonzero scale does not identify a quadratic form from its zero set. -/
theorem same_null_set_under_scaling {Vector Scalar : Type*} [Field Scalar]
    (q : Vector → Scalar) {scale : Scalar} (nonzero : scale ≠ 0) :
    {v | scale * q v = 0} = {v | q v = 0} := by
  ext v
  change (scale * q v = 0) ↔ q v = 0
  exact ⟨fun zero => (mul_eq_zero.mp zero).resolve_left nonzero, fun zero => by simp [zero]⟩

theorem scaling_changes_nonzero_value {Vector Scalar : Type*} [Field Scalar]
    (q : Vector → Scalar) {scale : Scalar} (distinct : scale ≠ 1)
    {v : Vector} (nonzero : q v ≠ 0) : scale * q v ≠ q v := by
  intro equal
  apply distinct
  exact mul_right_cancel₀ nonzero (equal.trans (one_mul _).symm)

end EmergentSpacetime
