# Puts one group of Perron files on the store's Hugging Face dataset as one commit, then checks size and LFS SHA-256
# from the Hub against the local files. The token comes only from the environment and is never printed or saved.
# usage: hf_push_perron.py GROUP LOCAL=REPO_PATH [LOCAL=REPO_PATH ...]
# Prints HF_FILE rows and one HF_COMMIT row. json=0.
import hashlib, os, sys

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
from huggingface_hub import CommitOperationAdd, HfApi

REPO = "Jessedbrown/ym-3x4-room-store"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


group = sys.argv[1]
pairs = [a.split("=", 1) for a in sys.argv[2:]]
assert pairs, "no files"
local = {r: (l, os.path.getsize(l), sha(l)) for l, r in pairs}
api = HfApi(token=os.environ["HF_TOKEN"])
ops = [CommitOperationAdd(path_in_repo=r, path_or_fileobj=l) for l, r in pairs]
c = api.create_commit(repo_id=REPO, repo_type="dataset", operations=ops, commit_message=f"perron: {group}")
oid = c.oid
info = api.dataset_info(REPO, revision=oid, files_metadata=True)
hub = {s.rfilename: s for s in info.siblings}
good = 0
for r, (l, size, want) in local.items():
    s = hub.get(r)
    assert s is not None, f"{r} not on the Hub"
    got = s.lfs.sha256 if s.lfs is not None else None
    # Files under the LFS threshold carry only a blob id, so their bytes are checked by reading them back.
    if got is None:
        back = api.hf_hub_download(repo_id=REPO, repo_type="dataset", filename=r, revision=oid)
        got = sha(back)
    assert s.size == size and got == want, (r, s.size, size, got, want)
    good += 1
    print(f"HF_FILE|group={group}|path={r}|bytes={size}|sha256={want}|hub_match=1|json=0")
print(f"HF_COMMIT|group={group}|repo=datasets/{REPO}|commit={oid}|files={good}|all_match=1|json=0")
