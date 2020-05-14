#!/bin/zsh

if [[ $# -eq 2 ]]; then brief=1; f=$2; pf=`basename $f`
elif [[ $# -eq 0 ]]; then f=`realpath .`; pf=$f
else f=`realpath $1`; pf=$f
fi

ft=`file --mime-type -b $f`
echo "$pf : $ft"
if [[ $ft =~ '^inode/directory' ]]; then
	if ! [[ -n $brief ]]; then
		for sf in $f/*; do
			view -L1 $sf
		done
	fi
elif [[ $ft =~ '^inode/x-empty' ]]; then
elif [[ $ft =~ '^text' ]]; then
	if [[ -n $brief ]]; then
		if [[ `wc -l <$f` -le 6 ]]; then
			cat $f
		else
			head -n5 $f
			echo "..."
		fi
	else
		if [[ `wc -l <$f` -le 40 ]]; then
			cat $f
		else
			head -n39 $f
			echo "..."
		fi
	fi
fi | sed 's/^/  /'
