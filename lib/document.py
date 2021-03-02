from gupy.view import ListViewDataSource


class Document(ListViewDataSource):

    def __init__(self, text):
        self.__text = text
        self.__lines = self.__text.split('\n')

    def number_of_rows(self) -> int:
        return len(self.__lines)

    def get_data(self, i) -> object:
        return self.__lines[i]

    def getText(self) -> str:
        return self.__text


