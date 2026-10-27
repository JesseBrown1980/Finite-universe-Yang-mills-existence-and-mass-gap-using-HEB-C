/-!
# Column-partition conservation (countcols / countmerge)

A count split into column cells `[b₀,b₁), [b₁,b₂), …, [b_{k-1}, b_k)` with `b₀ = a` and
nondecreasing boundaries adds up to the count over `[a, b_k)`, for any per-column
contribution `f`. Natural numbers only.
-/
namespace HebcShadow

/-- Σ_{j ∈ [a, a + len)} f j -/
def sumLen (f : Nat → Nat) (a : Nat) : Nat → Nat
  | 0 => 0
  | k + 1 => f a + sumLen f (a + 1) k

/-- Σ_{j ∈ [a, b)} f j (zero when b ≤ a) -/
def sumR (f : Nat → Nat) (a b : Nat) : Nat := sumLen f a (b - a)

theorem sumLen_add (f : Nat → Nat) : ∀ (k a l : Nat), sumLen f a (k + l) = sumLen f a k + sumLen f (a + k) l
  | 0, a, l => by simp [sumLen]
  | k + 1, a, l => by
    have ih := sumLen_add f k (a + 1) l
    rw [show k + 1 + l = (k + l) + 1 by omega]
    simp only [sumLen, ih]
    rw [show a + 1 + k = a + (k + 1) by omega]
    omega

theorem sumR_split (f : Nat → Nat) (a b c : Nat) (hab : a ≤ b) (hbc : b ≤ c) :
    sumR f a c = sumR f a b + sumR f b c := by
  unfold sumR
  have h := sumLen_add f (b - a) a (c - b)
  rw [show b - a + (c - b) = c - a by omega, show a + (b - a) = b by omega] at h
  exact h

/-- The boundaries after `a` never decrease. -/
def Mono : Nat → List Nat → Prop
  | _, [] => True
  | a, b :: rest => a ≤ b ∧ Mono b rest

/-- Last boundary (or `a` itself when there are no cells). -/
def lastB : Nat → List Nat → Nat
  | a, [] => a
  | _, b :: rest => lastB b rest

/-- Sum of the cells' counts. -/
def cellsSum (f : Nat → Nat) : Nat → List Nat → Nat
  | _, [] => 0
  | a, b :: rest => sumR f a b + cellsSum f b rest

theorem partition (f : Nat → Nat) : ∀ (a : Nat) (bs : List Nat), Mono a bs →
    cellsSum f a bs = sumR f a (lastB a bs)
  | a, [], _ => by simp [cellsSum, lastB, sumR, sumLen]
  | a, b :: rest, h => by
    have ih := partition f b rest h.2
    have hle : b ≤ lastB b rest := mono_le b rest h.2
    simp only [cellsSum, lastB, ih]
    exact (sumR_split f a b (lastB b rest) h.1 hle).symm
where
  mono_le : ∀ (a : Nat) (bs : List Nat), Mono a bs → a ≤ lastB a bs
    | _, [], _ => Nat.le_refl _
    | a, b :: rest, h => Nat.le_trans h.1 (mono_le b rest h.2)

/-- What countmerge certifies: cells starting at column 0 and ending at the core size,
merged, give the whole count. -/
theorem countmerge_conserves (f : Nat → Nat) (bs : List Nat) (core : Nat)
    (hmono : Mono 0 bs) (hend : lastB 0 bs = core) :
    cellsSum f 0 bs = sumR f 0 core := by
  rw [← hend]; exact partition f 0 bs hmono

end HebcShadow
