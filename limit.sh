#!/bin/bash
proclist=`ps -eo user,etimes,pid,ppid,cmd | grep -v "defunct" | grep -v "ssh" | grep -v  "firejail" | grep -v "tail" | grep -v "/usr/bin/python" | grep -v "app.py" |  grep -v "vi" | grep -v "bash" | grep -v "tmux" | awk '$1 == "try"' | awk '$2 > 30' | awk '{print $3}'`
for pid in $proclist; do
kill -9 $pid
done
