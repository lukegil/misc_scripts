#!/bin/bash

##############
# Find number of lines added/deleted 
# by date/user for repos
##############


#OPTIONS
while [[ $# -gt 1 ]]; do
	key="$1";
	
	case $key in 
		-d|--dir)
		SEARCHDIR="$2";
		shift
		;;
	    *)
		
		;;
	esac
	shift
done

CURDIR=`pwd`
		
if [-z $SEARCHDIR ]; then
	
	#Are you in a git repo now?
	in_repo=`git rev-parse --is-inside-work-tree`
	if [ $in_repo ]; then 
		safety=10;
		no_dir=1;
		i=0;
		cur_dir="./"
		while [ no_dir && $i -lt $safety]; do
			if [ `ls $cur_dir.git 2> /dev/null` ]; then
				SEARCHDIR=$cur_dir
				no_dir=0
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
	cd $repo
	repo_name=$( basename `git rev-parse --show-toplevel` )
	commits+=`git log --shortstat --pretty=format:"!=!=! %n$repo_name	%at  %H  %cI  %cn" | 
			  tr -d \n | 
			  sed $'s/!=!=!/\n/g' |
			  sed 's/[0-9] files changed, \([0-9]*\) insertions(+),/\1/g'`
done

commits=$(  2 files changed, 15 insertions(+), 4 deletions(-
