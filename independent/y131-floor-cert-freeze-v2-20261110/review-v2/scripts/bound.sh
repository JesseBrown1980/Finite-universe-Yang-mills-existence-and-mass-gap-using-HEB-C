S=/mnt/c/tmp/opus55/floor-v2-verify/scripts/reh.sh
bash $S BG_eq   --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 1042273/10000
bash $S BG_plus --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 1042274/10000
bash $S BU_eq   --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 104854118/1000000
bash $S BU_plus --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 104854119/1000000
