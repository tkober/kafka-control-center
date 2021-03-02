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

    def __init__(self, host):
        self.host = host

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

    def assertSuccess(self, response: requests.Response):
        if response.status_code not in range(200, 300):
            message = "\nRequest %s '%s' failed (%s):\n%s" % (response.request.method, response.url, response.status_code, response.text)
            raise RequestException(message)

    def prettyfyJson(self, aJson):
        return json.dumps(aJson, sort_keys=True, indent=4)

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




if __name__ == '__main__':
    host = 'http://172.20.3.207:31096'

    App(host)