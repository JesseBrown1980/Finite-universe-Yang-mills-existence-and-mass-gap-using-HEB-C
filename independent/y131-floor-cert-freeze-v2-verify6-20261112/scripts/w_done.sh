# w_done.sh FILE MAXSECS -- wait for a done file
i=0; while [ ! -e "$1" ] && [ $i -lt $2 ]; do sleep 5; i=$((i+5)); done; ls -la "$1" 2>&1
