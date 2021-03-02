import sys

from gupy.view import ListViewDataSource
import textwrap


class Document(ListViewDataSource):

    def __init__(self, text):
        self.__text = text
        self.wrapToWidth(sys.maxsize)

    def wrapToWidth(self, width):
        lines = []

        i = 1
        for line in self.__text.split('\n'):
            begin = True
            for wrappedLine in textwrap.wrap(line, width):
                lineNumber = i if begin else None
                lines.append((lineNumber, wrappedLine))

                begin = False

            i += 1

        self.__lines = lines
        self.__numeberOfUnwrappedLines = i-1

    def number_of_rows(self) -> int:
        return len(self.__lines)

    def get_data(self, i) -> object:
        return self.__lines[i]

    def getText(self) -> str:
        return self.__text

    def getNumberOfUnwrappedLines(self) -> int:
        return self.__numeberOfUnwrappedLines


