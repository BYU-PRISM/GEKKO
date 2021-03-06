# This is the test_runner for our end-to-end tests. It is not 
# a test itself, but import it and use it to run your own E2E tests.
# See `hs71_test.py` for an example.
from colorama import Fore, Style
import traceback
import numpy as np

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

def like(v1,v2):
    eps = 1e-5 #maximum allowable difference
    v1 = np.array(v1)
    v2 = np.array(v2)
    if np.any(np.abs(v1-v2)>eps):
        return False
    else: 
        return True