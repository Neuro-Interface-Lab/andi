Generate signals
================

This page explains how to use ANDI's waveform generator features: querying generator capabilities
and producing common waveforms (sine/square/triangle).

.. note::

   These examples require a Digilent Analog Discovery device connected to your computer and
   the Digilent **WaveForms** software installed.



Concepts
--------

- **Output channels**: the Analog Discovery provides one or more waveform generator channels.
- **Reset**: it is good practice to reset generators before configuring a new output.
- **Enable/disable**: explicitly enable the output you are using, and disable it when finished.

Example: generator capabilities and basic setup
-----------------------------------------------

This first example focuses on capability queries (number of channels, frequency limits, buffer sizes)
and basic output enable/disable.

.. literalinclude:: ../../../examples/01_out_basics.py
   :language: python
   :linenos:

Example: generate sine / square / triangle
------------------------------------------

This example shows how to actually generate common waveforms, switching between them.

.. literalinclude:: ../../../examples/02_waveforms.py
   :language: python
   :linenos:

Notes
-----

- When validating waveforms, use either the Analog Discovery scope inputs or an external oscilloscope.
- If the waveform does not appear, confirm the correct output channel and wiring.
