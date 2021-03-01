def main():
    result = [
        ('[UP]', ' Scroll up '),
        ('[DOWN]', ' Scroll down '),
        ('[R]', ' Refresh '),
        ('[O]', ' Overview '),
        ('[S]', ' Status '),
        ('[ENTER]', ' Config '),
        ('[U]', ' Update Config '),
        ('[T]', ' Tasks '),
    ]

    result.append(('[Q]', ' Quit '))
    return result

def fileView():
    return [
        ('[UP|DOWN]', ' Scroll '),
        ('[ESC]', ' Quit ')
    ]