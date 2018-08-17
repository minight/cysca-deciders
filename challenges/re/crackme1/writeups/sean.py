import angr
import claripy
from pwn import *


BINARY = './crackme'
INPUT_LENGTH = 80

BASE = 0x400000
START_ADDR = BASE + 0xc6c

FIND_ADDR = BASE + 0xe99
AVOID_ADDR = BASE + 0xe8e

log.info('loading binary')
p = angr.Project(BINARY, load_options={'auto_load_libs': False})

log.info('setting up state')
state = p.factory.blank_state(addr=START_ADDR)

magic = claripy.BVS('magic', INPUT_LENGTH * 8)
state.memory.store(state.regs.rsp - 0x100, magic)
state.regs.rdi = state.regs.rsp - 0x100

log.info('exploring')
path = p.factory.path(state)
path_group = p.factory.path_group(path)

path_group.explore(find=FIND_ADDR, avoid=AVOID_ADDR)

if path_group.found:
    result = path_group.found[0].state.se.any_str(magic)#, INPUT_LENGTH)
    log.success(result)
else:
    log.error('No path found')

"""Submit flag
eWVzIGFuZCBoaXMgaGFuZHMgc2hvb2sgd2l0aCBleAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
"""
