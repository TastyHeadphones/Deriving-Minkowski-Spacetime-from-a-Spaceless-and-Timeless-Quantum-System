import Mathlib.Logic.Relation

namespace EmergentSpacetime

/-- An abstract relation on labels, with no embedding or propagation law. -/
structure CorrelationGraph (Label : Type*) where
  adjacent : Label → Label → Prop
  symmetric : Symmetric adjacent
  irreflexive : Irreflexive adjacent

def CorrelationGraph.IsComplete {Label : Type*} (graph : CorrelationGraph Label) : Prop :=
  ∀ a b, a ≠ b → graph.adjacent a b

end EmergentSpacetime
