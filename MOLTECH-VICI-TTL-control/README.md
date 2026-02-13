# MOLTECH-VICI-TTL-control: TTL controller for VICI valve actuator

This is an Arduino Uno R3-based controller for the VICI valve actuator, enabling direct switching of the valve via the TTL standard interface.

**under development**


## Hardware

### Connector

The controller should be connected to the 6-pin "standard interface" connector on the back of the VICI valve enclosure.

![VICI actuator standard interface connector](./VICI_fig4.png)

**Figure.** VICI actuator standard interface connector pin-out

The functions of the pins change slightly depending on the operating mode of the valve actuator. 

**WARNING!** The current controller is designed for operation with the "Two Position Mode" only!

#### Two Position Mode Pin Assignments

| Pin # | Function         |
|-------|------------------|
| 1     | A output (3.3 VDC)|
| 2     | Common           |
| 3     | B output (3.3 VDC)|
| 4     | A contact        |
| 5     | Unused           |
| 6     | B contact        |


#### Multiposition Mode Pin Assignments

  Pin # | Function         |
 |-------|------------------|
 | 1     | Motor Run output |
 | 2     | Common           |
 | 3     | Home output      |
 | 4     | Home             |
 | 5     | Unused           |
 | 6     | Step             |

