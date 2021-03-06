# confluent-connect

This tool implements an interactive command line tool for working with the Confluent Connect [REST interface](https://docs.confluent.io/platform/current/connect/references/restapi.html).
![image](doc/screenshot.png)

## Prerequireties

In order do install or run this tool make sure either PIP or Anaconda is installed and available on your bash.

## Cloning

This repo contains git submodules. Remember to initialize these by running

```
git submodule init
git submodule update --remote
```


## Install

The repository's root directory contains a bash script for installation.

`bash install.sh`

#### Caution

Some packages will be installed during the installation. If anaconda is available a seperate environment will be created. If Anaconda is not found PIP will be used instead. This could lead to overwriting existing packages or versions. The usage of Anaconda is highly recommended. You can get it [here](https://www.anaconda.com/).

### Run

After installation _sg-translations_ is available in your bash using the following command:

```
confluent-connect [-h] [-c NAME] [-b PATH] [--jdbcSource] [--jdbcSink] [--info] [--plugins] URL
```

If no path is provided the current directory will be used.

### --help
```
usage: confluent-connect [-h] [-c NAME] [-b PATH] [--jdbcSource] [--jdbcSink] [--info] [--plugins] URL

Implements an interactive tool for the usage of the Confluent Connect REST interface.

positional arguments:
  URL                   The URL of the cluster in the format https://HOST:PORT

optional arguments:
  -h, --help            show this help message and exit
  -c NAME, --create NAME
                        Create a new connector with the given NAME
  -b PATH, --backup PATH
                        Saves the configs of all connectors to a fiven destination. The file name will be the connectors name.
  --jdbcSource          Uses the template for a JDBC Source Connector
  --jdbcSink            Uses the template for a JDBC Sink Connector
  --info                Returns the Connect Cluster information
  --plugins             Return a list of connector plugins installed in the Kafka Connect cluster
```