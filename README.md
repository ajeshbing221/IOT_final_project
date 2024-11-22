IoT TTN Receiver
=================

This Python app connects to the TTN MQTT broker and subscribes to all messages
from the class TTN app. It then parses the first byte and dispatches to the
correct decoder.

You must modify your group's `group/groupX.py` file to correctly decode your
device's payload.
