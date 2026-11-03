# prints: --r HEX --k0 HEX --k1 HEX, drawn from the OS
python3 -I -X utf8 -c "import secrets; r=secrets.randbelow((1<<127)-1); print('--r %x --k0 %x --k1 %x' % (r, secrets.randbits(64), secrets.randbits(64)))"
