import argparse
import curses
import os
import tempfile
from subprocess import call
from os import path

import requests
import json

from requests import RequestException

from gupy.view import ListViewDataSource
from lib.ui import UI


class App(ListViewDataSource):

    def parseArgs(self):
        argparser = argparse.ArgumentParser(
            prog='confluent-connect',
            description='Implements an interactive tool for the usage of the Confluent Connect REST interface.'
        )

        argparser.add_argument(
            'URL',
            help='The URL of the cluster in the format https://HOST:PORT')

        argparser.add_argument(
            '-c',
            '--create',
            help="Create a new connector with the given NAME",
            metavar='NAME'
        )

        argparser.add_argument(
            '-b',
            '--backup',
            help="Saves the configs of all connectors to a fiven destination. The file name will be the connectors name. In addition to that a file 'ACTIVE_CONNECTORS.json' will be created containing a list of all config files as a JSON array.",
            metavar='PATH'
        )

        argparser.add_argument(
            '-r',
            '--restore',
            help='Restores connectors from a list of configuration files. Per default a file containing a JSON array of the config files is expected. Use --directory to restore all config files from a given directory.',
            metavar='LIST_OR_DIRECTORY'
        )

        argparser.add_argument(
            '--directory',
            help="Restores all config files in a directory instead of a list.",
            action="store_true"
        )

        argparser.add_argument(
            '--jdbcSource',
            help="Uses the template for a JDBC Source Connector",
            action="store_true"
        )

        argparser.add_argument(
            '--jdbcSink',
            help="Uses the template for a JDBC Sink Connector",
            action="store_true"
        )

        argparser.add_argument(
            '--info',
            help="Returns the Connect Cluster information",
            action="store_true"
        )

        argparser.add_argument(
            '--plugins',
            help="Return a list of connector plugins installed in the Kafka Connect cluster",
            action="store_true"
        )

        return argparser.parse_args()

    def configFromArgs(self, args):
        config = dict()

        if args.jdbcSource:
            config['connector.class'] = 'io.confluent.connect.jdbc.JdbcSourceConnector'
            config['mode'] = 'timestamp'
            config['poll.interval.ms'] = '7200000'
            config['tasks.max'] = '1'
            config['timestamp.column.name'] = None
            config['topic.prefix'] = None
            config['connection.url'] = None
            config['query'] = None

        elif args.jdbcSink:
            config['connector.class'] = 'io.confluent.connect.jdbc.JdbcSinkConnector'
            config['auto.create'] = 'true'
            config['insert.mode'] = 'upsert'
            config['tasks.max'] = '1'
            config['pk.fields'] = None
            config['pk.mode'] = None
            config['connection.url'] = None
            config['topics'] = None

        else:
            config['connector.class'] = None
            config['tasks.max'] = '1'
            config['topics'] = None

        return config

    def __init__(self):

        args = self.parseArgs()
        self.host = args.URL

        if args.create:
            config = self.configFromArgs(args)
            self.buildConnector(args.create, config)

        elif args.restore:
            self.restoreConnectors(args.restore, args.directory)

        elif args.backup:
            self.backupConnectors(args.backup)

        elif args.info:
            self.printInfo()

        elif args.plugins:
            self.printPlugins()

        else:
            self.__connectors = []
            ui = UI(self)
            curses.wrapper(ui.loop)

    def getConnectInfos(self):
        url = '%s/' % self.host
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorPlugins(self):
        url = '%s/connector-plugins' % self.host
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectors(self):
        url = '%s/connectors' % self.host
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorOverview(self, connector: str):
        url = '%s/connectors/%s' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorStatus(self, connector: str):
        url = '%s/connectors/%s/status' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorTasks(self, connector: str):
        url = '%s/connectors/%s/tasks' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorConfig(self, connector: str):
        url = '%s/connectors/%s/config' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def restartConnector(self, connector: str):
        url = '%s/connectors/%s/restart' % (self.host, connector)
        response = requests.post(url)
        self.assertSuccess(response)

    def pauseConnector(self, connector: str):
        url = '%s/connectors/%s/pause' % (self.host, connector)
        response = requests.put(url)
        self.assertSuccess(response)

    def resumeConnector(self, connector: str):
        url = '%s/connectors/%s/resume' % (self.host, connector)
        response = requests.put(url)
        self.assertSuccess(response)

    def createConnector(self, content: str):
        url = '%s/connectors' % self.host
        response = requests.post(url, json=json.loads(content))
        self.assertSuccess(response)

    def updateConfig(self, connector: str, content: str):
        url = '%s/connectors/%s/config' % (self.host, connector)
        response = requests.put(url, json=json.loads(content))
        self.assertSuccess(response)

    def assertSuccess(self, response: requests.Response):
        if response.status_code not in range(200, 300):
            message = "\n\nRequest %s '%s' failed (%s):\n%s\n" % (response.request.method, response.url, response.status_code, response.text)
            raise RequestException(message)

    def prettyfyJson(self, aJson, sortKeys=True):
        return json.dumps(aJson, sort_keys=sortKeys, indent=4)

    def number_of_rows(self) -> int:
        return len(self.__connectors)

    def get_data(self, i) -> object:
        return self.__connectors[i]

    def getConnector(self, connectorId):
        connector = self.getConnectorStatus(connectorId)
        state = connector['connector']['state']
        workerId = connector['connector']['worker_id']
        type = connector['type']
        name = connector['name']
        tasks = len(connector['tasks'])

        config = self.getConnectorConfig(name)
        if type == 'source':
            topic = config['topic.prefix']
        else:
            topic = config['topics']

        return (state, type, workerId, tasks, topic, name)

    def refreshConnectors(self, onBegin=None, onFetchComplete=None, onLoadingBegin=None, onClomplete=None):
        self.__connectors = []
        if onBegin:
            onBegin()

        connectorIds = self.getConnectors()
        connectorIds.sort()
        if onFetchComplete:
            onFetchComplete(connectorIds)

        self.__connectors = []
        i = 1
        for connectorId in connectorIds:
            if onLoadingBegin:
                onLoadingBegin(i, len(connectorIds), connectorId)

            self.__connectors.append(self.getConnector(connectorId))
            i += 1

        if onClomplete:
            onClomplete()

    def refreshConnector(self, index):
        _, _, _, _, _, connector = self.__connectors[index]
        self.__connectors[index] = self.getConnector(connector)

    def openEditor(self, content):
        EDITOR = os.environ.get('EDITOR', 'vim')
        with tempfile.NamedTemporaryFile(suffix='.tmp', mode='w+') as tf:
            tf.write(content)
            tf.flush()
            call([EDITOR, '+set backupcopy=yes', tf.name])

            tf.seek(0)
            updatedContent = tf.read()
            updatedContent = updatedContent.strip()
            changed = updatedContent != content

            return (changed, updatedContent)

    def buildConnector(self, name, config):
        content = dict()
        content['name'] = name
        content['config'] = config

        contentJson = json.loads(json.dumps(content))
        prettyJson = self.prettyfyJson(contentJson, sortKeys=False)
        changed, updatedContent = self.openEditor(prettyJson)

        if changed:
            self.createConnector(updatedContent)

    def loadConfigFiles(self, files):
        configs = {}
        for file in files:
            with open(file) as jsonFile:
                print(f'Reading config from {file}')
                config = json.load(jsonFile)
                jsonFile.close()

                configs[file] = config

        return configs

    def loadConfigFilesFromDirectory(self, directory):
        if not path.exists(directory):
            print("No such file ore directory: '%s'" % directory)

        if not path.isdir(directory):
            print("'%s' is not a directory" % directory)

        files = [path.join(directory, f) for f in os.listdir(directory) if path.isfile(path.join(directory, f))]
        result = self.loadConfigFiles(files)

        return result

    def loadConfigFilesFromList(self, listFile):
        if not path.exists(listFile):
            print("No such file ore directory: '%s'" % listFile)

        if not path.isfile(listFile):
            print("'%s' is a directory" % listFile)

        with open(listFile) as jsonFile:
            files = json.load(jsonFile)
            jsonFile.close()

        files = [f for f in files if path.isfile(f)]
        result = self.loadConfigFiles(files)

        return result

    def transformConfigIfNecessary(self, config):
        result = config
        if 'config' not in config:
            result = dict()
            result['name'] = config['name']
            result['config'] = config

        return result

    def restoreConnectors(self, listOrDirectory, isDirectory):
        if (isDirectory):
            configs = self.loadConfigFilesFromDirectory(listOrDirectory)
        else:
            configs = self.loadConfigFilesFromList(listOrDirectory)

        print('\nRestoring Connectors...')
        for filename, config in configs.items():
            transformedConfig = self.transformConfigIfNecessary(config)
            self.createConnector(self.prettyfyJson(transformedConfig))

            print(f'Restored connector {filename}')


    def updateConnector(self, connector):
        config = self.getConnectorConfig(connector)
        config = self.prettyfyJson(config)
        changed, updatedContent = self.openEditor(config)

        if changed:
            self.updateConfig(connector, updatedContent)

    def duplicateConnector(self, connector):
        config = self.getConnectorConfig(connector)
        name = config['name']
        config.pop('name', None)

        self.buildConnector(name, config)

    def printPlugins(self):
        plugins = self.getConnectorPlugins()
        print(self.prettyfyJson(plugins))

    def printInfo(self):
        infos = self.getConnectInfos()
        print(self.prettyfyJson(infos))

    def backupConnectors(self, directory):
        if not path.exists(directory):
            print("No such file ore directory: '%s'" % directory)

        if not path.isdir(directory):
            print("'%s' is not a directory" % directory)

        connectorIds = self.getConnectors()
        connectorIds.sort()
        maxConnectorLength = len(max(connectorIds, key=len))
        configFiles = []

        for connectorId in connectorIds:
            config = self.getConnectorConfig(connectorId)

            configFileName = f'{connectorId}.json'
            configPath = path.join(directory, configFileName)
            configFile = open(configPath, 'w')
            configFile.write(self.prettyfyJson(config))
            configFile.close()

            configFiles.append(configFileName)

            print('%s  =>  %s' % (connectorId.ljust(maxConnectorLength), configPath))

        activeConnectorsFileName = 'ACTIVE_CONNECTORS.json'
        activeConnectorsPath = path.join(directory, activeConnectorsFileName)
        file = open(activeConnectorsPath, 'w')
        file.write(self.prettyfyJson(configFiles))
        file.close()

        print(f'\nA list of active connectors can be found here => {activeConnectorsPath}')

if __name__ == '__main__':
    App()