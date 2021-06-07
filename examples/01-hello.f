: . emit ;

: dup sp@ @ ;

\ make some numbers
: -1 dup dup nand dup dup nand nand ;
: 0 -1 dup nand ;
: 1 -1 dup + dup nand ;
: 2 1 1 + ;
: 3 2 1 + ;
: 4 2 2 + ;
: 6 2 4 + ;

\ logic and arithmetic operators
: invert dup nand ;
: and nand invert ;
: negate invert 1 + ;
: - negate + ;

\ equality checks
: = - 0= ;
: <> = invert ;

\ stack manipulation words
: drop dup - + ;
: over sp@ 1 + @ ;
: swap over over sp@ 3 + ! sp@ 1 + ! ;
: nip swap drop ;
: 2dup over over ;
: 2drop drop drop ;

\ more logic
: or  invert swap invert and invert ;

\ left shift 1 bit
: 2* dup + ;

\ constant to check/set immediate flag
: 80h  1 2* 2* 2* 2* 2* 2* 2* ;

\ compile things
: , here @ ! here @ 2 + here ! ;

\ make words immediate
: immediate latest @ 2 + dup @ 80h or swap ! ;

\ control interpreter state
: [ 0 state ! ; immediate
: ] 1 state ! ;

\ unconditional branch
: branch rp@ @ dup @ + rp@ ! ;

\ conditional branch when top of stack is 0
: ?branch  0= rp@ @ @ 2 - and rp@ @ + 2 + rp@ ! ;

\ lit pushes the value on the next cell to the stack at runtime
\ e.g. lit [ 42 , ] pushes 42 to the stack
: lit ( -- x ) rp@ @ dup 2 + rp@ ! @ ;

\ ['] is identical to lit, the choice of either depends on context
\ don't write as : ['] lit ; as that will break lit's assumptions about
\ the return stack
: ['] ( -- addr ) rp@ @ dup 2 + rp@ ! @ ;