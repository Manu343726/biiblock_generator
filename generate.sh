#!/bin/sh

entry_point="generate.py"
sources=("${entry_point}" "utils.py")
remote="https://raw.githubusercontent.com/Manu343726/biiblock_generator/master"

for source in "${sources[@]}"; do
    wget -q -N -O "${source}" "${remote}/${source}"
done

''''which python2 >/dev/null 2>&1 && exec python2 "./${entry_point}" "$@" # '''
''''which python  >/dev/null 2>&1 && exec python  "./${entry_point}" "$@" # '''
''''exec echo "Error: I can't find python anywhere"                       # '''

for source in "${sources[@]}"; do
    rm -fv "./${source}"
done
