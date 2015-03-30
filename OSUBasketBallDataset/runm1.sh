#!/bin/bash
dirname="$1"
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


# {
#	execute PumpFeatures "'FourOnFour'" "'Video8.avi'" "'$dirname'" $isRandom $Grey
#	execute PumpFeatures "'Drills'" "'Video1.avi'" "'$dirname'" $isRandom $Grey
#	execute PumpFeatures "'Drills'" "'Video6.avi'" "'$dirname'" $isRandom $Grey
#	execute PumpFeatures "'Drills'" "'Video9.avi'" "'$dirname'" $isRandom $Grey
#}&
#echo "$!"
{
	execute PumpFeatures1 "'TwoOnTwo'" "'Video3.avi'" "'$dirname'"
	execute PumpFeatures1 "'TwoOnTwo'" "'Video4.avi'" "'$dirname'"
}&
echo "$!"
{
	execute PumpFeatures1 "'TwoOnTwo'" "'Video5.avi'" "'$dirname'"
	execute PumpFeatures1 "'TwoOnTwo'" "'Video7.avi'" "'$dirname'"
}&
echo "$!"

wait
echo "all jobs are done!"
