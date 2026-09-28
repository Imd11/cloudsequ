#!/usr/bin/env python3
"""Publish the fetched main commit using this Mac's private SSH deployment key."""
import os, pathlib, shlex, subprocess, tempfile, urllib.request
REPO = pathlib.Path(__file__).resolve().parents[1]
SITE = "cloudsequ"
DOMAIN = "cloudsequ.com"
def run(args, **kw):
    return subprocess.run(args, check=True, **kw)
def output(args):
    return subprocess.check_output(args, text=True).strip()
os.chdir(REPO)
if output(["git", "status", "--porcelain"]):
    raise SystemExit("Working tree has changes. Commit/review them before publishing main.")
run(["git", "fetch", "origin", "main"])
sha = output(["git", "rev-parse", "refs/remotes/origin/main"])
access = REPO.parent / "server-access"
key = pathlib.Path(os.environ.get("DEPLOY_SSH_KEY", str(access / "cloudsequ-beijing")))
hosts = pathlib.Path(os.environ.get("DEPLOY_KNOWN_HOSTS", str(access / "known_hosts")))
if not key.is_file() or not hosts.is_file():
    raise SystemExit("Set DEPLOY_SSH_KEY and DEPLOY_KNOWN_HOSTS to approved private local files.")
host = os.environ.get("DEPLOY_HOST", "admin@47.93.39.219")
options = ["-i", str(key), "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=" + str(hosts)]
def ssh(command):
    return run(["ssh", *options, host, command])
remote = output(["ssh", *options, host, "mktemp -d /tmp/website-release.XXXXXXXX"])
# mktemp output is used only after strict validation.
if not remote.startswith("/tmp/website-release.") or not remote.replace("/", "").replace(".", "").replace("-", "").isalnum():
    raise SystemExit("Unexpected remote staging path")
print(f"Publishing {SITE}: main {sha}", flush=True)
try:
    with tempfile.TemporaryDirectory(prefix="website-release-") as tmp:
        archive = pathlib.Path(tmp) / "source.tar.gz"
        run(["git", "archive", "--format=tar.gz", "-o", str(archive), sha])
        # Use the release operator from the same fixed main revision.
        operator = pathlib.Path(tmp) / "release.sh"
        operator.write_bytes(subprocess.check_output(["git", "show", sha + ":scripts/release.sh"]))
        run(["scp", *options, str(archive), str(operator), host + ":" + remote + "/"])
        ssh("bash " + shlex.quote(remote + "/release.sh") + " " + " ".join(map(shlex.quote, [SITE, DOMAIN, sha, remote])))
    with urllib.request.urlopen("https://" + DOMAIN + "/", timeout=30) as response:
        if response.status != 200:
            raise SystemExit(f"Public HTTPS returned {response.status}; inspect the deployed version.")
    print(f"Verified public HTTPS: https://{DOMAIN}/ — {sha}", flush=True)
finally:
    ssh("rm -rf -- " + shlex.quote(remote))
