from colorama import Fore, Style
import traceback

def test(name, testFunc):
    try:
        print('Testing {}...'.format(name), end='')
        testFunc()
        print(f'\t{Fore.GREEN}Success{Style.RESET_ALL}')
    except AssertionError:
        print(f'\t{Fore.RED}Failed{Style.RESET_ALL}')
        print(traceback.format_exc())
    except Exception as e:
        print('Unhandled error!')
        print(e)