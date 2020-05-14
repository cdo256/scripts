#!/bin/bash
command=$1
shift
indent() {
	sed 's/^/  /g'
}
a=`filemake`
$command "$@" 2>$a
if [[ $? -eq 127 ]]; then
	vs=($(sudo pacman -Fq $command))
	if [[ $? -ne 0 ]]; then
		eror "command not found (pacman failed)"
	elif [[ $#vs -eq 0 ]]; then
		eror "command not found (no external results)"
	elif [[ $#vs -eq 1 ]]; then
		echo "installing..."
		sudo pacman -S ${vs[1]} | indent
		echo "running..."
		$command $@ | indent
	else
		for (( i = 1; i <= $#vs; i++ )) do
			printf "%i %s\n" $i ${vs[i]}
		done
		read choice
		if [[ -n ${vs[choice]} ]]; then
			echo "installing..."
			sudo pacman -Sy ${vs[choice]} | indent
			echo "running..."
			$command $@ | indent
		else
			eror "invalid choice"
		fi
	fi
else
	>&2 cat $a
fi
