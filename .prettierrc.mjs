/** @type {import("prettier").Config} */
const config = {
    trailingComma: 'es5',
    tabWidth: 4,
    semi: true,
    printWidth: 120,
    singleQuote: true,
    overrides: [
        {
            files: ['*.yml', '*.yaml', '*.ansible-lint', '.ansible-lint', '*.yamllint', '.yamllint'],
            options: {
                singleQuote: false,
                parser: 'yaml',
            },
        },
    ],
};

export default config;
