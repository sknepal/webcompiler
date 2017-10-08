#!/bin/bash
proclist=`ps -eo user,etimes,pid,ppid,cmd | awk '$5 == "/usr/bin/firejail"' | awk '$1 == "try"' | awk '$2 > 600' | awk '{print $3}'`
for pid in $proclist; do
firejail --shutdown=$pid
done

