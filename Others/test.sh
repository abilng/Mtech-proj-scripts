#!/bin/bash
# Testing TrainedModel
# It require test.main (T2) file.and 
# Python dnn config in $CONFIG_JSON  with data_cofig.json 
#   with test=test.main
#
#-----------------------------------
# examle test.main:
#    57600 3
#    tmplist.list
#    empty.list
#    empty.list

PYTHON_DNN_HOME="/home/abil/python-dnn2/"

TESTDIR="/home/abil/MSR2-action-data/test/"
DATA_DIR="data_in" #relative to $TESTDIR

CONFIG_JSON="/home/abil/MSR2-action-data/test/CNN/model_conf.json"

touch $TESTDIR/empty.list
mkdir -p $TESTDIR/labels/


cd $PYTHON_DNN_HOME
for fullfilename in $TESTDIR/$DATA_DIR/*.txt ; do
	filename=$(basename $fullfilename);
	echo "On $DATA_DIR/$filename"
	echo "$DATA_DIR/$filename" >$TESTDIR/tmplist.list
	THEANO_FLAGS=device=gpu,floatX=float32 exception_verbosity=high ./python-dnn $CONFIG_JSON
	mv "$PYTHON_DNN_HOME/test.out" "$TESTDIR/labels/$filename.out"
done