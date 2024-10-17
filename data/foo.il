foo:
    addi sp, sp, -12
    sw v1, 8(sp)
    sw v2, 4(sp)
    sw v3, 0(sp)
    li v3, 10
    li v1, 0
    li v2, 1

loop_start:
    blt v1, a0, loop_body
    j loop_end

loop_body:
    slli v4, v1, 1
    add v3, v4, v2
    addi v1, v1, 1
    add v2, v1, v3
    j loop_start
    
loop_end:
    mv a0, v2
    lw v3, 0(sp)
    lw v2, 4(sp)
    lw v1, 8(sp)
    addi sp, sp, 12
    jr ra
