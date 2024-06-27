import importlib
import json
from unittest import mock

import ujson
import pytest

from src import StopWatch, StopWatchDict, Lap, exceptions
import datetime


class TimeChanger:
    _fake_time: float

    def __init__(self, fake_time: float):
        self.change_time(fake_time)

    def change_time(self, fake_time: float):
        self._fake_time = fake_time

    def add_time(self, time_to_add: float) -> float:
        self._fake_time = self._fake_time + time_to_add
        return self._fake_time

    @property
    def fake_time(self) -> float:
        return self._fake_time

    def __call__(self) -> float:
        return self._fake_time


@pytest.fixture
def create_time_changer():
    def _inner(fake_time: float = datetime.datetime(2000, 10, 23, 12, 30, 20, 10).timestamp()) -> TimeChanger:
        return TimeChanger(fake_time)

    return _inner


@pytest.fixture
def time_changer(create_time_changer) -> TimeChanger:
    return create_time_changer()


def test_stop_watch__happy_path(create_time_changer):
    start = datetime.datetime(2020, 1, 1).timestamp()
    time_changer = create_time_changer(start)

    timer = StopWatch(time_func=time_changer)

    assert not timer.stopped
    assert timer.total is None
    assert timer.running

    stop = time_changer.add_time(59.0)

    assert timer.stop(), "Stopping a running timer should have returned true."

    assert not timer.running
    assert timer.stopped
    assert timer.total == 59.0

    time_changer.change_time(117.0)
    assert not timer.stop(), "Attempting to stop an already stopped timer should have returned false."
    assert len(timer.laps) == 1
    re_stop_attempt_lap = timer.laps[0]

    assert re_stop_attempt_lap["lap_name"] == "attempted_to_stop_again"
    assert re_stop_attempt_lap["lap_time_stamp"] == 117.0

    expected_dict = StopWatchDict(
        start_time=start,
        stop_time=stop,
        laps=[Lap(lap_name="attempted_to_stop_again", lap_time_stamp=117.0)],
        total_time=59.0,
    )

    assert timer.as_dict() == expected_dict

    assert ujson.dumps(timer) == ujson.dumps(expected_dict)
    assert str(timer) == ujson.dumps(expected_dict)


def test_stop_watch__manual_start_time(time_changer):
    timer = StopWatch(start_time=time_changer(), time_func=time_changer)

    assert timer.start_time == time_changer.fake_time
    assert not timer.stopped

    time_changer.add_time(343.0)
    timer.stop()

    assert timer.stop_time == time_changer.fake_time
    assert timer.total == 343.0


@pytest.mark.parametrize("bad_value", ["123", 123, True, datetime.datetime(2020, 1, 1)])
def test_stop_watch__manual_start_time_bad_type(bad_value):
    with pytest.raises(exceptions.ProgrammerError):
        StopWatch(start_time=bad_value)


def test_stop_watch__laps(time_changer):
    """Check that the timer can have named laps."""
    time_changer.change_time(0.0)
    timer = StopWatch(time_func=time_changer)

    # total 14.5s
    expected_laps = [
        Lap(lap_name="a", lap_time_stamp=2.0),
        Lap(lap_name="b", lap_time_stamp=3.5),
        Lap(lap_name="c", lap_time_stamp=6.7),
        Lap(lap_name="d", lap_time_stamp=7.7),
        Lap(lap_name="e", lap_time_stamp=12.7),
        Lap(lap_name="f", lap_time_stamp=14.5),  # This final time + 1 will be the total.
    ]

    for lap in expected_laps:
        time_changer.change_time(lap["lap_time_stamp"])
        timer.lap(lap["lap_name"])

    time_changer.add_time(1.0)
    timer.stop()

    assert timer.total == 15.5, "Total time should have been all of the lap times plus the final 1s addition."
    assert len(timer.laps) == len(expected_laps)
    assert timer.laps == expected_laps

    assert timer.as_dict()["laps"] == expected_laps


def test_json_fallback(time_changer):
    """Test that we can fallback to builtin json if ujson is not installed."""
    time_changer.change_time(0)
    with mock.patch.dict("sys.modules", {"ujson": None}):
        # We need to reload the module to trigger the error because the modules were loaded before the mock happened.
        from src import stop_watch as local_sw

        importlib.reload(local_sw)
        expected = json.dumps(
            local_sw.StopWatchDict(
                start_time=0,
                stop_time=0,
                laps=[],
                total_time=0,
            )
        )
        timer = local_sw.StopWatch(time_func=time_changer)
        timer.stop()

        assert timer.__json__() == expected
