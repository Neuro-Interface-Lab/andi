Oscilloscope basics
===================

This page introduces input (ADC) configuration and a minimal acquisition workflow:
channel configuration, sampling frequency, buffer sizing, and a first captured waveform.

.. note::

   These examples require a Digilent Analog Discovery device connected to your computer and
   the Digilent **WaveForms** software installed.



Concepts
--------

- **Input channel** configuration typically includes range, offset, and attenuation.
- **Sampling frequency** and **buffer size** determine the capture duration and time resolution.
- Most scripts use matplotlib for visualization; if you run headless, you may need a non-interactive backend.

Example: query scope/ADC capabilities
-------------------------------------

Use this example to understand the instrument limits and default configuration values.

.. literalinclude:: ../../../examples/03_in_basics.py
   :language: python
   :linenos:

Example: acquire a waveform buffer
----------------------------------

This example configures the scope and records a waveform into a buffer, then plots it.

.. literalinclude:: ../../../examples/04_scope_aquisition.py
   :language: python
   :linenos:

Practical tips
--------------

- Start with conservative sampling frequency and record length, then increase once the setup works.
- If you see clipping, reduce signal amplitude or increase the input range.
