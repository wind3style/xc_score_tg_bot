#!/bin/bash

## META: 15

#Version:1.5 Date:25.09.2014
##############################

# Core Dump Limit
ulimit -c unlimited

# Open File Descriptors Limit
ulimit -n 65536

# имя файла запускаемой программы
PRG_NAME="xc_score_tg_bot"

# полный путь до скрипта
CMD_NAME=`readlink -e "$0"`

. /etc/xc_score/xc_score_tg_bot

# каталог в котором лежит скрипт
CMD_DIR=$PREFIX

# каталоги функциональные
LCK_DIR="$CMD_DIR/var/run"
LOG_DIR="$CMD_DIR/var/log"
CFG_DIR="$CMD_DIR/etc"
BIN_DIR="$CMD_DIR/bin"
CFG_EXT="conf"

mkdir -p $LCK_DIR
mkdir -p $LOG_DIR

run_program_prepare ()
{
    CMD="${BIN_DIR}/${PRG_NAME}.py -c ${CFG_DIR}/${1}.${CFG_EXT}"
}


run_program ()
{
    run_program_prepare $1
    echo "CMD: ${CMD}" 1>&2 2>>${LOG_DIR}/${1}_console.log
    ${CMD} 1>&2 2>>${LOG_DIR}/${1}_console.log
}

run_program2 ()
{
    run_program_prepare $1
    echo "CMD: ${CMD}"
    ${CMD}
}

start_one ()
{
    if [ -f ${LCK_DIR}/${1}.pid ]; then
        printf "${1} pid file is exists. Process may be running.\nRun restart command...\n"
        restart_one $1
   else
        touch ${LCK_DIR}/${1}.pid
        (while [ -f ${LCK_DIR}/${1}.pid ]; do
            echo "Start ${PRG_NAME} ${1}.${CFG_EXT} " `date '+%Y-%m-%d %H:%M:%S'` >> ${LOG_DIR}/${1}_restart.log
            run_program $1
            sleep 1
        done) 1>&2 2>>${LOG_DIR}/${1}_console.log &
        echo $! >${LCK_DIR}/${1}.pid
        echo "${PRG_NAME} ${1} start - OK"
    fi
}

stop_one ()
{
    if [ -f ${LCK_DIR}/${1}.pid ]; then
        p=$(cat ${LCK_DIR}/${1}.pid)
        rm -f ${LCK_DIR}/${1}.pid

        if [ -d /proc/${p} ]; then
            pp=`ps --ppid ${p} -opid --no-headers | sed 's/^[ ]*//'`
            if [ -d /proc/${pp} ]; then
                echo "PID for killing: "${pp}
                kill -TERM ${pp}
                echo "${PRG_NAME} ${1} stop - OK"
                return 0
            fi
        else
          echo "${1} loop process does not exist."
        fi
    else
        echo "${1} pid file not exists."
    fi
    echo "${PRG_NAME} ${1} stop - FAIL"
    return 1
}

rotate_one ()
{
    if [ -f ${LCK_DIR}/${1}.pid ]; then
        p=$(cat ${LCK_DIR}/${1}.pid)
        if [ -d /proc/${p} ]; then
            pp=`ps --ppid ${p} -opid --no-headers | sed 's/^[ ]*//'`
            if [ -d /proc/${pp} ]; then
                echo "PID for killing: "${pp}
                kill -TERM ${pp}
                echo "${PRG_NAME} ${1} rotate - OK"
                return 0
            fi
        else
          echo "${1} loop process does not exist."
        fi
    else
        echo "${1} pid file not exists."
    fi
    echo "${PRG_NAME} ${1} rotate - FAIL"
    return 1
}

clean_one ()
{
    echo "Clean for config name: ${1}"
    unset CLEAN_DAYS
    source ${CFG_DIR}/${1}.${CFG_EXT}
    if [ -v CLEAN_DAYS ]; then
        CMD="find ${STORE_DIR}/${1} -type f -mtime +${CLEAN_DAYS} -name *.pcap -delete"
        echo "CMD: ${CMD}"
        ${CMD}
        if [ $? -eq 0 ]; then
            echo "${PRG_NAME} ${1} clean - OK"
        else
            echo "${PRG_NAME} ${1} clean - FAIL"
        fi
    else
        echo "${PRG_NAME} ${1} clean - Disabled"
    fi
    return 1
}


restart_one ()
{
    stop_one $1
    echo "Please wait..."
    sleep 3
    start_one $1
}

start ()
{
    if [ "$1" = "ALL" ]; then
        for cfg in ${CFG_DIR}/*.${CFG_EXT}
        do
            [ -f $cfg ] && start_one `basename $cfg .${CFG_EXT}`
        done
    else
        start_one $1
    fi
}


stop ()
{
    if [ "$1" = "ALL" ]; then
        for cfg in ${CFG_DIR}/*.${CFG_EXT}
        do
            [ -f $cfg ] && stop_one `basename $cfg .${CFG_EXT}`
        done
    else
        stop_one $1
    fi
}

rotate ()
{
    if [ "$1" = "ALL" ]; then
        for cfg in ${CFG_DIR}/*.${CFG_EXT}
        do
            [ -f $cfg ] && rotate_one `basename $cfg .${CFG_EXT}`
        done
    else
        rotate_one $1
    fi
}

clean ()
{
    if [ "$1" = "ALL" ]; then
        for cfg in ${CFG_DIR}/*.${CFG_EXT}
        do
            [ -f $cfg ] && clean_one `basename $cfg .${CFG_EXT}`
        done
    else
        clean_one $1
    fi
}


restart ()
{
    if [ "$1" = "ALL" ]; then
        stop $1
        echo "Please wait..."
        sleep 5
        start $1
    else
        restart_one $1
    fi
}


cd ${CMD_DIR}

case "$1" in

    start)
        start ${2:-ALL}
        ;;
    stop)
        stop ${2:-ALL}
        ;;
    restart)
        restart ${2:-ALL}
        ;;
    run)
        run_program2 ${2:-ALL}
        ;;
    rotate)
        rotate ${2:-ALL}
        ;;
    clean)
        clean ${2:-ALL}
        ;;
    *)
        echo "Use: ${CMD_NAME} <start | stop | restart> [instance name]"
        ;;
esac
