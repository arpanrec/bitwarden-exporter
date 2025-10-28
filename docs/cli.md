# `bitwarden-exporter`

Bitwarden Exporter CLI

**Usage**:

```console
$ bitwarden-exporter [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...
```

**Options**:

* `-v, --version`: Show the application&#x27;s version and exit.
* `--debug / --no-debug`: Enable verbose logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,
This will not delete the temporary directory after the export.  [default: no-debug]
* `--tmp-dir TEXT`: Temporary directory to store temporary sensitive files.  [default: (Temporary directory)]
* `--bw TEXT`: Path or command name of the Bitwarden CLI executable.  [default: bw]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `export`: Select the exporter to use

## `bitwarden-exporter export`

Select the exporter to use

**Usage**:

```console
$ bitwarden-exporter export [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `keepass`: Export Bitwarden data to KDBX file.

### `bitwarden-exporter export keepass`

Export Bitwarden data to KDBX file.

**Usage**:

```console
$ bitwarden-exporter export keepass [OPTIONS]
```

**Options**:

* `-p, --kdbx-password TEXT`: Direct value: --kdbx-password &quot;my-secret-password&quot;.
From a file: --kdbx-password file:secret.txt.
From environment: --kdbx-password env:SECRET_PASSWORD.
From vault (JMESPath expression): --kdbx-password &quot;jmespath:[?id==&#x27;xx-xx-xx-xxx-xxx&#x27;].fields[] | [?name==&#x27;export-password&#x27;].value&quot;.  [required]
* `-k, --kdbx-file TEXT`: Bitwarden Export Location  [default: (bitwarden_dump_&lt;timestamp&gt;.kdbx)]
* `--help`: Show this message and exit.
