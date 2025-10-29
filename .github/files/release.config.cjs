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
                    'README_VERSION_NEXT=${nextRelease.version} uv run .github/files/readme_gen.py',
                    'uv version ${nextRelease.version}',
                    'uv export --format requirements.txt --no-hashes -o requirements.txt',
                    'uv export --format requirements.txt --no-hashes --extra dev -o requirements-dev.txt',
                    'uv build',
                    'uv run typer src/bitwarden_exporter/__main__.py utils docs --output docs/cli.md',
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
                assets: [
                    'CHANGELOG.md',
                    'pyproject.toml',
                    'uv.lock',
                    'requirements.txt',
                    'requirements-dev.txt',
                    'docs/cli.md',
                    'README.md',
                ],
                message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
            },
        ],
        // [
        //     '@semantic-release/github',
        //     {
        //         assets: [
        //             {
        //                 path: 'dist/bitwarden_exporter-*-py3-none-any.whl',
        //                 label: 'bitwarden_exporter-py3-none-any.whl',
        //             },
        //             { path: 'dist/bitwarden_exporter-*.tar.gz', label: 'bitwarden_exporter.tar.gz' },
        //         ],
        //     },
        // ],
    ],
};
