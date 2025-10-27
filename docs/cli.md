# `bitwarden-exporter`

Bitwarden Exporter CLI

**Usage**:

```console
$ bitwarden-exporter [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show the application&#x27;s version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `keepass`: Export Bitwarden data to KDBX file.

## `bitwarden-exporter keepass`

Export Bitwarden data to KDBX file.

**Usage**:

```console
$ bitwarden-exporter keepass [OPTIONS]
```

**Options**:

* `--export-location TEXT`: Bitwarden Export Location  [default: (bitwarden_dump_&lt;timestamp&gt;.kdbx)]
* `--export-password TEXT`: Direct value: --export-password &quot;my-secret-password&quot;.
From a file: --export-password file:secret.txt.
From environment: --export-password env:SECRET_PASSWORD.
From vault (JMESPath expression): --export-password &quot;jmespath:[?id==&#x27;xx-xx-xx-xxx-xxx&#x27;].fields[] | [?name==&#x27;export-password&#x27;].value&quot;.  [required]
* `--allow-duplicates / --no-allow-duplicates`: Allow duplicates entries in export, In bitwarden each item can be in multiple collections,  [default: no-allow-duplicates]
* `--tmp-dir TEXT`: Temporary directory to store temporary sensitive files.  [default: (Temporary directory)]
* `--bw-executable TEXT`: Path to the Bitwarden CLI executable.  [default: bw]
* `--debug / --no-debug`: Enable verbose logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,
This will not delete the temporary directory after the export.  [default: no-debug]
* `--help`: Show this message and exit.
