Very basic Forth version implemented in Python

Here's what you can expect:
```
1 2
 ok
. .
2 1  ok
.s
[] <- top of stack ok
2
 ok
.
2  ok
emit
stack underflow !!
.
stack underflow !!
1 2 . .
2 1  ok
1 2 + .
3  ok
.s
[] <- top of stack ok
3
 !!
: 3 2 1 + ;
 ok
3 2 + .
5  ok
```