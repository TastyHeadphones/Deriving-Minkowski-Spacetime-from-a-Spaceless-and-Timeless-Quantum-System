import EmergentSpacetime.Foundations

namespace EmergentSpacetime

/-- A directed endpoint token is prepared only when that ordered pair is an edge.
The two directions of each undirected edge are distinct fair-bit sources. -/
def HasToken {Label : Type*} (graph : CorrelationGraph Label)
    (label : Label) (token : Label × Label) : Prop :=
  graph.adjacent token.1 token.2 ∧ (token.1 = label ∨ token.2 = label)

theorem shared_token_iff_adjacent {Label : Type*} (graph : CorrelationGraph Label)
    {a b : Label} (distinct : a ≠ b) :
    (∃ token, HasToken graph a token ∧ HasToken graph b token) ↔ graph.adjacent a b := by
  constructor
  · rintro ⟨⟨left, right⟩, ⟨edge, atA⟩, ⟨_, atB⟩⟩
    change graph.adjacent left right at edge
    change left = a ∨ right = a at atA
    change left = b ∨ right = b at atB
    rcases atA with h | h <;> rcases atB with h' | h'
    · exact False.elim (distinct (h.symm.trans h'))
    · simpa [h, h'] using edge
    · exact graph.symmetric (by simpa [h, h'] using edge)
    · exact False.elim (distinct (h.symm.trans h'))
  · intro edge
    exact ⟨(a, b), ⟨edge, Or.inl rfl⟩, ⟨edge, Or.inr rfl⟩⟩

end EmergentSpacetime
