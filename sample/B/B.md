# 回文判定

## 問題文

長さ $N$ の文字列 $S$ が与えられます。文字列は奇数長であることが保証されます。

与えられる文字列 $S$ が回文であるか判定してください。

## 入力

```
$N$
$S$
```

- ${@constraints.MIN_N} \leq N \leq {@constraints.MAX_N}$
- {@constraints.N_IS_ODD}
- $|S| = N$
- {@constraints.GIVEN_STRING_IS_LOWERCASE}

## 出力

与えられる文字列が回文であれば ``Yes`` を、そうでなければ ``No`` を一行で出力してください。**出力の末尾で改行してください。**

## 入出力例

### 入力例 1
{@samples.sample_00_in}

### 出力例 1
{@samples.sample_00_out}

### 入力例 2
{@samples.sample_01_in}

### 出力例 2
{@samples.sample_01_out}
