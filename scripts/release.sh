#!/usr/bin/env bash
# Prepare a release: write the version into every file that carries it, commit, and tag.
# Pushing the tag starts .github/workflows/release.yml, which creates the GitHub release and publishes to PyPI.
#
# Usage: scripts/release.sh <version>      e.g. scripts/release.sh 1.11.0

set -euo pipefail

usage() {
    echo "Usage: $0 <version>   (semantic version without a leading v, e.g. 1.11.0 or 1.11.0-rc.1)" >&2
    exit 1
}

[[ $# -eq 1 ]] || usage
version="$1"
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$'
[[ "$version" =~ $semver_re ]] || usage

cd "$(git rev-parse --show-toplevel)"

branch="$(git branch --show-current)"
[[ "$branch" == "main" ]] || {
    echo "Releases are cut from main, not '${branch}'." >&2
    exit 1
}
[[ -z "$(git status --porcelain)" ]] || {
    echo "The working tree has uncommitted changes; commit or stash them first." >&2
    exit 1
}
if git rev-parse --quiet --verify "refs/tags/${version}" > /dev/null; then
    echo "Tag ${version} already exists." >&2
    exit 1
fi

current="$(uv version --short --no-progress)"
echo "Bumping ${current} -> ${version}"

uv version --no-progress "${version}"

uv sync --extra dev --locked --no-progress
uv run --no-progress typer src/bitwarden_exporter/__main__.py utils docs --output docs/cli.md

git add pyproject.toml uv.lock docs/cli.md
git commit -m "chore(release): ${version}"
git tag "${version}"

echo
echo "Created commit and tag ${version}. Review with 'git show ${version}', then publish with:"
echo "    git push origin main ${version}"
