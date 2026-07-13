from datetime import datetime

def timestamp():
    current_date = datetime.now()
    return current_date.strftime('%d/%m/%Y %H:%M')


def print_message(message: str):
    print('\n┌' + '─' *  (len(message)+2) + '┐')
    print(f'│ {message} │')
    print('└' + '─' * (len(message)+2) + '┘')

def on_start():
    msg = f'Bot started at {timestamp()}'
    print_message(msg)


def on_shutdown():
    msg = f'Bot is down at {timestamp()}'
    print_message(msg)