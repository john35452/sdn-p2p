rm user*
rm *answer.txt
cd experiment
rm Config -r
rm Log -r
rm PID -r
rm Host_Local_Storage -r
rm NewTorrent -r
killall deluged
killall python
