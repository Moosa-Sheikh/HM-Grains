# HM Grains website

Static, WordPress-free copy of the public HM Grains website. The main pages are `/`, `/about/`, and `/contact/`. The published `/hello-world/` post is also preserved for existing links.

## Development

Run `python3 -m http.server 8000` from this directory and visit `http://localhost:8000`.

## Deployment

The repository is [Moosa-Sheikh/HM-Grains](https://github.com/Moosa-Sheikh/HM-Grains). GitHub Actions secrets `HOSTINGER_FTP_SERVER`, `HOSTINGER_FTP_USERNAME`, and `HOSTINGER_FTP_PASSWORD` are configured for the dedicated staging-site FTP account on Hostinger's Unlimited plan. The workflow deploys on pushes to `main` (and can be run manually) using FTPS. This FTP account is already rooted at its own `public_html`, so `server-dir` is `./`.

The staging site is `sweet-goldenrod-camel-25.hostingersite.com` on Unlimited Web Hosting. The live `hmgrains.com` domain currently remains assigned to the old WordPress website on the Cloud Professional plan until the Cloudflare DNS zone can be updated. When cutting over, point Cloudflare's apex A record to the Unlimited site's IP (`82.29.199.46`), ensure `www` resolves to the same site, and move the domain in Hostinger from the WordPress site to this PHP/HTML site. The deployment action transfers the files in this repo; it does not remove unrelated files from the server. Keep PHP enabled for `contact/submit.php` and confirm Hostinger's outbound mail delivery works. Set `HM_CONTACT_TO` in the server environment to change the recipient from `contact@hmgrains.com`.

The static pages and assets are committed to the repository. WordPress is not required to serve them.

To refresh a public-page snapshot deliberately, run `python3 scripts/snapshot.py` and review the resulting diff. This script downloads the public site; it is **not** run by the deployment workflow.
