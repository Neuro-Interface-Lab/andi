Triggers and acquisition modes
==============================

This page focuses on triggered acquisitions: setting up an external trigger source and performing
single-shot and repetitive acquisitions.

.. note::

   These examples require a Digilent Analog Discovery device connected to your computer and
   the Digilent **WaveForms** software installed.



Wiring
------

The following wiring is used by the example scripts on this page:

- Connect **1-** and **2-** to **GND**
- Connect **1+** and **T1** to **W1**
- Connect **2+** to **W2**

Trigger concepts
----------------

- **Trigger source**: where the trigger event comes from (external trigger, channel, etc.).
- **Trigger type**: edge, level, etc. (depends on your implementation).
- **Trigger position**: where in the buffer the trigger point is placed.
- **Single-shot**: capture once and stop.
- **Repetitive**: capture continuously, typically updating a plot or streaming data.

Example: single-shot acquisition
--------------------------------

.. literalinclude:: ../../../examples/05_scope_single_aquisition.py
   :language: python
   :linenos:

Example: repetitive acquisition loop
------------------------------------

.. literalinclude:: ../../../examples/06_scope_repetitive_aquisition.py
   :language: python
   :linenos:

Notes
-----

- If triggers are unstable, verify the trigger level/reference and the signal routing to T1.
- For periodic signals, averaging can significantly improve SNR; see the next page for interactive averaging workflows.
