#!/bin/bash
# Nov 7 2018

# ---------------------------------------------
# aux functions
# trap ctrl-c and exit
trap ctrl_c INT

function ctrl_c() {
    echo -e "\nAborting"
    killall python3 -q > /dev/null 2>&1
    mv game_consts.py.backup ../game_consts.py
    exit 2
}

# run a batch of tests
run_tests() {
    FILES="consts_files/*"
    LEVEL=$1
    GHOSTS=$2
    GHOSTS_LEVEL=$3

    echo -e "Map $LEVEL, $GHOSTS Ghosts, Ghosts Level $GHOSTS_LEVEL\n\n" > results/averages_${LEVEL}_${GHOSTS}_${GHOSTS_LEVEL}.txt
    cd .. > /dev/null

    # run the server
    if [ $GHOSTS -eq 0 ]; then
        python3 server.py --map data/map$LEVEL.bmp --ghosts 0 & #>> log_run_consts_test_server 2>&1 &
    else 
        python3 server.py --map data/map$LEVEL.bmp --ghosts $GHOSTS --level $GHOSTS_LEVEL & #>> log_run_consts_test_server 2>&1 &
    fi
    
    echo -e "\n\e[33mWaiting for server finishing its setup\n\033[0m"
    sleep 5
    python3 viewer.py >> log_viewer &
    cd - > /dev/null

    # for each consts file
    for FILE in $FILES ; do
        echo -e "\e[34m---------------\nProcessing $FILE file...\033[0m"   

        # const file is now the game_const used in the program
        cp $FILE ../game_consts.py 
        
        # run N_ITERS tests with this file. 
        # this will produce a result in file our_tests/averages  (the average)
        cd .. > /dev/null
        ./test_tool.sh $NUM_ITERS >> log_run_consts_test #2>&1   
        #pwd
        #pwd
        # exit 1

        cd - > /dev/null

        # print results 
        echo -ne "\t${FILE:13} -> " 
        cat averages_run
        echo -ne "${FILE:13} -> " >> results/averages_${LEVEL}_${GHOSTS}_${GHOSTS_LEVEL}.txt
        cat averages_run >> results/averages_${LEVEL}_${GHOSTS}_${GHOSTS_LEVEL}.txt

        # # remove game_const file and average file
        # rm ../game_consts.py
        rm -f averages_run
    done
      
    killall python3 -q > /dev/null 2>&1
}

# compute average of a scores file
average () {
    if [ -f $1 ]; then
        s=${1%%.*}
        
        awk 'NF' $1 > aaaaaa #trim empty lines
        awk '{s+=$1}END{print "\t",(NR?s/NR:"NaN")}' RS="\n" aaaaaa
        awk '{s+=$1}END{print "\t",(NR?s/NR:"NaN")}' RS="\n" aaaaaa >> consts_averages
        rm -f aaaaaa   
    fi  
}

# ---------------------------------------------
# "MAIN"
# comment tests as needed

NUM_ITERS=10


# backup original file
mv ../game_consts.py game_consts.py.backup > /dev/null

# constants
FILES=consts_files/*

# create needed dirs
mkdir -p results/

killall python3 -q > /dev/null 2>&1

# mapa de nıvel 1 conhecido, número de fantasmas 
# echo -e "\e[34mLevel 1, No ghosts\033[0m"
# run_tests 1 0 0  

# mapa de nıvel 2 conhecido, número de fantasmas 2, dificuldade 1
#echo -e "\e[34mMap 2, 2 Ghosts, Level 1\033[0m"
#run_tests 2 2 1 

# mapa de nıvel 2 conhecido, número de fantasmas 2, dificuldade 2
#echo -e "\e[34mMap 2, 2 Ghosts, Level 2\033[0m"
#run_tests 2 2 2 

# mapa de nıvel 2 conhecido, número de fantasmas 4, dificuldade 1
#echo -e "\e[34mMap 2, 4 Ghosts, Level 1\033[0m"
#run_tests 2 4 1 

#! WHEN THIS TEST IS RUN, RERUN GEENRATE CONST
#! FILES FIRST WITH THE APROPRIATED VALUES
# mapa de nıvel 2 conhecido, número de fantasmas 4, dificuldade 2
echo -e "\e[34mMap 2, 4 Ghosts, Level 2\033[0m"
run_tests 2 4 3 

# ---------------------------------------------
# restore game_consts
mv game_consts.py.backup ../game_consts.py
