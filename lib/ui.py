import subprocess
import platform

from gupy.geometry import Padding
from gupy.view import BackgroundView, Label, HBox, ListView, ListViewDelegate, View
from gupy.screen import ConstrainedBasedScreen
from enum import Enum
import curses

from lib import colorpairs, legends, keys
from lib.document import Document


class Mode(Enum):
    CONNECTORS = 1
    DOCUMENT = 2


class Clipping(Enum):
    BEGIN = 1
    END = 2


class UI(ListViewDelegate):

    STATE_FORMAT = '{:<11}'
    WORKER_ID_FORMAT = '{:<21}'
    TYPE_FORMAT = '{:<7}'
    TASKS_FORMAT = '{:<6}'

    MAX_TOPIC_LENGTH = 30
    TOPIC_FORMAT = '{:<' + str(MAX_TOPIC_LENGTH) + '}'

    STATE_COLORS = {
        'UNASSIGNED': colorpairs.UNASSIGNED,
        'RUNNING': colorpairs.RUNNING,
        'PAUSED': colorpairs.PAUSED,
        'FAILED': colorpairs.FAILED
    }

    TYPE_COLORS = {
        'source': colorpairs.SOURCE,
        'sink': colorpairs.SINK
    }

    def __init__(self, app):
        self.app = app

    def setupColors(self):
        curses.curs_set(0)

        curses.init_pair(colorpairs.KEY, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(colorpairs.DESCRIPTION, curses.COLOR_BLACK, curses.COLOR_WHITE)

        curses.init_pair(colorpairs.SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)

        curses.init_pair(colorpairs.HEADER_TEXT, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

        curses.init_pair(colorpairs.UNASSIGNED, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.RUNNING, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.PAUSED, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.FAILED, curses.COLOR_RED, curses.COLOR_BLACK)

        curses.init_pair(colorpairs.SOURCE, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.SINK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        curses.init_pair(colorpairs.VIEW, curses.COLOR_BLUE, curses.COLOR_WHITE)

        curses.init_pair(colorpairs.LINE_NUMBER, curses.COLOR_CYAN, curses.COLOR_BLACK)

    def addLegend(self, screen, legendItems):
        moreLabel = Label('')

        def setMoreLabel(clipped):
            moreLabel.text = '...' if clipped else ''

        legendHBox = HBox()
        legendHBox.clipping_callback = setMoreLabel

        for key, description in legendItems:
            keyLabel = Label(key)
            keyLabel.attributes.append(curses.color_pair(colorpairs.KEY))
            legendHBox.add_view(keyLabel, Padding(2, 0, 0, 0))

            descriptionLabel = Label(description)
            descriptionLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
            legendHBox.add_view(descriptionLabel, Padding(0, 0, 0, 0))

        screen.add_view(legendHBox, lambda w, h, v: (0, h - 1, w - moreLabel.required_size().width, 1))
        screen.add_view(moreLabel, lambda w, h, v: (w - v.required_size().width - 1, h - 1, v.required_size().width, 1))

        return (legendHBox, moreLabel)

    def addHeaderBox(self, screen):
        background = BackgroundView(curses.color_pair(colorpairs.HEADER_TEXT))
        screen.add_view(background, lambda w, h, v: (0, 0, w, 2))

        hostLabel = Label(self.app.host)
        hostLabel.attributes.append(curses.color_pair(colorpairs.HEADER_TEXT))
        hostLabel.attributes.append(curses.A_BOLD)

        title_hbox = HBox()
        title_hbox.add_view(hostLabel, Padding(0, 0, 0, 0))
        screen.add_view(title_hbox, lambda w, h, v: (
        (w - v.required_size().width) // 2, 0, title_hbox.required_size().width + 1, 1))

        if self.__mode == Mode.CONNECTORS:
            subtitleBox, moreLabel = self.addColumnNames(screen)
            return (background, title_hbox, subtitleBox, moreLabel)
        else:
            subtitle_hbox = self.addDocumentName(screen)
            return (background, title_hbox, subtitle_hbox)

    def addDocumentName(self, screen):
        moreLabel = Label('')

        def setMoreLabel(clipped):
            moreLabel.text = '...' if clipped else ''

        box = HBox()
        box.clipping_callback = setMoreLabel

        connectorNameLabel = Label(self.__connectorName)
        connectorNameLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        connectorNameLabel.attributes.append(curses.A_BOLD)

        viewLabel = Label('[%s]' % self.__view)
        viewLabel.attributes.append(curses.color_pair(colorpairs.VIEW))
        viewLabel.attributes.append(curses.A_BOLD)

        subtitle_hbox = HBox()
        subtitle_hbox.add_view(connectorNameLabel, Padding(0, 0, 0, 0))
        subtitle_hbox.add_view(viewLabel, Padding(1, 0, 0, 0))
        screen.add_view(subtitle_hbox, lambda w, h, v: (
            (w - v.required_size().width) // 2, 1, subtitle_hbox.required_size().width + 1, 1))

        return subtitle_hbox

    def addColumnNames(self, screen):
        moreLabel = Label('')

        def setMoreLabel(clipped):
            moreLabel.text = '...' if clipped else ''

        box = HBox()
        box.clipping_callback = setMoreLabel

        stateLabel = Label(self.STATE_FORMAT.format('STATE'))
        stateLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        stateLabel.attributes.append(curses.A_BOLD)
        box.add_view(stateLabel, Padding(1, 0, 0, 0))

        workerIdLabel = Label(self.WORKER_ID_FORMAT.format('WORKER_ID'))
        workerIdLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        workerIdLabel.attributes.append(curses.A_BOLD)
        box.add_view(workerIdLabel, Padding(2, 0, 0, 0))

        typeLabel = Label(self.TYPE_FORMAT.format('TYPE'))
        typeLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        typeLabel.attributes.append(curses.A_BOLD)
        box.add_view(typeLabel, Padding(2, 0, 0, 0))

        topicLabel = Label(self.TOPIC_FORMAT.format('TOPIC'))
        topicLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        topicLabel.attributes.append(curses.A_BOLD)
        box.add_view(topicLabel, Padding(2, 0, 0, 0))

        tasksLabel = Label(self.TASKS_FORMAT.format('TASKS'))
        tasksLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        tasksLabel.attributes.append(curses.A_BOLD)
        box.add_view(tasksLabel, Padding(2, 0, 0, 0))

        nameLabel = Label('NAME')
        nameLabel.attributes.append(curses.color_pair(colorpairs.DESCRIPTION))
        nameLabel.attributes.append(curses.A_BOLD)
        box.add_view(nameLabel, Padding(2, 0, 0, 0))

        screen.add_view(box, lambda w, h, v: (0, 1, w - moreLabel.required_size().width, 1))
        screen.add_view(moreLabel, lambda w, h, v: (w - v.required_size().width - 1, 1, v.required_size().width, 1))

        return (box, moreLabel)

    def createListView(self, screen, dataSource):
        listView = ListView(self, dataSource)
        return self.addListView(screen, listView)

    def addListView(self, screen, listView):
        screen.add_view(listView, lambda w, h, v: (0, 2, w, h - 3))
        return listView

    def build_row(self, i, data, is_selected, width) -> View:
        if self.__mode == Mode.CONNECTORS:
            return self.buildConnectorRow(i, data, is_selected, width)

        elif self.__mode == Mode.DOCUMENT:
            return self.buildDocumentRow(i, data, is_selected, width)

    def buildDocumentRow(self, i, data, is_selected, width) -> View:
        rowHBox = HBox()

        lineNumber, line = data
        if self.__lineNumbers:
            formatString = '{:>%s}' % len(str(self.__document.getNumberOfUnwrappedLines()))
            lineWrapped = str(lineNumber) if lineNumber != None else ''
            lineNumberLabel = Label(formatString.format(lineWrapped))
            lineNumberLabel.attributes.append(curses.color_pair(colorpairs.LINE_NUMBER))

            rowHBox.add_view(lineNumberLabel, Padding(0, 0, 2, 0))

        lineLabel = Label(line)
        rowHBox.add_view(lineLabel, Padding(0, 0, 0, 0))

        if rowHBox.required_size().width >= width:
            length = (rowHBox.required_size().width - width) + 1
            self.clipLabel(lineLabel, length)

        result = rowHBox
        if is_selected:
            result = BackgroundView(curses.color_pair(colorpairs.SELECTED))
            result.add_view(rowHBox)
            for label in rowHBox.get_elements():
                label.attributes.append(curses.color_pair(colorpairs.SELECTED))

        return result

    def clipLabel(self, label, length, indicator='...', clipping=Clipping.END):
        length = length + len(indicator)
        if clipping == Clipping.END:
            clippedValue = label.text[:-length] + indicator
        else:
            clippedValue = indicator + label.text[length:]

        label.text = clippedValue

    def buildConnectorRow(self, i, data, is_selected, width) -> View:
        rowHBox = HBox()

        state, type, workerId, tasks, topic, name = data

        stateLabel = Label(self.STATE_FORMAT.format(state))
        stateLabel.attributes.append(curses.color_pair(self.STATE_COLORS[state]))
        stateLabel.attributes.append(curses.A_BOLD)

        workerIdLabel = Label(self.WORKER_ID_FORMAT.format(workerId))

        typeLabel = Label(self.TYPE_FORMAT.format(type))
        typeLabel.attributes.append(curses.color_pair(self.TYPE_COLORS[type]))
        typeLabel.attributes.append(curses.A_BOLD)

        tasksLabel = Label(self.TASKS_FORMAT.format(tasks))

        if topic and len(topic) > self.MAX_TOPIC_LENGTH:
            topic = topic[0:self.MAX_TOPIC_LENGTH-3] + '...'
        topicLabel = Label(self.TOPIC_FORMAT.format(topic if topic else ''))

        nameLabel = Label(name)

        rowHBox.add_view(stateLabel, Padding(1, 0, 0, 0))
        rowHBox.add_view(workerIdLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(typeLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(topicLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(tasksLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(nameLabel, Padding(2, 0, 0, 0))

        result = rowHBox
        if is_selected:
            result = BackgroundView(curses.color_pair(colorpairs.SELECTED))
            result.add_view(rowHBox)
            for label in rowHBox.get_elements():
                label.attributes.append(curses.color_pair(colorpairs.SELECTED))

        return result

    def switchToDocument(self, document: Document, connector: str, view: str):
        self.__mode = Mode.DOCUMENT
        self.__connectorName = connector
        self.__view = view
        self.__document = document

        self.__screen.remove_view(self.__connectorsListView)
        self.__documentListView = self.createListView(self.__screen, document)

        self.__screen.remove_views(self.__legendElements)
        self.__legendElements = self.addLegend(self.__screen, legends.document())

        self.__screen.remove_views(self.__headerElements)
        self.__headerElements = self.addHeaderBox(self.__screen)

    def switchToConnectors(self):
        self.__mode = Mode.CONNECTORS

        self.__screen.remove_view(self.__documentListView)
        self.addListView(self.__screen, self.__connectorsListView)

        self.__screen.remove_views(self.__legendElements)
        self.__legendElements = self.addLegend(self.__screen, legends.main())

        self.__screen.remove_views(self.__headerElements)
        self.__headerElements = self.addHeaderBox(self.__screen)

    def isMacOs(self):
        return platform.system() == 'Darwin'

    def reloadConnectors(self):
        self.app.refreshConnectors(onBegin=self.onReloadBegin,
                                   onFetchComplete=self.onFetchComplete,
                                   onLoadingBegin=self.onConnectorLoadingBegin,
                                   onClomplete=self.onReloadComplete)
        self.render()

    def onReloadBegin(self):
        self.hideConnectorsList()
        self.showApiInteractionStatusLabel('Fetching connectors...')
        self.render()

    def onFetchComplete(self, connectorIds):
        self.__maxConnectorIdLength = len(max(connectorIds, key=len))

    def onConnectorLoadingBegin(self, i, n, connectorId):
        connectorFormat = '{:<%d}' % self.__maxConnectorIdLength
        connector = connectorFormat.format("'"+connectorId+"'")
        status = '(%s|%s) Loading Connector %s' % (i, n, connector)
        self.updateApiInteractionStatusLabel(status)
        self.render()

    def onReloadComplete(self):
        self.removeApiInteractionStatusLabel()
        self.showConnectorsList()
        self.render()

    def hideConnectorsList(self):
        self.__screen.remove_view(self.__connectorsListView)

    def showConnectorsList(self):
        self.addListView(self.__screen, self.__connectorsListView)

    def showApiInteractionStatusLabel(self, status):
        self.__statusLabel = Label(status)

        self.__apiStatusHbox = HBox()
        self.__apiStatusHbox.add_view(self.__statusLabel, Padding(0, 0, 0, 0))
        self.__screen.add_view(self.__apiStatusHbox, lambda w, h, v: (
            (w - v.required_size().width) // 2, h // 2, self.__apiStatusHbox.required_size().width + 1, 1))

    def removeApiInteractionStatusLabel(self):
        self.__screen.remove_view(self.__apiStatusHbox)

    def updateApiInteractionStatusLabel(self, status):
        self.__statusLabel.text = status

    def render(self):
        self.__screen.render()

    def loop(self, stdscr):
        self.__mode = Mode.CONNECTORS
        self.__lineNumbers = True
        self.__document = None
        self.setupColors()

        self.__screen = ConstrainedBasedScreen(stdscr)
        self.titleElements = []
        self.__legendElements = self.addLegend(self.__screen, legends.main())
        self.__headerElements = self.addHeaderBox(self.__screen)
        self.__connectorsListView = self.createListView(self.__screen, self.app)
        self.__documentListView = None

        self.reloadConnectors()
        _, _, _, _, _, selectedConnector = self.app.get_data(self.__connectorsListView.get_selected_row_index())

        while 1:
            _, screen_width = self.__screen.get_screen_size()
            if self.__document:
                availableSize = screen_width
                if self.__lineNumbers:
                    availableSize = availableSize - len(str(self.__document.number_of_rows())) - 3
                self.__document.wrapToWidth(availableSize)

            self.render()

            key = stdscr.getch()

            if self.__mode == Mode.CONNECTORS:
                if key == curses.KEY_RESIZE:
                    continue

                if key == keys.UP:
                    self.__connectorsListView.select_previous()
                    _, _, _, _, _, selectedConnector = self.app.get_data(self.__connectorsListView.get_selected_row_index())

                if key == keys.DOWN:
                    self.__connectorsListView.select_next()
                    _, _, _, _, _, selectedConnector = self.app.get_data(self.__connectorsListView.get_selected_row_index())

                if key == keys.L:
                    self.reloadConnectors()

                if key == keys.O:
                    jsonContent = self.app.getConnectorOverview(selectedConnector)
                    document = Document(self.app.prettyfyJson(jsonContent))
                    self.switchToDocument(document, selectedConnector, 'Overview')

                if key == keys.S:
                    jsonContent = self.app.getConnectorStatus(selectedConnector)
                    document = Document(self.app.prettyfyJson(jsonContent))
                    self.switchToDocument(document, selectedConnector, 'Status')

                if key == keys.C:
                    jsonContent = self.app.getConnectorConfig(selectedConnector)
                    document = Document(self.app.prettyfyJson(jsonContent))
                    self.switchToDocument(document, selectedConnector, 'Config')

                if key == keys.T:
                    jsonContent = self.app.getConnectorTasks(selectedConnector)
                    document = Document(self.app.prettyfyJson(jsonContent))
                    self.switchToDocument(document, selectedConnector, 'Tasks')

                if key == keys.R:
                    self.app.restartConnector(selectedConnector)
                    self.app.refreshConnector(self.__connectorsListView.get_selected_row_index())

                if key == keys.P:
                    self.app.pauseConnector(selectedConnector)
                    self.app.refreshConnector(self.__connectorsListView.get_selected_row_index())

                if key == keys.E:
                    self.app.resumeConnector(selectedConnector)
                    self.app.refreshConnector(self.__connectorsListView.get_selected_row_index())

                if key == keys.U:
                    conifg = self.app.getConnectorConfig(selectedConnector)
                    conifg = self.app.prettyfyJson(conifg)
                    self.app.updateConnector(selectedConnector, conifg)
                    exit(0)

                if key == keys.Q:
                    exit(0)

            else:
                if key == keys.UP:
                    self.__documentListView.select_previous()

                if key == keys.DOWN:
                    self.__documentListView.select_next()

                if key == keys.O:
                    self.app.openEditor(self.__document.getText())
                    exit(0)

                if key == keys.L:
                    self.__lineNumbers = not self.__lineNumbers

                if key == keys.C and self.isMacOs():
                    if self.app.number_of_rows() > 0:
                        text = self.__document.getText()
                        subprocess.run("pbcopy", universal_newlines=True, input=text)
                        self.switchToConnectors()

                if key == keys.Q:
                    self.switchToConnectors()