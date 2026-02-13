# MOLTECH-VICI-TTL-control: TTL controller for VICI valve actuator

This is an Arduino Uno R3-based controller for the VICI valve actuator, enabling direct switching of the valve via the TTL standard interface.

**under development**


## Hardware

### Connector

![VICI actuator standard interface connector](.\VICI_fig4.png)

VICI actuator standard interface connector pin-out


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

