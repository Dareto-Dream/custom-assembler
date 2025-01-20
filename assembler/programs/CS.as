ldi r1 10
ldi r2 0
str r2 r1 0
lod r2 r3 0
ldi r4 5
cmp r3 r4
brh lt .end_0
lod r2 r3 0
adi r3 1
mov r3 r1
str r2 r1 0
.end_0
hlt