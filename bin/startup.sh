#!/bin/bash
# Author kim kiogora <kimkiogora@gmail.com>

script_home=[ PATH TO ]/web
script_name="$script_home/autodeployer.py"

pid_file="/var/run/autodeployer.pid"

# returns a boolean and optionally the pid
running() {
    local status=false
    if [[ -f $pid_file ]]; then
        # check to see it corresponds to the running script
        local pid=$(< "$pid_file")
        local cmdline=/proc/$pid/cmdline
        # you may need to adjust the regexp in the grep command
        if [[ -f $cmdline ]] && grep -q "$script_name" $cmdline; then
            status="true $pid"
        fi
    fi
    echo $status
}


start() {
    #isRoot()
    echo "starting $script_name"
    nohup python $script_name &
    echo $! > "$pid_file"
}

stop() {
    #isRoot()
    # `kill -0 pid` returns successfully if the pid is running, but does not
    # actually kill it.
    #if [[ -f $cmdline ]] && grep -q "$script_name" $cmdline; then
    if [ -e "$pid_file" ];then
    pidis=`ps aux | grep "$script_name" | grep -v 'grep'|awk '{print $2}'`
    echo "Killing PID $pidis">>nohup.out
    kill -9 $pidis
    #kill -0 $1 && kill $1
    rm "$pid_file"
    echo "stopped"
    echo "stopped" >> nohup.out
    else
        echo "App is not running"
    fi
}

isRoot() {
    if [ "$(id -u)" != "0" ]; then
        echo "This script must be run as root" 1>&2
        exit 1
    fi
}

read running pid < <(running)

case $1 in 
    start)
        if $running; then
            echo "$script_name is already running with PID $pid"
        else
	    isRoot
            start
        fi
        ;;
    stop)
	isRoot
        stop $pid
        ;;
    restart)
        isRoot
        stop $pid
        start
        ;;
    status)
        if $running; then
            echo "$script_name is running with PID $pid"
        else
            echo "$script_name is not running"
        fi
        ;;
    *)  echo "usage: $0 <start|stop|restart|status>"
        exit
        ;;
esac
