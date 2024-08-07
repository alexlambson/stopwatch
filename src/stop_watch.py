import time
import typing as t

try:
    # Use ujson if the user has it installed.
    import ujson as json_module
except ImportError:
    import json as json_module

from src import exceptions

TimeCompatibleCallable = t.Callable[[], float]
"""attr: The type expected for dependency injecting the ``time.time`` function in the stop watch initialization."""


class Lap(t.TypedDict):
    """A named lap for more granular timing."""

    lap_name: str
    """str: Any string that means something to you. e.g. "my_function_begin"."""
    lap_time_stamp: float
    """float: The time that the named lap was called."""


class StopWatchDict(t.TypedDict):
    """A typed dictionary for logging.

    Will be returned by :func:`stop_watch.StopWatch.as_dict` and gets serialized when calling
    ``ujson.dumps()`` on a :class:`~stop_watch.StopWatch`.
    """

    start_time: float
    """float: The time that the stopwatch was created."""
    stop_time: t.Optional[float]
    """t.Optional[float]: The time that the stopwatch was stopped with :func:`stop_watch.StopWatch.stop`"""
    laps: t.List[Lap]
    """t.List[Lap]: The list of named laps in the order that they were created."""
    total_time: t.Optional[float]
    """t.Optional[float]: The total time between creating the stopwatch and calling :func:`stop_watch.StopWatch.stop`"""


class StopWatch:
    """A class to time your code with.

    Supports "laps" to give more granular timing. A lap is just a named point in time that means something to you.
    Laps are created by calling :func:`stop_watch.StopWatch.lap`.
    """

    _start_time: t.Optional[float] = None
    _stop_time: t.Optional[float] = None
    _time: t.Callable[[], float]

    _laps: t.List[Lap]

    def __init__(self, *, start_time: t.Optional[float] = None, time_func: TimeCompatibleCallable = time.time):
        """Initialize a stopwatch timer and start the timer.

        :param start_time:
            If set, this will be the time that the timer starts at instead of ``.time()``.
        :param time_func:
            Dependency injection. Must be a function that returns a float.
            Defaults to the Python ``time.time`` function.
            Is only called if ``start_time`` is ``None``.
        """
        self._time = time_func

        if start_time is not None:
            if not isinstance(start_time, float):
                raise exceptions.SkillIssue("'start_time' must be a float if provided")
            self._start_time = start_time
        else:
            self._start_time = self._time()

        self._laps = []

    @property
    def stopped(self) -> bool:
        """Timer stopped property

        Returns true if the timer has been stopped with :func:`~src.stop_watch.StopWatch.stop`
        """
        return self._stop_time is not None

    @property
    def running(self) -> bool:
        """Returns True if the timer hasn't been stopped yet."""
        return not self.stopped

    @property
    def start_time(self) -> float:
        """Returns the float time that this timer was started at."""
        return self._start_time

    @property
    def stop_time(self) -> float:
        """Returns the float time that this timer was stopped at."""
        return self._stop_time

    @property
    def laps(self) -> t.List[Lap]:
        """Returns the list of named laps."""
        return self._laps

    @property
    def total(self) -> t.Optional[float]:
        """Returns the total time of the timer if the timer has been stopped.

        Returns ``None`` if the timer is still running.
        """
        if self.stopped:
            return self.stop_time - self.start_time
        return None

    def stop(self) -> bool:
        """Stops the timer if it is running.

        If the timer is already stopped then we create a lap at the attempted stop time, then return ``False``.
        If you stop and already stopped timer, then you should consider this a bug in your code and try to fix it.

        :return:
            True if the timer was running and has been stopped.
            False if the timer was already stopped prior to this call.
        """
        if not self.stopped:
            self._stop_time = self._time()
            return True
        self.lap("attempted_to_stop_again")
        return False

    def lap(self, name: str) -> Lap:
        """Record the current time as a named lap.

        Laps **can** be called after the timer has already been stopped.
        This behavior was intentional to help diagnose race conditions even if you've stopped the timer.
        Laps are **not** included in :attr:`~stop_watch.StopWatch.total` and exist purely for tracing your code.

        I did consider the idea of not allowing laps on stopped timers, but that'd either require an error,
        failing silently, or returning a bool that would need to be checked. All of these would be annoying to deal
        with for a simple timer.

        :param name:
            Any string that will be useful to you and your logging.
        :return:
            The :class:`~src.stop_watch.Lap` created by this call.
            Use :attr:`~src.stop_watch.StopWatch.laps` to see all laps.
        """
        self._laps.append(Lap(lap_name=name, lap_time_stamp=self._time()))
        return self._laps[-1]

    def as_dict(self) -> StopWatchDict:
        """Return the dictionary representation of a timer.

        Mostly useful for logging.

        :return:
            A typed dictionary representing this timer.
        """
        return StopWatchDict(start_time=self.start_time, stop_time=self.stop_time, laps=self.laps, total_time=self.total)

    def __json__(self) -> str:
        """Add support for ``ujson.dumps`` being called on this class.

        ``ujson`` will automatically detect and call ``__json__`` in ``ujson.dumps``.

        Regular ``json`` and ``orjson`` do not support checking for a ``__json__`` method.
        You'll need to use ``json.dumps(timer.as_dict())`` for those JSON libraries.

        This function will still work when called without ``ujson`` installed, but you should instead just call
        ``json.dumps(timer.as_dict())`` or ``str(timer)``. I wouldn't recommend calling this method directly.
        """
        return json_module.dumps(self.as_dict())

    def __str__(self) -> str:
        """Converts self to a string."""
        return self.__json__()
