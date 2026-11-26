import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring

namespace EmergentSpacetime

/-- Conditional consistency check using an already selected signature and boost.
Coordinates are expressed in units for which the cone slope is one. -/
theorem boost_preserves_selected_interval (gamma beta t x y z : ℝ)
    (normalized : gamma ^ 2 * (1 - beta ^ 2) = 1) :
    (gamma * (t - beta * x)) ^ 2 - (gamma * (x - beta * t)) ^ 2 - y ^ 2 - z ^ 2 =
      t ^ 2 - x ^ 2 - y ^ 2 - z ^ 2 := by
  calc
    _ = (gamma ^ 2 * (1 - beta ^ 2)) * (t ^ 2 - x ^ 2) - y ^ 2 - z ^ 2 := by ring
    _ = _ := by rw [normalized, one_mul]

end EmergentSpacetime
