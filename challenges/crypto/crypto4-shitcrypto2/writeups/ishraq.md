# What does encrypt do?
encrypt(k,m,n) takes k = key, m = message, n = bit length parameter.
Repeat k til it is the same length as m. Treat each as a stream of 8|m| bits
and split that into blocks of n bits, padding with 0s if necessary.
Then add each pair of corresponding blocks mod 2^n, and then convert back to
the original format. So we just have a vignere cipher mod 2^n.

# Solution
We'll use the fact that the message starts with 'flag{' (which gives us 40
bits). Guessing the value of n=3 (less than 8 so we just try them all), and
running the process in reverse gives us the first 39 bits of the key (in the
script we assume we get 40 bits, I think this is just luck and in general we
might need to try guessing the 40th bit). We can then try decrypting 39 bits
(again we assume 40 bits=5chars are decrypted, here it doesn't matter cause if
x is printable ascii then x^1 probably is too) of the ciphertext from each
position and seeing if we get printable ascii characters. These positions
should form (or at least contain) an arithmetic progression with difference =
length of key if we got n correct. Here we see pretty clear AP with difference
6, so n=3 is probably correct.

There is only one character of the key we are missing so we just try all
possibilities and see which one gives the "right" flag, here we can tell by if
the final character of the flag is }.

Note we do not need to implement anything for decryption, we (roughly speaking)
just change the + to a - in encr\_vals.

```
import sys, string

# Convert (s = list of chars) to int in base 256
def to_num(s):
    x = 0
    for i in range(len(s)): x += ord(s[-1-i]) * pow(256, i)
    return x

# Break s into blocks of n chars = 8n bits, and convert each to base 256 number = n base256 digits
def get_nums(s, n):
    sections = [s[i:i+n] for i in range(0, len(s), n)]
    sections[-1] = sections[-1] + ("\x00" * (n - len(sections[-1])))
    return [to_num(x) for x in sections]

# Convert x to list of 8 base 2^n digits
def get_vals(x, n):
    vals = []
    mask = (1 << n) - 1
    for i in range(8):
        vals.append(x & mask)
        x = x >> n
    vals.reverse()
    return vals


# Convert list of base 2^n digits to string length n in base 256
def get_chrs(val_list, n):
    x = val_list[0]
    chrs = []
    for i in range(1, len(val_list)):
        x <<= n
        x += val_list[i]
    for i in range(n):
        chrs.append(chr(x % 256))
        x //= 256
    chrs.reverse()
    return "".join(chrs)

def decr_vals(m_chr, k_chr, n):
    return ((1<<n) + m_chr - k_chr) & ((1 << n) - 1)

def decrypt(k, m, n):
    if (n >= 8): raise ValueError("n is too high!")
    rep_k = k * (len(m) // len(k)) + k[:len(m) % len(k)] # repeated key
    m_val_list = [get_vals(x, n) for x in get_nums(m, n)]
    k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
    m_vals, k_vals, c_vals = [], [], []
    for lst in m_val_list: m_vals += lst
    for lst in k_val_list: k_vals += lst
    c_vals = [decr_vals(m_vals[i], k_vals[i % len(k_vals)], n)
        for i in range(0, len(m_vals))]
    c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
    return "".join([get_chrs(lst, n) for lst in c_val_list])

n = 3
s = "809fdd88dafa96e3ee60c8f179f2d88990ef4fe3e252ccf462deae51872673dcd34cc9f55380cb86951b8be3d8429839".decode('hex')

# This assumes all 40 bits are correct, but maybe we can only trust 39?
k = decrypt('flag{', s, n)[:5]

# Determine period for given n
for i in xrange(len(s)-5):
    dc = decrypt(k, s[i:i+5], n)[:5]
    p = all(c in string.printable for c in dc)
    if p:
        # Note that the dc do not exactly correspond with the final plaintext,
        # because the 40th bit can't actually be trusted
        print i, dc

for j in xrange(0,256):
    tk = k + chr(j)
    o = decrypt(tk, s, n)
    if o[-1] == '}':
        print tk.encode('hex'), o
```
