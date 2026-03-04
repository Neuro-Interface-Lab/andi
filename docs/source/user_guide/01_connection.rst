Connection and device discovery
===============================

This page shows how to detect connected Digilent devices, identify them (name/serial), and open
a session with ANDI.

.. note::

   These examples require a Digilent Analog Discovery device connected to your computer and
   the Digilent **WaveForms** software installed.



Checklist
---------

- Install WaveForms
- Plug the Analog Discovery device via USB
- Close other applications that may be using the device (WaveForms, other Python sessions, etc.)

Example: connect and list devices
---------------------------------

.. literalinclude:: ../../../examples/00_connect.py
   :language: python
   :linenos:

Troubleshooting
---------------

- **No device found**: check USB cable, permissions (Linux udev rules), and that WaveForms can see
  the device.
- **Device already opened**: close WaveForms or any other process that holds the device.
