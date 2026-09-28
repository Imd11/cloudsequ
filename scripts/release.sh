#!/usr/bin/env bash
set -euo pipefail
site=$1 domain=$2 sha=$3 stage=$4
[[ "$sha" =~ ^[a-f0-9]{40}$ ]]
case "$site:$domain" in fde:fde.cloudsequ.com|cloudsequ:cloudsequ.com) ;; *) exit 2;; esac
mkdir "$stage/source" "$stage/artifact"
tar -xzf "$stage/source.tar.gz" -C "$stage/source"
if [[ "$site" == fde ]]; then
  cd "$stage/source"
  export PATH=/opt/node24/bin:$PATH
  npm ci --no-audit --no-fund
  npx tsc --noEmit
  npm run build:server
  cp -a dist/standalone/. "$stage/artifact/"
else
  # Explicit public asset types; never publish Git, docs, scripts or private files.
  python3 - "$stage/source" "$stage/artifact" <<'PYASSETS'
import pathlib, shutil, sys
src, dst = map(pathlib.Path, sys.argv[1:])
allowed = {'.html','.css','.js','.json','.svg','.png','.jpg','.jpeg','.webp','.gif','.ico','.woff','.woff2','.ttf','.pdf','.mp4','.webm'}
for p in src.rglob('*'):
    rel = p.relative_to(src)
    if any(x.startswith('.') for x in rel.parts) or rel.parts[0] in {'docs','scripts','deploy'}:
        continue
    if p.is_file() and p.suffix.lower() in allowed:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
assert (dst/'index.html').is_file()
PYASSETS
fi
sudo bash -s -- "$site" "$domain" "$sha" "$stage" <<'ROOT'
set -euo pipefail
site=$1 domain=$2 sha=$3 stage=$4
exec 9>"/run/lock/$site-deploy.lock"
flock -n 9 || { echo 'Another release is active'; exit 1; }
base=/srv/$site
stamp=$(date -u +%Y%m%dT%H%M%SZ)-$$
release=$base/releases/$sha-$stamp
backup=/var/backups/$site/$stamp
install -d -m 755 "$base/releases"
install -d -m 700 "$backup"
if [[ "$site" == fde ]]; then
  sudo -u postgres pg_dump -Fc fde > "$backup/database.dump"
  pg_restore -l "$backup/database.dump" > "$backup/database.contents"
  sha256sum "$backup/database.dump" > "$backup/database.sha256"
  cp /etc/systemd/system/fde.service "$backup/"
fi
cp /etc/nginx/conf.d/cloudsequ-public.conf "$backup/"
mkdir "$release"
cp -a "$stage/artifact/." "$release/"
chown -R root:root "$release"
chmod -R a+rX "$release"
printf '%s\n' "$sha" > "$release/.deployed-sha"
# Convert the original directory deployment once; retain it for rollback.
if [[ ! -L "$base/current" ]]; then
  mv "$base/current" "$base/releases/legacy-$stamp"
  ln -s "$base/releases/legacy-$stamp" "$base/current"
fi
previous=$(readlink -f "$base/current")
printf '%s\n' "$previous" > "$backup/previous-release"
switch_to() {
  ln -s "$1" "$base/.next-$stamp"
  mv -Tf "$base/.next-$stamp" "$base/current"
}
rollback() {
  trap - ERR
  echo 'Release failed; restoring previous application version.' >&2
  switch_to "$previous"
  if [[ "$site" == fde ]]; then systemctl restart fde; fi
  exit 1
}
trap rollback ERR
switch_to "$release"
if [[ "$site" == fde ]]; then systemctl restart fde; fi
curl --fail --silent --show-error --retry 12 --retry-connrefused --retry-delay 2 --max-time 10 \
  --resolve "$domain:443:127.0.0.1" "https://$domain/" -o /dev/null
if [[ "$site" == fde ]]; then
  # This endpoint must be reachable and reject unsupported form content.
  code=$(curl --silent --show-error --resolve "$domain:443:127.0.0.1" \
    -X POST -H "Origin: https://$domain" -H 'Content-Type: text/plain' \
    -o /dev/null -w '%{http_code}' "https://$domain/api/requirements")
  [[ "$code" == 415 ]]
fi
trap - ERR
printf 'DEPLOYED %s %s\nBACKUP %s\nPREVIOUS %s\n' "$site" "$sha" "$backup" "$previous"
ROOT
