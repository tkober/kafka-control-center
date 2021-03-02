from gupy.view import ListViewDataSource
import textwrap


class Document(ListViewDataSource):

    def __init__(self, text):
        self.__text = text
        self.__lines = self.__text.split('\n')

    def wrapToWidth(self, width):
        lines = []

        for line in self.__text.split('\n'):
            lines.extend(textwrap.wrap(line, width))

        self.__lines = lines

    def number_of_rows(self) -> int:
        return len(self.__lines)

    def get_data(self, i) -> object:
        return self.__lines[i]

    def getText(self) -> str:
        return self.__text


