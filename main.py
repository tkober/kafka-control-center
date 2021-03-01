import requests
import json
from tqdm import tqdm

def getConnectors(host):
    url = '%s/connectors' % host
    r = requests.get(url)

    return json.loads(r.text)

def getConnectorOverview(host, connector):
    url = '%s/connectors/%s' % (host, connector)
    r = requests.get(url)

    return json.loads(r.text)

def getConnectorStatus(host, connector):
    url = '%s/connectors/%s/status' % (host, connector)
    r = requests.get(url)

    return json.loads(r.text)

def getConnectorTasks(host, connector):
    url = '%s/connectors/%s/tasks' % (host, connector)
    r = requests.get(url)

    return json.loads(r.text)

def getConnectorConfig(host, connector):
    url = '%s/connectors/%s/config' % (host, connector)
    r = requests.get(url)

    return json.loads(r.text)

def prettyfyJson(aJson):
    return json.dumps(aJson, sort_keys=True, indent=4)


if __name__ == '__main__':
    host = 'http://172.20.3.207:31096'

    print('loading connectors...')
    connectorIds = getConnectors(host)

    connectors = dict()
    for i in tqdm(range(len(connectorIds))):
        connectorId = connectorIds[i]
        #connector = getConnectorStatus(host, connectorId)
        #connectors[connectorId] = connector

    print('\n\nStatus')
    print(prettyfyJson(getConnectorStatus(host, connectorIds[0])))

    print('\n\nOverview')
    print(prettyfyJson(getConnectorOverview(host, connectorIds[0])))

    print('\n\nTasks')
    print(prettyfyJson(getConnectorTasks(host, connectorIds[0])))

    print('\n\nConfig')
    print(prettyfyJson(getConnectorConfig(host, connectorIds[0])))