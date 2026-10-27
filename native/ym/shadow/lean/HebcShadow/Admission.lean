/-!
# The 3×4 admission rule (PRODUCTION-ADMISSION.md), conditional form

If every admitted block uses at most `col` bytes, everything else uses at most `reserve`,
and the admission rule is enforced, then total resident memory stays within `budget`.
Natural numbers only.
-/
namespace HebcShadow

inductive Ev where
  | admit
  | release

/-- One step of the rule: admit only if `(active + 1) * col + reserve ≤ budget`. -/
def step (col reserve budget : Nat) (a : Nat) : Ev → Nat
  | .admit => if (a + 1) * col + reserve ≤ budget then a + 1 else a
  | .release => a - 1

/-- Active blocks after a sequence of events, starting from `a`. -/
def run (col reserve budget : Nat) : Nat → List Ev → Nat
  | a, [] => a
  | a, e :: es => run col reserve budget (step col reserve budget a e) es

theorem step_inv (col reserve budget a : Nat) (e : Ev)
    (h : a * col + reserve ≤ budget) :
    step col reserve budget a e * col + reserve ≤ budget := by
  cases e with
  | admit =>
    simp only [step]
    split
    · assumption
    · exact h
  | release =>
    simp only [step]
    have : (a - 1) * col ≤ a * col := Nat.mul_le_mul_right col (Nat.sub_le a 1)
    omega

/-- Forward invariance: for ANY sequence of arrivals and completions. -/
theorem run_inv (col reserve budget : Nat) :
    ∀ (es : List Ev) (a : Nat), a * col + reserve ≤ budget →
      run col reserve budget a es * col + reserve ≤ budget
  | [], _, h => h
  | e :: es, a, h => run_inv col reserve budget es _ (step_inv col reserve budget a e h)

theorem sum_le_length_mul (col : Nat) :
    ∀ us : List Nat, (∀ u ∈ us, u ≤ col) → us.sum ≤ us.length * col
  | [], _ => by simp
  | u :: us, h => by
    have hu : u ≤ col := h u List.mem_cons_self
    have ih := sum_le_length_mul col us (fun v hv => h v (List.mem_cons_of_mem u hv))
    simp only [List.sum_cons, List.length_cons, Nat.succ_mul]
    omega

/-- The admission theorem. `us` are the actual usages of the resident blocks (one per
active block), `other` the rest of the process. Both bounds are hypotheses: the pilot
measures them and the runtime gate tests them cell by cell. -/
theorem admission (col reserve budget other : Nat) (es : List Ev) (us : List Nat)
    (hstart : reserve ≤ budget)
    (hlen : us.length = run col reserve budget 0 es)
    (hblock : ∀ u ∈ us, u ≤ col)
    (hother : other ≤ reserve) :
    us.sum + other ≤ budget := by
  have hinv := run_inv col reserve budget es 0 (by simpa using hstart)
  have hs := sum_le_length_mul col us hblock
  rw [hlen] at hs
  omega

/-- The frozen budget: 12 GiB. -/
def budget12GiB : Nat := 12 * 2 ^ 30

theorem admission_12GiB (col reserve other : Nat) (es : List Ev) (us : List Nat)
    (hstart : reserve ≤ budget12GiB)
    (hlen : us.length = run col reserve budget12GiB 0 es)
    (hblock : ∀ u ∈ us, u ≤ col) (hother : other ≤ reserve) :
    us.sum + other ≤ 12 * 2 ^ 30 :=
  admission col reserve budget12GiB other es us hstart hlen hblock hother

end HebcShadow
