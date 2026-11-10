# KM — Prebuilt SMSM Runtime

This repository separates **building** SMSM from **running** it.

## First-time setup

1. Open **Settings → Secrets and variables → Actions**.
2. Add a repository secret named `SMSM_OWNER_PASSWORD`.
3. Use a strong password. Do not put it in workflow files or commits.

## Build or update the prebuilt bundle

1. Open **Actions → Build SMSM Ready Bundle**.
2. Choose the source ref (default: `feature/smsm-owner-auth`).
3. Run the workflow and wait for it to finish successfully.
4. It publishes a versioned GitHub Release containing the server, SSHX client, static web assets, and checksum.

Build again only when you want to publish a newer SMSM source version.

## Start SMSM

1. Open **Actions → KM SMSM Runtime**.
2. Run the workflow.
3. Open the run's **Summary** to find the Web interface and SSHX session links.

The runtime downloads the latest release bundle, verifies its SHA-256 checksum, and starts it without compiling Rust or rebuilding the web interface.

## Important notes

- The source remains in `Abbas2487248/smsm`; this repository stores workflows and release bundles.
- This workflow targets GitHub's `ubuntu-latest` x86_64 runner.
- This repository is currently public, so release binaries and assets are publicly downloadable. Keep the owner password in repository Actions secrets only.
- GitHub-hosted runners are temporary. Each runtime run lasts at most 350 minutes.
- The `uploads/` directory is temporary runner storage, not permanent backup storage.
- The SSHX session URL contains an access key. Treat it as a password and do not share it publicly.
