export PATH="$HOME/.cargo/bin:$PATH"
cd /root/floor-v2/repo
git log --format='%H %P %an <%ae>%n%B---' -3
git status --short | head
git diff --stat e74d8a46 3b91d1a0 | tail -5
git diff --stat cfc57bef 3b91d1a0
