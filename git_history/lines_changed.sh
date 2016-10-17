#!/bin/bash

##############
# Find number of lines added/deleted 
# by date/user for repos
##############


#OPTIONS
while [[ $# -gt 1 ]]; do
	key="$1";
	
	case $key in 
		-d|--searchdir)
		SEARCHDIR="$2";
		shift
		;;
		-o|--outfile)
		OUTFILE="$2"
		;;
	    *)
		
		;;
	esac
	shift
done

CURDIR=`pwd`
OLD_IFS=$IFS
IFS=$'\n'
		
if [ -z $SEARCHDIR ]; then
  	#Are you in a git repo now?
	in_repo=`git rev-parse --is-inside-work-tree`
	
	if [ $in_repo ]; then 
		safety=10;
		no_dir=1;
		i=0;
		cur_dir="./"
		while [[ no_dir -eq 1 && $i -lt $safety ]]; do
			if [[ `ls $cur_dir.git 2> /dev/null` ]]; then
				
				SEARCHDIR=$cur_dir
				no_dir=false
			else
				cur_dir="../"$cur_dir
			fi

			i=$(( $i + 1 ))
		done

	#if not, use home dir
	else 
		SEARCHDIR="~/"
	fi
fi

repos=$( find $SEARCHDIR -type d -name ".git" )
commits=""
for repo in $repos; do
	cd `dirname $repo`
	repo_name=$( basename `git rev-parse --show-toplevel` )
	commits+=`git log --shortstat --pretty=format:"Œ $repo_name	%at  %H  %cI  %cn" | tr -d "\n" | tr "Œ" "\n" 2> /dev/null` 
	
done

final_commits="";

while  read -r line; do
	final_commits+=$'\n'
	if [[ -n `echo "$line" | grep 'insertion[s]*(+)' | grep 'deletion[s]*(-)'` ]]; then
		final_commits+=$( echo "$line" | sed -e 's/\(.*\)\([0-9]\{1,\} file[s]* changed, \)\([0-9]*\) insertion[s]*(+)*, \([0-9]*\)\( delet.*\)/\1  \3      \4/g' );
	elif [[ -n `echo "$line" | grep 'insertion[s]*(+)'` ]]; then
		final_commits+=$( echo "$line" | sed -e 's/\(.*\)\([0-9]\{1,\} file[s]* changed, \)\([0-9]*\) insertion[s]*(+)*\(.*\)/\1  \3	0/g' );
	elif [[ -n `echo "$line" | grep 'deletion[s]*(-)'` ]]; then
		final_commits+=$( echo "$line" | sed -e 's/\(.*\)\([0-9]\{1,\} file[s]* changed, \)\([0-9]*\) deletion[s]*(-)/\1	0  \3/g' );
	else
		final_commits+=$( echo $line )
	fi

	
done <<< "$commits"

cd $CURDIR
if [[ -n $OUTFILE ]]; then
	echo "$final_commits" > "$OUTFILE"
else
	echo "$final_commits"
fi

IFS=$OLD_IFS