/-!
# From the frozen counts to the gap (STAGE-B-SPEC.md, certificate arithmetic)

Eigenvalues `E 0 ≤ E 1 ≤ …` (0-indexed, integer milli-J_E). `N t` counts those below `t`.
If `N t1 ≥ 8` and `N tF ≤ 8`, then `E 7 < t1` and `E 8 ≥ tF`: in the spec's 1-indexed words,
E₈ < t1 and E₉ ≥ t_F, so E₉ − E₈ > t_F − t1 = 19,366,578 milli-J_E at r = 9.
Integers only.
-/
namespace HebcShadow

/-- Number of indices `i < n` with `E i < t`. -/
def countBelow (E : Nat → Int) (t : Int) : Nat → Nat
  | 0 => 0
  | n + 1 => countBelow E t n + (if E n < t then 1 else 0)

def Sorted (E : Nat → Int) : Prop := ∀ i j, i ≤ j → E i ≤ E j

/-- If E k ≥ t, nothing at or after k is below t (sorted). -/
theorem countBelow_le_of_ge (E : Nat → Int) (t : Int) (hs : Sorted E) (k : Nat) (hk : t ≤ E k) :
    ∀ n, countBelow E t n ≤ k
  | 0 => Nat.zero_le _
  | n + 1 => by
    simp only [countBelow]
    by_cases hn : n < k
    · have := countBelow_le_of_ge E t hs k hk n
      have hcount : countBelow E t n ≤ n := countBelow_le_n n
      split <;> omega
    · have hge : t ≤ E n := Int.le_trans hk (hs k n (by omega))
      have : ¬ E n < t := Int.not_lt.mpr hge
      simp only [this, if_false, Nat.add_zero]
      exact countBelow_le_of_ge E t hs k hk n
where
  countBelow_le_n : ∀ n, countBelow E t n ≤ n
    | 0 => Nat.le_refl _
    | n + 1 => by simp only [countBelow]; have := countBelow_le_n n; split <;> omega

/-- If E k < t (sorted), all of 0..k are below t, so the count over n > k is at least k+1. -/
theorem countBelow_ge_of_lt (E : Nat → Int) (t : Int) (hs : Sorted E) (k : Nat) (hk : E k < t) :
    ∀ n, k < n → k + 1 ≤ countBelow E t n
  | 0, h => absurd h (Nat.not_lt_zero _)
  | n + 1, h => by
    simp only [countBelow]
    have hlt : E n < t ∨ ¬ E n < t := Classical.em _
    by_cases hn : k < n
    · have := countBelow_ge_of_lt E t hs k hk n hn
      split <;> omega
    · have hkn : k = n := by omega
      subst hkn
      simp only [hk, if_true]
      have : k ≤ countBelow E t k := all_below k (fun i hi => Int.lt_of_le_of_lt (hs i k (by omega)) hk)
      omega
where
  all_below : ∀ m, (∀ i, i < m → E i < t) → m ≤ countBelow E t m
    | 0, _ => Nat.le_refl _
    | m + 1, h => by
      simp only [countBelow, h m (by omega), if_true]
      have := all_below m (fun i hi => h i (by omega))
      omega

/-- 8 or more below t1 ⇒ E₈ (index 7) < t1. -/
theorem e8_lt (E : Nat → Int) (t1 : Int) (hs : Sorted E) (n : Nat) (hn : 8 ≤ countBelow E t1 n) :
    E 7 < t1 := by
  by_cases h : E 7 < t1
  · exact h
  · have := countBelow_le_of_ge E t1 hs 7 (Int.not_lt.mp h) n
    omega

/-- at most 8 below tF, with more than 8 eigenvalues ⇒ E₉ (index 8) ≥ tF. -/
theorem e9_ge (E : Nat → Int) (tF : Int) (hs : Sorted E) (n : Nat) (hn9 : 8 < n)
    (hc : countBelow E tF n ≤ 8) : tF ≤ E 8 := by
  by_cases h : E 8 < tF
  · have := countBelow_ge_of_lt E tF hs 8 h n hn9
    omega
  · exact Int.not_lt.mp h

/-- The certificate at r = 9: counts (8, 8) at (t1, t_F) ⇒ E₉ − E₈ > 19,366,578 milli-J_E. -/
theorem gap_r9 (E : Nat → Int) (hs : Sorted E) (n : Nat) (hn9 : 8 < n)
    (h1 : countBelow E 52533422 n = 8) (hF : countBelow E 71900000 n = 8) :
    E 8 - E 7 > 19366578 := by
  have a := e8_lt E 52533422 hs n (by omega)
  have b := e9_ge E 71900000 hs n hn9 (by omega)
  omega

/-- For all r ≥ 9: E₉(r) ≥ E₉(9) (M ⪰ 0) and E₈ ≤ 54 J_E (flat trial space)
⇒ E₉ − E₈ ≥ 17,900,000 milli-J_E. The two inputs are hypotheses checked elsewhere. -/
theorem gap_all_r (e9r e9_9 e8r : Int) (hmono : e9_9 ≤ e9r) (h9 : 71900000 ≤ e9_9)
    (hflat : e8r ≤ 54000000) : e9r - e8r ≥ 17900000 := by
  omega

end HebcShadow
