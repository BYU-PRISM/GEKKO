# Writing and Running Gekko test

## Writing 
Mostly writing an end-to-end test for gekko is like writing a specific use case, but there are a few things to keep in mind. 
- Do not use `random` in tests. It is almost impossible to test that. Run the script with `random` once and then save those 'random' input points into the test script.
- Keep the number of iterations low. We are running a lot of tests here and so we don't want tests to take longer than they need to.
- Don't forget to add your test to `run_tests.py`. In the future this will hopefully be resolved in a more pythonic fashion. 
- set `disp=False` in `GEKKO.solve()`. This keeps thhe output cleaner.
- Do not include print statements in tests. Use an `assert` instead and keep the output clean. Your script should not print anything unless it breaks.
- This folder is meant only for end-to-end tests. Add unit tests side-by-side with the file to be tested(once we implement this).
- Name your test descriptively and end it with `_test.py`. This will allow to get pciked up automatically in the future.
- Import the test runner `import test_runner`. This allows us to handle all the tests the same.
- Encapsulate your entire test into a single method. Pass this method along with a descriptive name to `test_runner.test()`. See `hs71_test.py` for an example.
- Use `assert` methods or similar from a testing package to confirm the test ran properly

## Running
The E2E(end-to-end) tests can all be run together with the following:
```bash
python run_tests.py
```
A green `Success` message will appear for passing tests and a red `Failed` will appear along with the traceback and `AssertionError` if a test fails. Since these tests by nature can take some time, expect it to take some time for all the E2E tests to run. 

The E2E tests can also be run individually as a usual python script with the same results as above.


## Ideas for improvement
- Add unit testing - Very Important!
- Improve the importing process in `run_tests.py` so anything ending in `_test.py` in the folder gets run. 
- Allow the tests to parrallelize to make everything faster and everyone happier.