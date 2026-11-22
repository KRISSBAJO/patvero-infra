# Patvero bare-domain app links

The public website remains on Amplify at `www.patvero.com`. The existing API host serves `patvero.com` through a separate Caddy virtual host. Only the two public association documents are proxied to the canonical website; credentials and cookies are removed. Other paths receive an HTTPS redirect preserving the path and query. No API release, database, media route, service port or name-server migration is required.

Before changing DNS, export the GoDaddy zone and retain the existing forwarding settings. Check the API health, review the current Caddy configuration, copy the site and installer to the existing host, and run the installer as root. It validates the combined configuration using the installed Caddy version, creates a protected backup, and hot-reloads Caddy. The existing API block is preserved.

Remove only the bare-domain GoDaddy forwarding entry, then point the bare-domain A record to the existing API host. Preserve `api`, `livekit`, `turn`, `www`, ACM validation, mail records, nameservers and DNSSEC. Caddy issues and renews the apex certificate using its existing certificate storage and custody. Never copy certificate private keys into the repository.

Verify authoritative DNS, API health, a trusted apex certificate, HTTP-to-HTTPS behavior, JSON with HTTP 200 and no redirect on both apex association paths, the Google Digital Asset Links relationship, and a redirect preserving a meeting path and invitation query. Existing resolver caches may retain the prior records for their original TTL; record observation times and distinguish deployed from globally propagated.

Rollback: restore the exact forwarding settings and apex DNS records from the zone backup. Restore `/etc/caddy/Caddyfile` from the installer's reported protected backup, validate with Caddy, and hot-reload. Remove only this new site import/file after the original configuration is active. No application or database rollback is involved.
