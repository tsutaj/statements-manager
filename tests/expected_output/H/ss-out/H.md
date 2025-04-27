


## H: Many Kinds of Apples

### Problem Statement

Apple Farmer Mon has two kinds of tasks: "harvest apples" and "ship apples".

There are $N$ different species of apples, and $N$ distinguishable boxes. Apples are labeled by the species, and boxes are also labeled, from $1$ to $N$. The $i$-th species of apples are stored in the $i$-th box.

For each $i$, the $i$-th box can store at most $c_i$ apples, and it is initially empty (no apple exists).

Mon receives $Q$ instructions from his boss Kukui, and Mon completely follows in order. Each instruction is either of two types below.

- "harvest apples": put $d$ $x$-th apples into the $x$-th box.
- "ship apples": take $d$ $x$-th apples out from the $x$-th box.

However, not all instructions are possible to carry out. Now we call an instruction which meets either of following conditions "impossible instruction":

- When Mon harvest apples, the amount of apples exceeds the capacity of that box.
- When Mon tries to ship apples, there are not enough apples to ship.

Your task is to detect the instruction which is impossible to carry out.

### Input

Input is given in the following format.

```
$N$
$c_1$ $c_2$ $\cdots$ $c_N$
$Q$
$t_1$ $x_1$ $d_1$
$t_2$ $x_2$ $d_2$
$\vdots$
$t_Q$ $x_Q$ $d_Q$
```

In line 1, you are given the integer $N$, which indicates the number of species of apples.

In line 2, given $c_i$ $(1 \leq i \leq N)$ separated by whitespaces. $c_i$ indicates the capacity of the $i$-th box.

In line 3, given $Q$, which indicates the number of instructions.
Instructions are given successive $Q$ lines. $t_i$ $x_i$ $d_i$ means what kind of instruction, which apple Mon handles in this instruction, how many apples Mon handles, respectively. If $t_i$ is equal to $1$, it means Mon does the task of "harvest apples", else if $t_i$ is equal to $2$, it means Mon does the task of "ship apples".

### Constraints

All input values are integers, and satisfy the following constraints.

- $1 \leq N \leq 1{,}000$
- $1 \leq c_i \leq 100{,}000$ $(1 \leq i \leq N)$
- $1 \leq Q \leq 100{,}000$
- $t_i \in \left\\{ 1, 2 \right\\}$ $(1 \leq i \leq Q)$
- $1 \leq x_i \leq N$ $(1 \leq i \leq Q)$
- $1 \leq d_i \leq 100{,}000$ $(1 \leq i \leq Q)$

### Output

If there is "impossible instruction", output the index of the apples which have something to do with the first "impossible instruction".
Otherwise, output $0$.


### Sample Input 1
```
2
3 3
4
1 1 2
1 2 3
2 1 3
2 2 3
```



### Sample Output 1
```
1
```





In this case, there are not enough apples to ship in the first box.


### Sample Input 2
```
2
3 3
4
1 1 3
2 1 2
1 2 3
1 1 3
```



### Sample Output 2
```
1
```





In this case, the amount of apples exceeds the capacity of the first box.


### Sample Input 3
```
3
3 4 5
4
1 1 3
1 2 3
1 3 5
2 2 2
```



### Sample Output 3
```
0
```





### Sample Input 4
```
6
28 56 99 3 125 37
10
1 1 10
1 1 14
1 3 90
1 5 10
2 3 38
2 1 5
1 3 92
1 6 18
2 5 9
2 1 4
```



### Sample Output 4
```
3
```










