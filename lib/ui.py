from gupy.geometry import Padding
from gupy.view import BackgroundView, Label, HBox, ListView, ListViewDelegate, View
from gupy.screen import ConstrainedBasedScreen
from enum import Enum
import curses
import subprocess
import platform

from lib import colorpairs, legends


class UI(ListViewDelegate):

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
        curses.init_pair(colorpairs.HEADER_TEXT, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(colorpairs.PATTERN, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

        curses.init_pair(colorpairs.LANG, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(colorpairs.TRANSLATION_KEY, curses.COLOR_YELLOW, curses.COLOR_BLACK)

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
        screen.add_view(background, lambda w, h, v: (0, 0, w, 1))

        hostLabel = Label(self.app.host)
        hostLabel.attributes.append(curses.color_pair(colorpairs.HEADER_TEXT))
        hostLabel.attributes.append(curses.A_BOLD)

        title_hbox = HBox()
        title_hbox.add_view(hostLabel, Padding(0, 0, 0, 0))
        screen.add_view(title_hbox, lambda w, h, v: (
        (w - v.required_size().width) // 2, 0, title_hbox.required_size().width + 1, 1))

        return (background, title_hbox)

    def loop(self, stdscr):
        self.setupColors()

        screen = ConstrainedBasedScreen(stdscr)
        self.titleElements = []
        legendElements = self.addLegend(screen, legends.main())
        headerElements = self.addHeaderBox(screen)

        while 1:
            screen.render()

            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                continue

            exit(0)