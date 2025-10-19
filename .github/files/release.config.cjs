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
                    'uv version ${nextRelease.version}',
                    'uv export --format requirements.txt --no-hashes -o requirements.txt',
                    'uv export --format requirements.txt --no-hashes --extra dev -o requirements-dev.txt',
                    'uv build',
                    `uv publish --index test-pypi --token ${process.env.PYPI_TEST_API_TOKEN}`,
                ].join(' && '),
                successCmd: `uv publish --index pypi --token ${process.env.PYPI_PROD_API_TOKEN}`,
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
        [
            '@semantic-release/github',
            {
                assets: [{ path: 'dist/*.whl', label: 'Wheel', path: 'dist/*.tar.gz', label: 'Source' }],
            },
        ],
    ],
};
