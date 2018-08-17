import string
import itertools
from cipher import *

CHARSET = string.printable
PLAIN_FLAG = 'flag{'
MAX_BF_SIZE = 7

# helper
def log(msg):
    global verbose
    if not verbose: return
    print(msg)


def clamp(v, b, t):
    return max(b, min(v, t))

def dencr_vals(cip, key, n):
    # I have no clue why this works, but it does
    return (cip - key) & ((1 << n) - 1)

# This is just encrypt but with encr_vals replaced with dencr_vals
def decrypt(cip, key, n):
    if (n >= 8): raise ValueError("n is too high!")
    rep_k = key * (len(cip) // len(key)) + key[:len(cip) % len(key)]

    m_val_list = [get_vals(x, n) for x in get_nums(cip, n)]
    k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]

    m_vals, k_vals, c_vals = [], [], []
    for lst in m_val_list: m_vals += lst
    for lst in k_val_list: k_vals += lst

    # encr_vals is repaced with dencr_vals
    c_vals = [dencr_vals(m_vals[i], k_vals[i % len(k_vals)], n)
              for i in range(0, len(m_vals))]
    c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]

    return ''.join([get_chrs(x, n) for x in c_val_list])

def initialize_key(cip, n, plain_flag=PLAIN_FLAG):
    size = clamp(n, 1, len(plain_flag))
    size *= len(plain_flag)//size
    return (decrypt(cip[:size], plain_flag[:size], n), size)

def guess_key_lengths(cip, size, n, seed=''):
    lens = []
    for i in range(len(cip) - size):
        size_guess = size + i
        msg = decrypt(cip, seed + ('a' * i), n)
        # either the character in the message is in the charset (i.e. it is part of the flag we have found)
        # or the current character is not in the part we have found and can be whatever it wants
        # (j % size_guess >= size) <-- out of range of size
        if all(msg[j] in CHARSET or j % size_guess >= size for j in range(len(msg))):
            lens.append(size_guess)
    return lens

def guess_flag(cip, key_len, n, msg_seed=''):
    # brute force all keys
    size_bf = key_len - len(msg_seed)
    log("* Bruteforcing %d characters" % size_bf)
    if size_bf > MAX_BF_SIZE:
        log("- Bruteforce too big, skipping")
        return None

    possible = itertools.product(CHARSET, repeat=size_bf)
    for guess in possible:
        # Use our guess to try to find the key
        key = decrypt(cip[:key_len], msg_seed + ''.join(guess), n)
        # Use our guessed key to try to decrypt the message
        message = decrypt(cip, key, n)

        # If our decryption gave us ok characters, we win
        if message[-1] == '}' and all(c in CHARSET for c in message):
            return message
    return None

# With our decrypt function, we can now just bruteforce on n to get our answer
# this could probably be optimized by considering divisors of cip
def solve(cip):
    # If n is greater then the length of flag{, our try_solve_key function will fail
    # and we will need to work harder, luckily it doesn't so cbs
    for n in range(1, len(PLAIN_FLAG)+1):
        log("--- Trying n=%d ---" % n)
        # we know that the flag should start with flag{ (as per chal 1)
        key, size = initialize_key(cip, n)
        log("+ Found key [%s](len=%d)" % (key, size))

        # Our goal is to find possible key lengths
        guess_lens = guess_key_lengths(cip, size, n, seed=key)
        log("+ Found possible lengths %s" % str(guess_lens))

        # Using each guess find the associated key
        for guess_len in guess_lens:
            log("> Trying key length = %d" % guess_len)
            guess_key = guess_flag(cip, guess_len, n, msg_seed=PLAIN_FLAG)
            if guess_key is not None:
                log("! Found solution, terminating")
                return guess_key
    return "No flag found"

def de_hex(s):
    components = [s[i:i + 2] for i in range(0, len(s), 2)]
    return ''.join(chr(int(r, 16)) for r in components)


if __name__ == '__main__':
    import sys
    verbose = (sys.argv[1] == '-v') if len(sys.argv) > 1 else False
    cip = open('enc', 'r').read().strip()
    cip = de_hex(cip)
    print(solve(cip))
