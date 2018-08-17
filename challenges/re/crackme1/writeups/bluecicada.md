# This writeup is shit
but nobody has uploaded anything for this challenge so I'm going to upload it anyway

Ironically, this challenge did not teach me how 2 angr (more like learn2radare)

You can probably spin up an angr script to do this, but it would be easier just to inspect the binary in radare
(that said, I hear that the original challenge this was based on was like solving 2000 variations of this in a finite amount of time, so good luck trying to do that manually)

```
r2 -A learn2angr   # open the binary with radare and analyse functions or some shit
afl                # to list functions identified during analysis
```

You'll see a crapton of functions named something like "sub.exit_93b". Turns out these each do a single letter comparison, and these letters form the flag.

```
VV                 # view control flow graph
n                  # keep pressing n to move through the graphs for each function
```

And just read the flag off the graphs (the functions happen to be in order)

## side notes
I couldn't run the binary - `file learn2angr` tells me that it uses musl instead of glibc. I spent a few hours trying to install musl and gave up
