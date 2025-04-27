


## Problem C2

### <u>**Static Range Sum**</u>

### Problem Statement

You are given a non-negative integer sequence $A = (a_0, a_1, \ldots, a_{N-1})$ with the length $N$. Process the following $Q$ queries in order:

- You are given integers $l_i$​ and $r_i$​. Print $\sum_{k=l_i}^{r_i-1} a_k$​.

### Note

The difference between C1 and C2 is only constraints of $N$ and $Q$.

### Input

```
$N$ $Q$
$a_0$​ $a_1$​ $\ldots$ $a_{N-1}$​
$l_1$​ $r_1$​
$\vdots$
$l_Q$​ $r_Q$​
```

- All inputs are integers.
- $1 \leq N \leq 100\\,000$
- $1 \leq Q \leq 100\\,000$
- $-10^{9} \leq a_i \leq 10^{9}$
- $1 \leq l_i < r_i \leq N$

### Sample


### Sample Input 
```
5 5
1 10 100 1000 10000
2 3
0 3
2 5
3 4
0 5
```



### Sample Output 
```
100
111
11100
1000
11111
```








