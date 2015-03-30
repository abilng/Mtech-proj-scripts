#!/bin/sh

INDIR="$1"
OUTDIR="$2"

mkdir -p $OUTDIR 

for typ in "train" "test" "val"
do 
    MINCNT=10000000
    for file in  $INDIR/*_$typ.txt
    do
	count=$(wc -l < $file)
	if [ $MINCNT -gt $count ]
	then
            MINCNT=$count
	fi
    done
    for infile in  $INDIR/*_$typ.txt
    do
	echo "[$MINCNT lines] $infile --> $OUTDIR/$(basename $infile)"
	head -n $MINCNT $infile > $OUTDIR/$(basename $infile)
    done
done
