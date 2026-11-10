# Setup TM1py Tests

- `pip install "tm1py[dev]"`

- Use a TM1 development environment

- In `Tests` folder: Copy the file `config.ini.template` with the new name `config.ini`

- Specify your instance coordinates in the config.ini file as `tm1srv01`

- `EnableSandboxDimension` config parameter must be set to `F` for the target TM1 instance

- `EnableTIDebugging` config parameter must be set to `T` for the target TM1 instance

# Run TM1py Tests

## Run tests via commandline 

### To run all tests

On Windows:

`pytest .\Tests\`

On Linux and macOS:

`pytest ./Tests/`

### To run tests in parallel

Tests can run in parallel with [pytest-xdist](https://pytest-xdist.readthedocs.io/) (included in `tm1py[dev]`).
Tests marked as `serial` affect global server state (e.g. they close sessions or cancel threads of other users)
and must not run in parallel with other tests. Run them in a separate, sequential step:

`pytest -n auto -m "not serial" ./Tests/`

`pytest -m serial ./Tests/`

#### Writing tests that can run in parallel

- Make the names of all TM1 objects (cubes, dimensions, views, processes, chores, users, files, ...) unique
  per test class. Use `generate_test_uuid()` from `Tests/Utils.py` in `setUpClass`.
- Don't assert on global counts (e.g. number of cubes on the server). Other tests may create or delete
  objects at the same time. Assert that your own objects are (or are not) part of the result instead.
- Make search terms unique (e.g. rule comments, process code, parameter values), so that searches only find
  objects of the current test run.
- Don't use arbitrary server objects (e.g. a random dimension). They may be deleted by other tests.
- Mark tests that change global server state with `@pytest.mark.serial`.

### To run a specific test file from the `Tests` folder

On Windows:

`pytest .\Tests\ChoreService_test.py`

On Linux and macOS:

`pytest ./Tests/ChoreService_test.py`

## Run tests via PyCharm

### To run all tests

rightclick `Tests` folder -> run 'pytest in Tests'

### To run a specific test file from the `Tests` folder:
rightclick file (e.g., `ChoreService_test.py`) -> run 'pytest in ChoreService_test.py'
