# Contributing

This is a community template — contributions are welcome.

## How to Contribute

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## What to Contribute

- **New tools**: Add a CLI-based research tool to the scaffold
- **Makefile targets**: New workflow shortcuts
- **Documentation**: Improve or expand tool docs in `docs/`
- **Templates**: Better note/manuscript/outline templates
- **Bug fixes**: Broken scripts, incorrect install commands

## Adding a New Tool

1. Add install instructions to `setup.sh`
2. Add Python packages to `requirements.txt` (if applicable)
3. Create or update the relevant file in `docs/` (organized by workflow stage)
4. Add a Makefile target if the tool has common CLI commands
5. Update the toolkit table in `README.md`

## Standards

- Shell scripts: `#!/usr/bin/env bash`, `set -euo pipefail`, pass `shellcheck`
- Keep everything CLI-first — no GUI dependencies
- All tools must be free (paid tiers are fine, but free tier must be functional)
- Test on both macOS and Linux when possible
