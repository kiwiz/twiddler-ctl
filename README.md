# twiddler-ctl

A CLI tool to manage Twiddler (v7) configurations

## Features

* Converting between binary (`.cfg`) files and a text-based format
* Support for alternative keyboard layouts
* Syncing a set of configuration files to the Twiddler
* (WIP) [Untethered Re-Chording Mode](https://www.mytwiddler.com/doc/doku.php?id=t4_datalogger) datalog encoding/decoding
* (WIP) Chord visualizations

## Installation

Install with `pipx` or `pip`:

```bash
pipx install twiddler-ctl
```

## Usage

### Manipulating configuration files

**To Text**:

```bash
twiddler-ctl convert input.cfg output.txt
```

**To Binary**:

```bash
twiddler-ctl convert input.txt output.cfg
```


### Visualize configuration file

```bash
twiddler-ctl visualize input.cfg
```


### Sync configurations

* Copy `config.sample.ini` and rename to `config.ini`
* Update the file to point to your Twiddler
* Sync configs with `twiddler-ctl sync`


### Print valid keys

```bash
twiddler-ctl dump --table=keys
```


### Manipulating Untethered Re-Chording Mode datalog files

**Encoding**:

```bash
twiddler-ctl convert-log input.txt output.log
```

**Decoding**:

```bash
twiddler-ctl convert-log input.log output.txt
```
