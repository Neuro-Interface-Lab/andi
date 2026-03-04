Real-time acquisition and averaging
===================================

This page shows higher-level acquisition workflows where you continuously acquire data and apply
averaging, while interacting with the acquisition parameters during runtime (mouse/GUI events).

.. note::

   These examples require a Digilent Analog Discovery device connected to your computer and
   the Digilent **WaveForms** software installed.



When to use averaging
---------------------

Averaging is useful when:

- The signal is periodic and time-aligned (or triggered consistently)
- You want to improve precision / reduce noise
- You can tolerate the increased effective acquisition time

Example: averaging with mouse wheel control
-------------------------------------------

This example performs repetitive acquisitions and allows changing the averaging factor using the mouse wheel.

.. literalinclude:: ../../../examples/07_scope_avg_scroll.py
   :language: python
   :linenos:

Example: interactive sampling frequency + reset
-----------------------------------------------

This example adjusts sampling frequency at runtime and provides a control to reset accumulated averages.

.. literalinclude:: ../../../examples/08_scope_avg_realtime.py
   :language: python
   :linenos:

UI controls summary
-------------------

- Scroll: adjust averaging or sampling frequency (depending on the script)
- Middle click (where implemented): reset the accumulated average
- Close the window: exit

Performance notes
-----------------

- Real-time plotting speed depends heavily on CPU/GPU and matplotlib backend.
- If the UI feels sluggish, reduce update rate or the number of samples per acquisition.
