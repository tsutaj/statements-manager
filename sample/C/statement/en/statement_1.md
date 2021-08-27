# Static Range Sum

## Note

The difference between C1 and C2 is only constraints of $N$ and $Q$.

## Problem statement

You are given a non-negative integer sequence $A = (a_0, a_1, \ldots, a_{N-1})$ with the length $N$. Process the following $Q$ queries in order:

- You are given integers $l_i$​ and $r_i$​. Print $\sum_{k=l_i}^{r_i-1}$​.

## Input

```
$N$ $Q$
$a_0$​ $a_1$​ $\ldots$ $a_{N-1}$​
$l_1$​ $r_1$​
$\vdots$
$l_Q$​ $r_Q$​
```

- All inputs are integers.
- ${@constraints.MIN_N_SMALL} \leq N \leq {@constraints.MAX_N_SMALL}$
- ${@constraints.MIN_Q_SMALL} \leq Q \leq {@constraints.MAX_Q_SMALL}$
- ${@constraints.MIN_A} \leq a_i \leq {@constraints.MAX_A}$
- $1 \leq l_i < r_i \leq N$

## Sample

{@samples.all}
