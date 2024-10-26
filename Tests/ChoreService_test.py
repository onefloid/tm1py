import configparser
import random
import pytest
from datetime import datetime
from pathlib import Path
from uuid import uuid1
from TM1py.Objects import Chore, ChoreStartTime, ChoreFrequency, ChoreTask, Process
from TM1py.Services import TM1Service


def _create_chore_object(
    constants,
    name: str,
    active: bool = True,
    dst_sensitivity: bool= True,
    execution_mode: str = Chore.SINGLE_COMMIT,
    start_time: ChoreStartTime = None,
    frequency: ChoreFrequency = None,
    tasks: list[ChoreTask] = None,
)->Chore:
    # Set defaults
    if start_time is None:
        start_time = ChoreStartTime(
            constants["start_time"].year,
            constants["start_time"].month,
            constants["start_time"].day,
            constants["start_time"].hour,
            constants["start_time"].minute,
            constants["start_time"].second,
        )
    if frequency is None:
        frequency = constants["frequency"]

    if tasks is None:
        tasks = constants["tasks"]

    # Create chore
    c = Chore(
        name=name,
        active=active,
        dst_sensitivity = dst_sensitivity,
        execution_mode=execution_mode,
        start_time=start_time,
        frequency=frequency,
        tasks=tasks,
    )

    return c

def _create_and_manage_chore(tm1, constants, chore_name, **chore_kwargs):
    c = _create_chore_object(
        constants=constants,
        name=chore_name,
        **chore_kwargs
    )
    tm1.chores.update_or_create(c)

    yield c

    if tm1.chores.exists(chore_name):
        tm1.chores.delete(chore_name)

@pytest.fixture
def constants():
    prefix = "TM1py_Tests_Chore_"
    frequency_days = int(random.uniform(0, 355))
    frequency_hours = int(random.uniform(0, 23))
    frequency_minutes = int(random.uniform(0, 59))
    frequency_seconds = int(random.uniform(0, 59))
    test_uuid = str(uuid1()).replace('-', "_")
    process_name1 = prefix + 'Process1_' + test_uuid
    chore_name1 = prefix + "Chore1_" + test_uuid
    chore_name2 = prefix + "Chore2_" + test_uuid
    chore_name3 = prefix + "Chore3_" + test_uuid
    chore_name4 = prefix + "Chore4_" + test_uuid
    chore_name5 = prefix + "Chore5_" + test_uuid

    return {
        "process_name1": process_name1,
        "process_name2": prefix + "Process2",
        "chore_name1": chore_name1,
        "chore_name2": chore_name2,
        "chore_name3": chore_name3,
        "chore_name4": chore_name4,
        "chore_name5": chore_name5,
        "chore_names": [
            chore_name1,
            chore_name2,
            chore_name3,
            chore_name4,
            chore_name5,
        ],
        "start_time": datetime.now(),
        "frequency_days": frequency_days,
        "frequency_hours": frequency_hours,
        "frequency_minutes": frequency_minutes,
        "frequency_seconds": frequency_seconds,
        "frequency": ChoreFrequency(
            days=frequency_days,
            hours=frequency_hours,
            minutes=frequency_minutes,
            seconds=frequency_seconds,
        ),
        "tasks": [
            ChoreTask(
                0, process_name1, parameters=[{"Name": "pRegion", "Value": "UK"}]
            ),
            ChoreTask(
                1, process_name1, parameters=[{"Name": "pRegion", "Value": "FR"}]
            ),
            ChoreTask(
                2, process_name1, parameters=[{"Name": "pRegion", "Value": "CH"}]
            ),
        ],
    }

@pytest.fixture
def tm1():
    config = configparser.ConfigParser()
    config.read(Path(__file__).parent.joinpath('config.ini'))
    tm1 = TM1Service(**config['tm1srv01'])
    
    yield tm1

    tm1.logout()

@pytest.fixture
def process1(constants, tm1):
    tm1 = tm1
    process_name = constants["process_name1"]
    p = Process(name=process_name)
    p.add_parameter('pRegion', 'pRegion (String)', value='US')
    tm1.processes.update_or_create(p)

    yield p

    tm1.processes.delete(process_name)

@pytest.fixture
def process2(constants, tm1):
    tm1 = tm1
    process_name = constants["process_name2"]
    p = Process(name=process_name)
    p.add_parameter('pRegion', 'pRegion (String)', value='UK')
    tm1.processes.update_or_create(p)

    yield p

    tm1.processes.delete(process_name)


@pytest.fixture
def chore1(constants, tm1, process1):
    chore_name = constants["chore_name1"]
    yield from _create_and_manage_chore(
        tm1, constants, chore_name, execution_mode=Chore.MULTIPLE_COMMIT
    )

@pytest.fixture
def chore2(constants, tm1, process1):
    chore_name = constants["chore_name2"]
    yield from _create_and_manage_chore(
        tm1, constants, chore_name, active=False,
    )

@pytest.fixture
def chore3(constants, tm1, process1):
    chore_name = constants["chore_name3"]
    yield from _create_and_manage_chore(
        tm1, constants, chore_name, active=False, tasks=[]
    )

@pytest.fixture
def chore4(constants, tm1, process1):
    chore_name = constants["chore_name4"]
    yield from _create_and_manage_chore(
        tm1, constants, chore_name, execution_mode=Chore.MULTIPLE_COMMIT
    )

@pytest.fixture
def chore5(constants, tm1, process1):
    chore_name = constants["chore_name5"]
    yield from _create_and_manage_chore(tm1, constants, chore_name)

def test_get_chore_without_tasks(constants, tm1, chore3):
    c3 = tm1.chores.get(chore_name=constants["chore_name3"])
    assert c3.tasks == []

def test_get_all(constants, tm1, chore1, chore2, chore3, chore4, chore5):
    all_chore_names = (c.name for c in tm1.chores.get_all())
    for chore_name in constants["chore_names"]:
        assert chore_name in all_chore_names

def test_get_all_names(constants, tm1, chore1, chore2, chore3, chore4, chore5):
    all_chore_names = tm1.chores.get_all_names()
    for chore_name in constants["chore_names"]:
        assert chore_name in all_chore_names


@pytest.mark.parametrize("chore_name, is_active, execution_mode",
    [
    ("chore_name1", True,  Chore.MULTIPLE_COMMIT),
    ("chore_name2", False, Chore.SINGLE_COMMIT)
    ])
def test_get_chore(chore_name, is_active, execution_mode, constants, tm1, chore1, chore2):
    c = tm1.chores.get(constants[chore_name])

    assert c._start_time._datetime == constants["start_time"].replace(microsecond=0)
    assert c._name == constants[chore_name]
    assert c._name == constants[chore_name]
    assert c.active is is_active
    assert c._dst_sensitivity is True
    assert c._execution_mode == execution_mode
    assert c._frequency._days == str(constants["frequency_days"]).zfill(2)
    assert c._frequency._hours == str(constants["frequency_hours"]).zfill(2)
    assert c._frequency._minutes == str(constants["frequency_minutes"]).zfill(2)
    assert c._frequency._seconds == str(constants["frequency_seconds"]).zfill(2)
    
    for task1, task2 in zip(constants["tasks"], c._tasks):
        assert task1 == task2

def test_search_for_process_name_happy_case(constants, tm1, process1, chore1, chore2):
    chores = tm1.chores.search_for_process_name(process_name=constants["process_name1"])
    assert len(chores) == 2
    assert chores[0].name == constants["chore_name1"]
    assert chores[1].name == constants["chore_name2"]

def test_search_for_parameter_value_no_match(tm1):
    chore_names = tm1.chores.search_for_parameter_value(parameter_value='NotAParamValue')
    assert chore_names == []

def test_search_for_parameter_value_happy_case(constants, tm1, process1, chore1, chore2):
    chore_names = tm1.chores.search_for_parameter_value(parameter_value='UK')
    assert len(chore_names) == 2
    assert chore_names[0].name == constants["chore_name1"]
    assert chore_names[1].name == constants["chore_name2"]

def test_update_chore_dst(constants, tm1, process2, chore1):
    # get chore
    c = tm1.chores.get(constants["chore_name1"])
    # update all properties
    # update start time
    start_time = datetime(2020, 5, 6, 17, 4, 2)
    c._start_time = ChoreStartTime(
        start_time.year, start_time.month, start_time.day,
        start_time.hour, start_time.minute, start_time.second
    )
    # update frequency
    frequency_days = int(random.uniform(0, 355))
    frequency_hours = int(random.uniform(0, 23))
    frequency_minutes = int(random.uniform(0, 59))
    frequency_seconds = int(random.uniform(0, 59))
    c._frequency = ChoreFrequency(
        days=frequency_days, hours=frequency_hours,
        minutes=frequency_minutes, seconds=frequency_seconds
    )
    # update tasks
    tasks = [
        ChoreTask(0, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'DE'}]),
        ChoreTask(1, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'ES'}]),
        ChoreTask(2, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'US'}])
    ]
    c._tasks = tasks
    # execution mode
    c._execution_mode = Chore.SINGLE_COMMIT
    # dst sensitivity
    c.dst_sensitivity = True
    # activate
    c.deactivate()
    # update chore in TM1
    tm1.chores.update(c)
    # get chore and check all properties
    c = tm1.chores.get(chore_name=constants["chore_name1"])

    assert c.start_time.datetime.hour == start_time.hour
    assert c._start_time._datetime.replace(hour=0) == start_time.replace(hour=0)

    assert c._name == constants["chore_name1"]
    assert c._dst_sensitivity is True
    assert c._active is False
    assert c._execution_mode == Chore.SINGLE_COMMIT
    assert int(c._frequency._days) == int(frequency_days)
    assert int(c._frequency._hours) == int(frequency_hours)
    assert int(c._frequency._minutes) == int(frequency_minutes)
    assert len(tasks) == len(c._tasks)
    # sometimes there is one second difference. Probably a small bug in the REST API
    assert abs(int(c._frequency._seconds) - int(frequency_seconds)) <= 1
    for task1, task2 in zip(tasks, c._tasks):
        assert task1 == task2

def test_update_active_chore(constants, tm1, chore1):
    tm1.chores.activate(constants["chore_name1"])

    c = tm1.chores.get(constants["chore_name1"])
    c.execution_mode = Chore.MULTIPLE_COMMIT

    tm1.chores.update(c)

    c = tm1.chores.get(chore_name=constants["chore_name1"])

    assert c.execution_mode == Chore.MULTIPLE_COMMIT

def test_update_chore_without_tasks(self):
        # get chore
        c = self.tm1.chores.get(self.chore_name1)
        # update all properties
        # update start time
        start_time = datetime(2023,4,5, 12,5,30)
        c._start_time = ChoreStartTime(start_time.year, start_time.month, start_time.day,
                                       start_time.hour, start_time.minute, start_time.second)
        c.dst_sensitivity = True
        # update frequency
        frequency_days = int(random.uniform(0, 355))
        frequency_hours = int(random.uniform(0, 23))
        frequency_minutes = int(random.uniform(0, 59))
        frequency_seconds = int(random.uniform(0, 59))
        c._frequency = ChoreFrequency(days=frequency_days, hours=frequency_hours,
                                      minutes=frequency_minutes, seconds=frequency_seconds)

        # execution mode
        c._execution_mode = Chore.SINGLE_COMMIT
        # activate
        c.deactivate()
        # update chore in TM1
        self.tm1.chores.update(c)
        # get chore and check all properties
        c = self.tm1.chores.get(chore_name=self.chore_name1)
        self.assertEqual(c._start_time._datetime.replace(microsecond=0), start_time.replace(microsecond=0))
        self.assertEqual(c._name, self.chore_name1)
        self.assertEqual(c._dst_sensitivity, True)
        self.assertEqual(c._active, False)
        self.assertEqual(c._execution_mode, Chore.SINGLE_COMMIT)
        self.assertEqual(int(c._frequency._days), int(frequency_days))
        self.assertEqual(int(c._frequency._hours), int(frequency_hours))
        self.assertEqual(int(c._frequency._minutes), int(frequency_minutes))

def test_update_chore_add_tasks(tm1, constants, chore1):
    # get chore
    c = tm1.chores.get(constants["chore_name1"])
    # update all properties
    # update start time
    start_time = datetime.now()
    c._start_time = ChoreStartTime(start_time.year, start_time.month, start_time.day,
                                   start_time.hour, start_time.minute, start_time.second)
    c.dst_sensitivity = True
    # update frequency
    frequency_days = int(random.uniform(0, 355))
    frequency_hours = int(random.uniform(0, 23))
    frequency_minutes = int(random.uniform(0, 59))
    frequency_seconds = int(random.uniform(0, 59))
    c._frequency = ChoreFrequency(days=frequency_days, hours=frequency_hours,
                                  minutes=frequency_minutes, seconds=frequency_seconds)
    # update tasks
    tasks = [ChoreTask(0, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'DE'}]),
             ChoreTask(1, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'ES'}]),
             ChoreTask(2, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'CH'}]),
             ChoreTask(3, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'US'}])]
    c._tasks = tasks
    # execution mode
    c._execution_mode = Chore.SINGLE_COMMIT
    # activate
    c.deactivate()
    # update chore in TM1
    tm1.chores.update(c)
    # get chore and check all properties
    c = tm1.chores.get(chore_name=constants["chore_name1"])
    assert c._start_time._datetime.replace(microsecond=0) == start_time.replace(microsecond=0)
    assert c._name == constants["chore_name1"]
    assert c._dst_sensitivity is True
    assert c._active is False
    assert c._execution_mode == Chore.SINGLE_COMMIT
    assert int(c._frequency._days) == int(frequency_days)
    assert int(c._frequency._hours) == int(frequency_hours)
    assert int(c._frequency._minutes) == int(frequency_minutes)
    assert len(tasks) == len(c._tasks)
    # sometimes there is one second difference. Probably a small bug in the REST API
    assert abs(int(c._frequency._seconds) - int(frequency_seconds)) <= 1
    for task1, task2 in zip(tasks, c._tasks):
        assert task1 == task2

def test_update_chore_remove_tasks(tm1, constants, chore1):
    # get chore
    c = tm1.chores.get(constants["chore_name1"])
    # update all properties
    # update start time
    start_time = datetime.now()
    c._start_time = ChoreStartTime(start_time.year, start_time.month, start_time.day,
                                   start_time.hour, start_time.minute, start_time.second)
    c.dst_sensitivity = True
    # update frequency
    frequency_days = int(random.uniform(0, 355))
    frequency_hours = int(random.uniform(0, 23))
    frequency_minutes = int(random.uniform(0, 59))
    frequency_seconds = int(random.uniform(0, 59))
    c._frequency = ChoreFrequency(days=frequency_days, hours=frequency_hours,
                                  minutes=frequency_minutes, seconds=frequency_seconds)
    # update tasks
    tasks = [ChoreTask(0, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'DE'}]),
             ChoreTask(1, constants["process_name2"], parameters=[{'Name': 'pRegion', 'Value': 'US'}])]
    c._tasks = tasks
    # execution mode
    c._execution_mode = Chore.SINGLE_COMMIT
    # activate
    c.deactivate()
    # update chore in TM1
    tm1.chores.update(c)
    # get chore and check all properties
    c = tm1.chores.get(chore_name=constants["chore_name1"])
    assert c._start_time._datetime.replace(microsecond=0) == start_time.replace(microsecond=0)
    assert c._name == constants["chore_name1"]
    assert c._dst_sensitivity is True
    assert c._active is False
    assert c._execution_mode == Chore.SINGLE_COMMIT
    assert int(c._frequency._days) == int(frequency_days)
    assert int(c._frequency._hours) == int(frequency_hours)
    assert int(c._frequency._minutes) == int(frequency_minutes)
    assert len(tasks) == len(c._tasks)
    # sometimes there is one second difference. Probably a small bug in the REST API
    assert abs(int(c._frequency._seconds) - int(frequency_seconds)) <= 1
    for task1, task2 in zip(tasks, c._tasks):
        assert task1 == task2

def test_activate(tm1, constants, chore1):
    chore = tm1.chores.get(constants["chore_name1"])
    if chore.active:
        tm1.chores.deactivate(constants["chore_name1"])
    tm1.chores.activate(constants["chore_name1"])

def test_deactivate(tm1, constants, chore1):
    chore = tm1.chores.get(constants["chore_name1"])
    if not chore.active:
        tm1.chores.activate(constants["chore_name1"])
    tm1.chores.deactivate(constants["chore_name1"])

def test_execute_chore(tm1, constants, chore1):
    response = tm1.chores.execute_chore(constants["chore_name1"])
    assert response.ok

def test_exists(tm1, constants, chore1, chore2, chore3):
    assert tm1.chores.exists(constants["chore_name1"])
    assert tm1.chores.exists(constants["chore_name2"])
    assert tm1.chores.exists(constants["chore_name3"])
    assert not tm1.chores.exists(str(uuid1()))

def test_search_for_process_name_no_match(tm1):
    chore_names = tm1.chores.search_for_process_name(process_name="NotAProcessName")
    assert chore_names == []