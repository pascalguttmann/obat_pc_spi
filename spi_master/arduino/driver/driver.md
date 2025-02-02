# Driver

## Genuine ArduinoUno

No driver installation should be required for usage of a genuine ArduinoUno as
FTDI chip is used, for which drivers are often pre-installed. If there should
be problems try to follow the instructions on [arduino-support-ftdi].

[arduino-support-ftdi]: https://support.arduino.cc/hc/en-us/articles/4411305694610-Install-or-update-FTDI-drivers

## Non-Genuine ArduinoUno

Other boards might use different USB interface chips requiring the
corresponding driver. If you don't know, which chip is used and you cannot
connect try installing the drivers for CH340/CH341 (CH341SER). They are used on
many cheaper knock-offs.
