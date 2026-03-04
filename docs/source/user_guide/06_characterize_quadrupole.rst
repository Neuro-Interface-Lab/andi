Characterize a quadrupole (frequency response)
==============================================

This page demonstrates how to characterize a device-under-test (DUT) as a two-port element by measuring
its frequency response (gain and phase) using a Bode plot workflow.

.. note::

   These examples require a Digilent Analog Discovery device connected to your computer and
   the Digilent **WaveForms** software installed.



What you should document here
-----------------------------

Because hardware setups vary, this page is intentionally structured as a template. You should fill in:

- Exact DUT wiring and signal routing (W1/W2 to DUT, which inputs measure what)
- Any required grounding/shielding practices
- Recommended sweep parameters (start/stop frequency, number of points, amplitude)
- Calibration steps (baseline measurement, reference channel definition) if your workflow supports it

Example: Bode measurement (network analyser)
--------------------------------------------

.. literalinclude:: ../../../examples/09_network_bode.py
   :language: python
   :linenos:

Interpreting results
--------------------

- **Gain magnitude** typically shows amplification/attenuation vs frequency.
- **Phase** indicates reactive behavior (poles/zeros, delays).
- Use logarithmic frequency axis for readability over wide sweeps.
