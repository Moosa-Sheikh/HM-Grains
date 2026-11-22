# HM Grains website

Static, WordPress-free copy of the public HM Grains website. The main pages are `/`, `/about/`, and `/contact/`. The published `/hello-world/` post is also preserved for existing links.

## Development

Run `python3 -m http.server 8000` from this directory and visit `http://localhost:8000`.

## Deployment

Create a GitHub repository and push this folder to its `main` branch. In **GitHub → repository Settings → Secrets and variables → Actions**, create `HOSTINGER_FTP_SERVER`, `HOSTINGER_FTP_USERNAME`, and `HOSTINGER_FTP_PASSWORD` from the FTP account in Hostinger hPanel. The included GitHub Actions workflow deploys on pushes to `main` (and can be run manually). It expects Hostinger FTPS and `/public_html/`; change these in `.github/workflows/deploy.yml` if your hosting account uses a different protocol/path.

Before switching the live domain, back up the WordPress installation and database, verify the deployed site and form, and remove the WordPress files from `public_html` so its old routing does not override these static pages. The deployment action transfers the files in this repo; it does not remove unrelated files from the server. Keep PHP enabled for `contact/submit.php` and confirm Hostinger's outbound mail delivery works. Set `HM_CONTACT_TO` in the server environment to change the recipient from `contact@hmgrains.com`.

The static pages and assets are committed to the repository. WordPress is not required to serve them.

To refresh a public-page snapshot deliberately, run `python3 scripts/snapshot.py` and review the resulting diff. This script downloads the public site; it is **not** run by the deployment workflow.
