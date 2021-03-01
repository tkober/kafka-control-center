import curses
import requests
import json
from tqdm import tqdm

from gupy.view import ListViewDataSource
from lib.ui import UI


class App(ListViewDataSource):

    def __init__(self, host):
        self.host = host

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



if __name__ == '__main__':
    host = 'http://172.20.3.207:31096'

#    print('loading connectors...')
#    connectorIds = getConnectors(host)

#    connectors = dict()
#    for i in tqdm(range(len(connectorIds))):
#        connectorId = connectorIds[i]
#        connector = getConnectorStatus(host, connectorId)
#        connectors[connectorId] = connector

    App(host)