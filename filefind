#!/bin/zsh
x=`filemake`
grep -nrH $2 -e $1 | tee $x | cat -n
c=`wc -l <$x`
if [[ c -ne 0 ]]; then
	read "?>"
	echo $REPLY
	a=`<$x sed "${REPLY}q;d" | tr ':' '\n' | head -n2`
	fn=`head -n1 <<<"$a"`
	ln=`tail -n1 <<<"$a"`
	edit -l $ln $fn
else
	<<<"not found"
fi
