# Python Stopwatch

A helper to time your code in a granular way without a ton of bloat.

Useful for people who don't have a metrics service, but do have some form of logging.

Github project: https://github.com/alexlambson/stopwatch/

The main class that a user will be interested in is {py:class}`src.stop_watch.StopWatch`


# Usage

Consider the manual way of timing:

```python
import time

def do_second_thing(timer: float):
    stuff()
    print(f"Stuff took: {time.time() - timer}")
    more_stuff()
    return

start = time.time()
do_something()
do_another_thing()
print(f"Doing two things took: {time.time() - start} seconds")

start2 = time.time()
do_second_thing(start2)
print(f"Doing second thing set took: {time.time() - start2}")
print(f"Total time: {time.time() - start}")
```

Now with stop watch

```python
import stopwatch

def do_second_thing(timer: StopWatch):
    stuff()
    timer.lap("do_second_thing.stuff_took")
    more_stuff()
    return

timer = stopwatch.StopWatch()
do_something()
do_another_thing()
timer.lap("Doing two things")

do_second_thing()
timer.lap("second_thing")
# timer.stop() can be called manually, but will also be called inside __str__
print(timer)
```
