cal .Main
hlt
.Main
ldi r1 5
ldi r2 0
str r2 r1 0
.while_start_0
ldi r2 0
lod r2 r3 0
ldi r4 0
cmp r3 r4
brh lt .while_end_1
ldi r2 0
lod r2 r3 0
ldi r1 1
sub r3 r1 r3
mov r3 r1
ldi r2 0
str r2 r1 0
jmp .while_start_0
.while_end_1
ret