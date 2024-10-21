import configparser
import random
import pytest
from datetime import datetime
from pathlib import Path
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

@pytest.fixture
def constants():
    prefix = "TM1py_Tests_Chore_"
    process_name1 = prefix + 'Process1'
    frequency_days = int(random.uniform(0, 355))
    frequency_hours = int(random.uniform(0, 23))
    frequency_minutes = int(random.uniform(0, 59))
    frequency_seconds = int(random.uniform(0, 59))

    return {
        "process_name1": process_name1,
        "process_name2": prefix + 'Process2',
        "chore_name1": prefix + "Chore1",
        "chore_name2": prefix + "Chore2",
        "chore_name3": prefix + "Chore3",
        "chore_name4": prefix + "Chore4",
        "chore_name5": prefix + "Chore5",
        "start_time": datetime.now(),
        "frequency_days": frequency_days,
        "frequency_hours": frequency_hours,
        "frequency_minutes": frequency_minutes,
        "frequency_seconds": frequency_seconds,
        "frequency": ChoreFrequency(
            days=frequency_days,
            hours=frequency_hours,
            minutes=frequency_minutes,
            seconds=frequency_seconds
        ),
        "tasks": [
            ChoreTask(0, process_name1, parameters=[{'Name': 'pRegion', 'Value': 'UK'}]),
            ChoreTask(1, process_name1, parameters=[{'Name': 'pRegion', 'Value': 'FR'}]),
            ChoreTask(2, process_name1, parameters=[{'Name': 'pRegion', 'Value': 'CH'}])
        ]
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
    tm1 = tm1
    chore_name = constants["chore_name1"]
    c = _create_chore_object(
        constants=constants,
        name=chore_name,
        execution_mode=Chore.MULTIPLE_COMMIT
    )
    tm1.chores.update_or_create(c)

    yield c 

    if tm1.chores.exists(chore_name):
        tm1.chores.delete(chore_name)

@pytest.fixture
def chore2(constants, tm1, process1):
    tm1 = tm1
    chore_name = constants["chore_name2"]
    c = _create_chore_object(
        constants=constants,
        name=chore_name,
        active=False
    )
    tm1.chores.update_or_create(c)

    yield c 

    if tm1.chores.exists(chore_name):
        tm1.chores.delete(chore_name)

@pytest.fixture
def chore3(constants, tm1):
    tm1 = tm1
    chore_name = constants["chore_name3"]
    c = _create_chore_object(
        constants=constants,
        name=chore_name,
        active=False,
        tasks=[]
    )
    tm1.chores.update_or_create(c)

    yield c

    if tm1.chores.exists(chore_name):
        tm1.chores.delete(chore_name)

@pytest.fixture
def chore4(constants, tm1, process1):
    tm1 = tm1
    chore_name = constants["chore_name4"]
    c = _create_chore_object(
        constants=constants,
        name=chore_name,
        execution_mode=Chore.MULTIPLE_COMMIT
    )
    tm1.chores.update_or_create(c)
    
    yield c

    if tm1.chores.exists(chore_name):
        tm1.chores.delete(chore_name)

@pytest.fixture
def chore5(constants, tm1, process1):
    tm1 = tm1
    chore_name = constants["chore_name5"]
    c = _create_chore_object(
        constants=constants,
        name=chore_name,
    )
    tm1.chores.update_or_create(c)
    
    yield c

    if tm1.chores.exists(chore_name):
        tm1.chores.delete(chore_name)

def test_get_chore_without_tasks(constants, tm1, chore3):
    c3 = tm1.chores.get(chore_name=constants["chore_name3"])
    assert c3.tasks == []

def test_get_all(constants, tm1, chore1, chore2, chore3, chore4, chore5):
    all_chores = (c.name for c in tm1.chores.get_all())
    assert constants["chore_name1"] in all_chores
    assert constants["chore_name2"] in all_chores
    assert constants["chore_name3"] in all_chores
    assert constants["chore_name4"] in all_chores
    assert constants["chore_name5"] in all_chores

def test_get_all_names(constants, tm1, chore1, chore2, chore3, chore4, chore5):
    all_chore_names = tm1.chores.get_all_names()
    assert constants["chore_name1"] in all_chore_names
    assert constants["chore_name2"] in all_chore_names
    assert constants["chore_name3"] in all_chore_names
    assert constants["chore_name4"] in all_chore_names
    assert constants["chore_name5"] in all_chore_names

