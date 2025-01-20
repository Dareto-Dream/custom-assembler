.myFunction
ldi r1 10
ldi r2 0
str r2 r1 0
ldi r2 0
lod r2 r3 0
adi r3 1
mov r1 r3
ldi r2 0
str r2 r1 0
ret
.Main
ldi r1 12
ldi r2 1
str r2 r1 0
cal .myFunction
ret
hlt