from pwn import *
r = remote('localhost', 9091)
r.recv()
cmd = 'cat flag.txt'
cmdline = 'A' * 16 * 256 + cmd
r.sendline(' <|>tag ' + cmdline)
mac = r.recv().split()[0]
print mac
cmdline = ' ' * 16 * 256 + cmd
r.sendline(mac + '<|>' + cmdline)
print r.recv()
