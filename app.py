import argparse
import curses
import os
import tempfile
from subprocess import call

import requests
import json

from requests import RequestException

from gupy.view import ListViewDataSource
from lib.ui import UI


class App(ListViewDataSource):

    def parseArgs(self):
        argparser = argparse.ArgumentParser(
            prog='confluent-cli',
            description='Implements an interactive CLI for the usage of the confluent REST interface'
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
            '--jdbcSource',
            help="Uses the template for a JDBC Source Connector",
            action="store_true"
        )

        argparser.add_argument(
            '--jdbcSink',
            help="Uses the template for a JDBC Sink Connector",
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

        else:
            self.__connectors = []
            ui = UI(self)
            curses.wrapper(ui.loop)

    def getConnectors(self):
        url = '%s/connectors' % self.host
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorOverview(self, connector):
        url = '%s/connectors/%s' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorStatus(self, connector):
        url = '%s/connectors/%s/status' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorTasks(self, connector):
        url = '%s/connectors/%s/tasks' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def getConnectorConfig(self, connector):
        url = '%s/connectors/%s/config' % (self.host, connector)
        response = requests.get(url)
        self.assertSuccess(response)

        return json.loads(response.text)

    def restartConnector(self, connector):
        url = '%s/connectors/%s/restart' % (self.host, connector)
        response = requests.post(url)
        self.assertSuccess(response)

    def pauseConnector(self, connector):
        url = '%s/connectors/%s/pause' % (self.host, connector)
        response = requests.put(url)
        self.assertSuccess(response)

    def resumeConnector(self, connector):
        url = '%s/connectors/%s/resume' % (self.host, connector)
        response = requests.put(url)
        self.assertSuccess(response)

    def createConnector(self, content: str):
        url = '%s/connectors' % self.host
        response = requests.post(url, json=json.loads(content))
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

        return (state, type, workerId, tasks, name)

    def refreshConnectors(self, onBegin=None, onFetchComplete=None, onLoadingBegin=None, onClomplete=None):
        self.__connectors = []
        if onBegin:
            onBegin()

        connectorIds = self.getConnectors()
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
        _, _, _, _, connector = self.__connectors[index]
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

if __name__ == '__main__':
    App()