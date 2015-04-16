#!/usr/bin/env bash
# usage:
# partion DIMENTION FOLDER1 [FOLDER2 [FOLDER3 ..]]

dim=${1%/};shift;
outfolder=${1%/};shift;

TRAIN_PER=0.80
#VAL_PER=0.10
TEST_PER=0.10

TEST_DIR="${outfolder}/test"
VAL_DIR="${outfolder}/val"
TRAIN_DIR="${outfolder}/train"

mkdir -p $TEST_DIR
mkdir -p $TRAIN_DIR
mkdir -p $VAL_DIR

function checkFile {
    #checkFile FileName Dimention
    if [[ ! -f "$1" ]]; then
	echo "$2" > "$1"
    fi
}

for folder in $@; do
    for file in ${folder%/}/*.txt; do

	NUMOFLINES=`wc -l $file | cut -f1 -d' '`
	TEMP1="$(bc -l <<< $NUMOFLINES*$TRAIN_PER)";
	TEMP2="$(bc -l <<< $NUMOFLINES*$TEST_PER)";
	TEMP2="${TEMP2%.*}";

	PS1="1";
	PE1="${TEMP1%.*}";
	
	PS2="$(($PE1+1))"
	PS3="$(($NUMOFLINES-$TEMP2))";
	
	PE2="$(($PS3-1))"
	PE3=$NUMOFLINES

	echo "${file##*/} : 1( $PS1 $PE1 ) 2( $PS2 $PE2 ) 3( $PS3 $PE3) ";	
	checkFile $TRAIN_DIR/${file##*/} $dim
	checkFile $TEST_DIR/${file##*/} $dim
	checkFile $VAL_DIR/${file##*/} $dim

	echo "Appending ${file} ..."
	
	TEMPFILE=`tempfile`;
	shuf $file -o $TEMPFILE

	sed -n "$PS1,${PE1}p; ${PS2}q" $TEMPFILE >> $TRAIN_DIR/${file##*/}
	sed -n "$PS2,${PE2}p; ${PS3}q" $TEMPFILE >> $VAL_DIR/${file##*/} 
	sed -n "$PS3,${PE3}p;" $TEMPFILE >> $TEST_DIR/${file##*/}

	#head -n "$PE1" $file >> $TRAIN_DIR/${file##*/}
	#sed -n "$PS2,${PE2}p; ${PS3}q" $file >> $VAL_DIR/${file##*/} 
	#tail -n "+$PS3" $file  >> $TEST_DIR/${file##*/}
	
	rm -f $TEMPFILE
    done
done
