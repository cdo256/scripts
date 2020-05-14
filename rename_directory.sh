#!/bin/zsh

sorc=$1
dest=$2
[[ -n $3 ]] && diry=$3 || diry=.

if true; then
bkup $diry
bkup $sorc
bkup $dest 
fi >/dev/null 2>/dev/null

truncate -s 0 .diryrnam

for file in `find $diry`; do
	n=`sed "s/$sorc/$dest/g" <<<$file`
	if [[ $file != $n ]]; then
		cp -r $file $n
		echo $file >>.diryrnam
	fi
done

while read file; do
	remv $file
done <.diryrnam

truncate -s 0 .diryrnam_1

for file in `find $diry`; do
	echo $file
	[[ -f $file ]] &&
		echo $file >>.diryrnam_1 &&
		sed -i "s/$sorc/$dest/g" $file
done

echo "`wc -l <.diryrnam` files renamed"
echo "`wc -l <.diryrnam_1` files changed"
