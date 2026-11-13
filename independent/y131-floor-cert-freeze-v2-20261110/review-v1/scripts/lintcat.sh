#!/bin/bash
L=/tmp/opus55ffv/trace/lint.out
grep -v LINT_RESULT $L | sed -E 's/^line [0-9]+: //' | sed -E 's/ (work|final|\.\.)\/.*//' | cut -c1-60 | sort | uniq -c | sort -rn | head
head -3 $L | cut -c1-220
grep -c 'PIN' $L
