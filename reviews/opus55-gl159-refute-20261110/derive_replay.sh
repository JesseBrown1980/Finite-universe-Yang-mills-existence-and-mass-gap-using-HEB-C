rm -rf /root/gl159/dv && mkdir -p /root/gl159/dv && cd /root/gl159/dv
git -C /root/gl159/repo worktree add -f /root/gl159/dv/wt 32ebe74 >/dev/null 2>&1
cd /root/gl159/dv/wt/independent/global-lock-20261110/measure
cp MEASURE-GLOBAL-LOCK.hbp /tmp/m32.hbp
python3 -I gl_derive.py measure > /dev/null; echo "measure exit=$?"
cmp MEASURE-GLOBAL-LOCK.hbp /tmp/m32.hbp && echo MEASURE_BLOCK_BYTE_IDENTICAL_32ebe74
tail -1 MEASURE-GLOBAL-LOCK.hbp
git -C /root/gl159/dv/wt checkout -q b3eeca0 -- independent/global-lock-20261110/measure/gl_derive.py
python3 -I gl_derive.py compare > /dev/null; echo "compare exit=$?"
diff MEASURE-GLOBAL-LOCK.hbp <(git -C /root/gl159/repo show b3eeca0:independent/global-lock-20261110/measure/MEASURE-GLOBAL-LOCK.hbp) && echo VERDICT_FILE_BYTE_IDENTICAL_b3eeca0
sha256sum MEASURE-GLOBAL-LOCK.hbp; cat MEASURE-GLOBAL-LOCK.hbp.sha256
git -C /root/gl159/repo show b3eeca0:independent/global-lock-20261110/measure/MEASURE-GLOBAL-LOCK.hbp.sha256
