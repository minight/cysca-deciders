## Introduction
Shitcrypto2 is an extention of shitcrypto1, which involves reversing the given python program in order to decrypt a ciphertext. The heart of the encryption lies in the `encr_vals` function, with all the other functions just doing preprocessing before and after the fact. We can also determine that for `n = 1` the cipher acts very much like an xor cipher. i.e.
`encrypt(key, encrypt(key, message, 1), 1) -> message`.

_For the first part of the write up we will lean n to be arbitrary, we will address this later_
_A deconstruction of cipher.py is not included, it should be present in the comments of the included cipher.py_

## Determining the behaviour of encr_vals
```python
def encr_vals(m_chr, k_chr, n):
    return (m_chr + k_chr) & ((1 << n) - 1)
```

This masks the addition of `m_chr + k_chr` with n `1`s. This is equivalent to `(m_chr + k_chr) % (2 ** n)`. Observe that
for `n = 1` this becomes `(m_chr + k_chr) % 2`, which is equivalent to `m_chr ^ k_chr`, this explains the beahviour we observed before. 

We can reverse this process by taking `(cip_char - k_char) % (2 ** n) <==> (cip_char - k_char) & ((1 << n) - 1)`. _(I'm not actially sure why this works, I determined it through trial and error)_

```python
def dencr_vals(cip, key,  n):
    return (cip - key) & ((1 << n) - 1)
```

This also allows us to reconstruct the `decrypt` function, simply by replacing `encr_vals` with `dencr_vals`.

## Initializing the key
We know that the plaintext begins with the `flag{`, as we know the cipher is xor-like, we can use this to determine
the first 5 bytes of potential keys. We also know that the cipher text will be partitioned into size n, so we need to
decrypt the first `k` bytes of the ciphertext, where `k` is the largest multiple of `n` that is smaller than `len('flag{')`.

```python
def initialize_key(cip, n):
    # clamp(x, top, bot) -> max(bot, min(x, top))
    # 5 = len('flag{')
    size =  clamp(n, 1, 5)
    size *= 5 // size
    return decrypt(cip[:size], ('flag{')[:size], n)
```
_A slightly more abstract version of this is present in solve.py_

## Determining the key length
_To reduce the complexity of this section we make the assumption that the plaintext is printable, and that `len(key) < len(plain_text)`._

As the plaintext is relatively short, we can easily bruteforce all possible key lengths. Once we guess a length, we pad it
out with a placeholder. We then just need to ensure that the known parts of the key lead to a decryption with printable
text. We then have a list of candidate lengths that might be the key length
```python
# cip is the ciphertext
# size is 'k' as described in the above section
# seed is the result of initialize_key
def guess_key_lengths(cip, size, n, seed):
    lens = []
    for i in range(len(cip) - size):
        size_guess = size + i
        msg = decrypt(cip, seed + ('a' * i), n)
        if all(msg[j] in string.printable or j % size_guess >= size for j in range(len(msg))):
            lens.append(size_guess)
    return lens
```
## Determining the flag
_This is probably not the optimal way to do it_

Armed with possible key lengths we can begin to solve for our plain_text, for this solution we just bruteforce possible
keys until we get a printable plaintext. As we can have bruteforces for extremely large numbers of characters, we apply
a limit to the maximum number of characters we are willing to bruteforce. Luckily for us this works out, such that we
only need to bruteforce a single character.
```python
possible = itertools.product(CHARSET, repeat=key_len - len(msg_seed))
```

We can check that our guessed key works by attempting to derive the key from the message seed and cipher text, that using
that key to rederive the message.
```python
key = decrypt(cip[:key_len], msg_seed + ''.join(guess), n)
message = decrypt(cip, key, n)
```

Putting this all together we get:
```python
def guess_flag(cip, key_len, n, msg_seed=''):
    size_bf = key_len - len(msg_seed)
    if size_bf > MAX_BF_SIZE:
        return None

    possible = itertools.product(CHARSET, repeat=size_bf)
    for guess in possible:
        key = decrypt(cip[:key_len], msg_seed + ''.join(guess), n)
        message = decrypt(cip, key, n)

        if message[-1] == '}' and all(c in CHARSET for c in message):
            return message
    return None
```

## Conclusion
We can use the above guess_flag function, to bruteforce on possible values of `n` in order to get our plain text
We can justify this bruteforce as well as the bruteforce for key_len as they are both small values. We just
got really lucky with our bruteforce for flag.

_The source for this solution is in solve.py_
