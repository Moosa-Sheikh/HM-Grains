# HM Grains website

Static, WordPress-free copy of the public HM Grains website. The main pages are `/`, `/about/`, and `/contact/`. The published `/hello-world/` post is also preserved for existing links.

## Development

Run `python3 -m http.server 8000` from this directory and visit `http://localhost:8000`.

## Deployment

The repository is [Moosa-Sheikh/HM-Grains](https://github.com/Moosa-Sheikh/HM-Grains). GitHub Actions secrets `HOSTINGER_FTP_SERVER`, `HOSTINGER_FTP_USERNAME`, and `HOSTINGER_FTP_PASSWORD` are configured for the dedicated staging-site FTP account on Hostinger's Unlimited plan. The workflow deploys on pushes to `main` (and can be run manually) using FTPS. This FTP account is already rooted at its own `public_html`, so `server-dir` is `./`.

The staging site is `blissful-lightgreen-jay-31.hostingersite.com` on Unlimited Web Hosting. Before switching the live domain, back up the WordPress installation and database, verify the deployed site and form, and move `hmgrains.com` to the staging site. The deployment action transfers the files in this repo; it does not remove unrelated files from the server. Keep PHP enabled for `contact/submit.php` and confirm Hostinger's outbound mail delivery works. Set `HM_CONTACT_TO` in the server environment to change the recipient from `contact@hmgrains.com`.

The static pages and assets are committed to the repository. WordPress is not required to serve them.

To refresh a public-page snapshot deliberately, run `python3 scripts/snapshot.py` and review the resulting diff. This script downloads the public site; it is **not** run by the deployment workflow.
