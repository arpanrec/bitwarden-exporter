module.exports = {
    branches: ['main'],
    tagFormat: '${version}',
    plugins: [
        [
            '@semantic-release/commit-analyzer',
            {
                preset: 'angular',
                parserOpts: {
                    noteKeywords: ['BREAKING CHANGE', 'BREAKING CHANGES', 'BREAKING'],
                },
            },
        ],
        [
            '@semantic-release/release-notes-generator',
            {
                preset: 'angular',
                parserOpts: {
                    noteKeywords: ['BREAKING CHANGE', 'BREAKING CHANGES', 'BREAKING'],
                },
                writerOpts: {
                    commitsSort: ['subject', 'scope'],
                },
            },
        ],
        [
            '@semantic-release/exec',
            {
                prepareCmd: [
                    'rm -f CHANGELOG.md',
                    'uv version ${nextRelease.version}',
                    'uv export --format requirements.txt --no-hashes -o requirements.txt',
                    'uv export --format requirements.txt --no-hashes --extra dev -o requirements-dev.txt',
                    'uv build',
                    'uv publish --index test-pypi',
                ].join(' && '),
                successCmd: 'uv publish --index pypi',
            },
        ],
        [
            '@semantic-release/changelog',
            {
                changelogFile: 'CHANGELOG.md',
            },
        ],
        [
            '@semantic-release/git',
            {
                assets: ['CHANGELOG.md', 'pyproject.toml', 'uv.lock', 'requirements.txt', 'requirements-dev.txt'],
                message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
            },
        ],
    ],
};
