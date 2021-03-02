import platform

def main():
    result = [
        ('[UP]', ' Scroll up '),
        ('[DOWN]', ' Scroll down '),
        ('[R]', ' Refresh '),
        ('[O]', ' Overview '),
        ('[S]', ' Status '),
        ('[C]', ' Config '),
        ('[U]', ' Update Config '),
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
        result.append(('[C]', ' Copy Key '))

    result.append(('[Q]', ' Quit '))
    return result