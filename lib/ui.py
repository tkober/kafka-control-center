from gupy.geometry import Padding
from gupy.view import BackgroundView, Label, HBox, ListView, ListViewDelegate, View
from gupy.screen import ConstrainedBasedScreen
from enum import Enum
import curses
import subprocess
import platform

from lib import colorpairs, legends, keys


class UI(ListViewDelegate):

    STATE_FORMAT = '{:<11}'
    WORKER_ID_FORMAT = '{:<21}'
    TYPE_FORMAT = '{:<7}'
    TASKS_FORMAT = '{:<6}'

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

        curses.init_pair(colorpairs.ADDED, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.DELETED, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.MODIFIED, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.MOVED, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.UNTRACKED, curses.COLOR_CYAN, curses.COLOR_BLACK)

        curses.init_pair(colorpairs.STAGED, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.CONFIRMATION, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(colorpairs.CONFIRMATION_SELECTION, curses.COLOR_BLACK, curses.COLOR_WHITE)

        curses.init_pair(colorpairs.FILTER_CRITERIA, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(colorpairs.FILTER_CRITERIA_EDITING, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(colorpairs.HEADER_TEXT, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        curses.init_pair(colorpairs.PATTERN, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

        curses.init_pair(colorpairs.LANG, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.TRANSLATION_KEY, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        curses.init_pair(colorpairs.UNASSIGNED, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.RUNNING, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.PAUSED, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.FAILED, curses.COLOR_RED, curses.COLOR_BLACK)

        curses.init_pair(colorpairs.SOURCE, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.SINK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

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

        columnNamesBox, moreLabel = self.addColumnNames(screen)

        return (background, title_hbox, columnNamesBox, moreLabel)

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

    def addListView(self, screen):
        listView = ListView(self, self.app)
        screen.add_view(listView, lambda w, h, v: (0, 2, w, h-2))

        return listView

    def build_row(self, i, data, is_selected, width) -> View:
        rowHBox = HBox()

        state, type, workerId, tasks, name = data

        stateLabel = Label(self.STATE_FORMAT.format(state))
        stateLabel.attributes.append(curses.color_pair(self.STATE_COLORS[state]))
        stateLabel.attributes.append(curses.A_BOLD)

        workerIdLabel = Label(self.WORKER_ID_FORMAT.format(workerId))

        typeLabel = Label(self.TYPE_FORMAT.format(type))
        typeLabel.attributes.append(curses.color_pair(self.TYPE_COLORS[type]))
        typeLabel.attributes.append(curses.A_BOLD)

        tasksLabel = Label(self.TASKS_FORMAT.format(tasks))

        nameLabel = Label(name)

        rowHBox.add_view(stateLabel, Padding(1, 0, 0, 0))
        rowHBox.add_view(workerIdLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(typeLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(tasksLabel, Padding(2, 0, 0, 0))
        rowHBox.add_view(nameLabel, Padding(2, 0, 0, 0))

        result = rowHBox
        if is_selected:
            result = BackgroundView(curses.color_pair(colorpairs.SELECTED))
            result.add_view(rowHBox)
            for label in rowHBox.get_elements():
                label.attributes.append(curses.color_pair(colorpairs.SELECTED))

        return result


    def loop(self, stdscr):
        self.setupColors()

        screen = ConstrainedBasedScreen(stdscr)
        self.titleElements = []
        legendElements = self.addLegend(screen, legends.main())
        headerElements = self.addHeaderBox(screen)
        listView = self.addListView(screen)

        while 1:
            screen.render()

            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                continue

            if key == keys.UP:
                listView.select_previous()

            if key == keys.DOWN:
                listView.select_next()

            if key == keys.R:
                self.app.refreshConnectors()

            if key == keys.Q:
                exit(0)