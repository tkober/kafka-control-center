import curses
import requests
import json

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
        r = requests.get(url)

        return json.loads(r.text)

    def getConnectorOverview(self, connector):
        url = '%s/connectors/%s' % (self.host, connector)
        r = requests.get(url)

        return json.loads(r.text)

    def getConnectorStatus(self, connector):
        url = '%s/connectors/%s/status' % (self.host, connector)
        r = requests.get(url)

        return json.loads(r.text)

    def getConnectorTasks(self, connector):
        url = '%s/connectors/%s/tasks' % (self.host, connector)
        r = requests.get(url)

        return json.loads(r.text)

    def getConnectorConfig(self, connector):
        url = '%s/connectors/%s/config' % (self.host, connector)
        r = requests.get(url)

        return json.loads(r.text)

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

    def refreshConnectors(self):
        self.__connectors = []

        connectorIds = self.getConnectors()
        self.__connectors = [ self.getConnector(connectorId) for connectorId in connectorIds ]




if __name__ == '__main__':
    host = 'http://172.20.3.207:31096'

    App(host)