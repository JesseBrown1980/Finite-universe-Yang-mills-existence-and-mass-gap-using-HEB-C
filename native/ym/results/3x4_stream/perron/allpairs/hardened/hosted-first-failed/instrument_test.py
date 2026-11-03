import os, subprocess, sys
LAUNCHER = "import os,sys\npid=os.fork()\nif pid==0:\n    os.execv(sys.argv[2],sys.argv[2:])\n_,st,ru=os.wait4(pid,0)\nopen(sys.argv[1],'w').write('%d %d'%(ru.ru_maxrss*1024,os.waitstatus_to_exitcode(st)))\n"
RES = "/tmp/instrument-res.txt"
big = bytes(range(256)) * (600 * 4096)
print("parent_holds_bytes=%d" % len(big))
p = subprocess.Popen(["/bin/true"])
_, st, ru = os.wait4(p.pid, 0)
print("INSTRUMENT|direct_from_big_parent|cmd=bin_true|peak_bytes=%d|json=0" % (ru.ru_maxrss * 1024))
subprocess.run([sys.executable, "-I", "-S", "-c", LAUNCHER, RES, "/bin/true"], check=True)
print("INSTRUMENT|through_small_launcher|cmd=bin_true|peak_and_exit=%s|json=0" % open(RES).read())
subprocess.run([sys.executable, "-I", "-S", "-c", LAUNCHER, RES, sys.executable, "-I", "-S", "-c", "b=bytes(range(256))*(300*4096);print(len(b))"], check=True, stdout=subprocess.DEVNULL)
print("INSTRUMENT|through_small_launcher|cmd=child_touching_300MiB|peak_and_exit=%s|json=0" % open(RES).read())
os.remove(RES)
