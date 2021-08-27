# Static Range Sum

## 注意

問題 C1 と C2 では、$N$ と $Q$ の制約のみが異なります。

## 問題文

長さ $N$ の非負整数列 $A = (a_0, a_1, \ldots, a_{N-1})$ が与えられます。以下で説明されるクエリを順に $Q$ 回処理してください。

- 整数 $l_i$​ と $r_i$​ が与えられるので、$\sum_{k=l_i}^{r_i-1}$​ を出力する。

## 入力

```
$N$ $Q$
$a_0$​ $a_1$​ $\ldots$ $a_{N-1}$​
$l_1$​ $r_1$​
$\vdots$
$l_Q$​ $r_Q$​
```

- 入力は全て整数で与えられる
- ${@constraints.MIN_N_LARGE} \leq N \leq {@constraints.MAX_N_LARGE}$
- ${@constraints.MIN_Q_LARGE} \leq Q \leq {@constraints.MAX_Q_LARGE}$
- ${@constraints.MIN_A} \leq a_i \leq {@constraints.MAX_A}$
- $1 \leq l_i < r_i \leq N$

## 入出力例

{@samples.all}
