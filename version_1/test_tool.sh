#!/bin/bash
# Nov 3 2018

# validate arguments sanity
if [ $# != 1 ]; then
	echo "$0 number_of_iterations"
	exit 1
fi

if [ $# -lt 1 ]; then
	echo "Number of iterations must be 1 or more"
	exit 2
fi

# aux functions 

# compute average
average () {
    if [ -f $1 ]; then
        s=${1%%.*}
        if [[ $2 == 1 ]]; then
            printf "\t${s:28}" 
        else
            printf "\t${s:17}" 
        fi
        
        awk 'NF' $1 > aaaaaa #trim empty lines
        sed -i '/NaN/d' aaaaaa   #remove NaN
        awk '{s+=$1}END{print "\t",(NR?s/NR:"NaN")}' RS="\n" aaaaaa

        if [[ $2 != 1 ]]; then
            echo "ADDDING THE VALUE "
            awk '{s+=$1}END{print "\t",(NR?s/NR:"NaN")}' RS="\n" aaaaaa >> our_tests/averages_run   # for batch processing on run_consts_tests
        fi
        rm -f aaaaaa   
    fi  
}

# time stats
average_time () {
    if [ -f $1 ]; then
        awk 'NF' $1 > aaaaaa #trim empty lines
        awk '{s+=$1}END{print "",(NR?s/NR:"NaN")}' RS="\n" aaaaaa
    fi
}

max () {
    if [ -f $1 ]; then
        grep -Eo '[0-9]+.[0-9]+' $1 | sort -rn | head -n 1
    fi 
}

# print history averages
print_last_averages () {
    echo -e "\n--------------------\nLast averages: "

    average 'our_tests/old_scores/scores.log' 1
    average 'our_tests/old_scores/scores_ghosts_level0.log' 1
    average 'our_tests/old_scores/scores_ghosts_level1.log' 1
    average 'our_tests/old_scores/scores_ghosts_level2.log' 1
}

# print run info
print_run_info () {
    echo -e "--------------------\nThis run:\n"
    average 'our_tests/scores/scores.log'
    average 'our_tests/scores/scores_ghosts_level0.log'
    average 'our_tests/scores/scores_ghosts_level1.log'
    average 'our_tests/scores/scores_ghosts_level2.log'
    echo -e "\n\tCrashes:\t" $1
    echo -e "\tTimes (seg):"
    printf "\n\t\tAver:\t" 
    average_time 'our_tests/times.txt'
    printf "\t\tMax:\t"
    max 'our_tests/times.txt'
}

# trap ctrl-c and exit
trap ctrl_c INT

function ctrl_c() {
    echo -e "\nAborting"
    exit 2
}

if [ $1 -eq 1 ]; then
    echo -e "Pacman Test Tool ($1 iteration)\n"
else
    echo -e "Pacman Test Tool ($1 iterations)\n"
fi

# create needed dirs
mkdir -p our_tests/
mkdir -p our_tests/averages/
mkdir -p our_tests/scores
mkdir -p our_tests/old_scores
mkdir -p our_tests/backup_scores
mkdir -p our_tests/iter_logs

# save old scores 
mv our_tests/scores/scores* our_tests/old_scores/ > /dev/null 2>&1

declare -i crash_count
crash_count=0

# run $1 timese
for i in $(seq 1 $1); do 
    echo -e "Execution #$i"
    /usr/bin/time -f "%e" -a -o "times.txt" --quiet python3 student.py > our_tests/iter_logs/output_$i.txt #2> tmp_error.txt  
    
    printf "\nTime was: " 
    sed "${i}q;d" times.txt
    
    #printf "\nOutput was: "
    #cat iter_logs/output$i.txt
    

    # copy save of scores
    if [ $? -eq 0 ]; then 
        cp scores* our_tests/backup_scores/
    
    # program failed, restore scores
    else    
        echo -e "\033[93mERROR: Execution #$i failed (game crashed). Restoring scores\033[0m"
        
        #echo -e "Error: " 
        #cat tmp_error.txt
        
        crash_count=crash_count+1
        
        mv -f our_tests/backup_scores/scores* .. > /dev/null 2>&1
    fi

    mv key_times.log our_tests/iter_logs/key_times_$i.log
    
    echo -e "---------------------\n"
done

echo -e "\nAll $1 iterations done\n\n"
mv scores* our_tests/scores/

# clean up
rm -f tmp_error.txt
#mv our_tests/scores/scores* our_tests/scores/
mv times.txt our_tests/

# print results
print_run_info $crash_count
print_last_averages
echo -e "\nIf an average is NaN it's not an error.\nIt means a script execution failed, was canceled or the client was exited using sys.exit."

echo -e "\n"


