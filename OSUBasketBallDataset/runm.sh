#!/bin/bash
dirname="$1"
if [[ -z "$2" ]]; then
	isRandom="false"	
else
	isRandom="$2"
fi
if [[ -z "$3" ]]; then
	Grey="true"	
else
	Grey="$3"
fi

matlab_exec=/sre1/software/matlab/bin/matlab
function join { local IFS="$1"; shift; echo "$*"; }

function execute(){
	if [[ "$#" -ne 0 ]]; then
		name=$1;
		shift;
		if [[ -z "$1" ]]; then
			X="${name}"
		else
			X="${name}($(join , $@))"
		fi
		FILENAME=$RANDOM
		echo "${X}" >"log/${FILENAME}.log"
		${matlab_exec} -nojvm -nodisplay -nosplash -r "${X}; exit" >>"log/${FILENAME}.log"
		echo "$X"
	fi
}


{
	execute PumpFeatures "'FourOnFour'" "'Video8.avi'" "'$dirname'" $isRandom $Grey
	execute PumpFeatures "'Drills'" "'Video1.avi'" "'$dirname'" $isRandom $Grey
	execute PumpFeatures "'Drills'" "'Video6.avi'" "'$dirname'" $isRandom $Grey
	execute PumpFeatures "'Drills'" "'Video9.avi'" "'$dirname'" $isRandom $Grey
}&
echo "$!"
{
	execute PumpFeatures "'TwoOnTwo'" "'Video3.avi'" "'$dirname'" $isRandom $Grey
	execute PumpFeatures "'TwoOnTwo'" "'Video4.avi'" "'$dirname'" $isRandom $Grey
	execute PumpFeatures "'TwoOnTwo'" "'Video5.avi'" "'$dirname'" $isRandom $Grey
	execute PumpFeatures "'TwoOnTwo'" "'Video7.avi'" "'$dirname'" $isRandom $Grey
}&
echo "$!"

wait
echo "all jobs are done!"
