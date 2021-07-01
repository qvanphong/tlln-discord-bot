. env/bin/active
nohup python3 -u selfbot.py > nohup.out 2>&1 &
echo $! > save_pid.txt