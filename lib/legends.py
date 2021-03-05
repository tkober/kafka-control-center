import platform

def main():
    result = [
        ('[UP|DOWN]', ' Scrolling '),
        ('[L]', ' Reload List '),
        ('[O]', ' Overview '),
        ('[S]', ' Status '),
        ('[C]', ' Config '),
        ('[U]', ' Update Config '),
        ('[R]', ' Restart '),
        ('[P]', ' Pause '),
        ('[E]', ' Resume '),
        ('[T]', ' Tasks '),
    ]

    result.append(('[Q]', ' Quit '))
    return result

def document():
    result = [
        ('[UP]', ' Scroll up '),
        ('[DOWN]', ' Scroll down '),
        ('[L]', ' Toggle Line Numbers '),
        ('[O]', ' Open in System Editor ')
    ]

    if platform.system() == 'Darwin':
        result.append(('[C]', ' Copy to clipboard '))

    result.append(('[Q]', ' Quit '))
    return result