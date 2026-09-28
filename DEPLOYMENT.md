# Beijing server deployment

This static site is served by Nginx from `/srv/cloudsequ/current`.
Internal preview listener: `127.0.0.1:8080`; access through the authorized SSH tunnel
at `http://localhost:18080`. Public domain target: `https://cloudsequ.com`.

Navigation and canonical URLs now use the independent domain root instead of the
original GitHub Pages `/miraphant/` prefix. Existing branding/content is retained.

The first deployment is a manual artifact upload. GitHub pushes are not yet automatic
deployments. Build a release from reviewed source, upload it, and replace the served
files. Keep `.git`, operational scripts, credentials, and non-public files outside
the web root. Review employee portal authentication before exposing it publicly:
its current browser password/localStorage checks are not server-side authorization.

The FDE repository contains the Nginx preview configuration and Node/PostgreSQL setup.
Public DNS and HTTPS are pending ICP filing. Preserve all existing email DNS records.
