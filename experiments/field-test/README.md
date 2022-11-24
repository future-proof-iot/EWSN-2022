# Field Test

The field-test experiment wants to evaluate the PoC in real life (non controlled)
scenarios comparing BLE vs UWB performance ability to classify contacts. Contact data
is logged with a high threshold (10m, 200s encounters), this is done to log as much
data as possible an analyze it. Another option is to apply relevant filters by
setting the following:

- `MAX_DISTANCE_CM`: maximum distance off a contact for it to be relevant (and logged)
- `MIN_EXPOSURE_TIME_S`: minimum exposure time for a contact to be relevant (and logged)

## I) Prerequisites

- For this experimentation a mobile DWM1001-DEV devices is required, with persistent
storage through an SD-CARD, see [requirements](https://anonymous.4open.science/r/EWSN-pepper-D6AD/apps/pepper_field/README.md#pre-requisites) listed by the application.

- Devices will be configured on the field through the [nRF Connect For Mobile](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-mobile/GetStarted) application.

<table>
<caption>Field Prototype</caption>
<tbody>
	<tr>
		<td><input type="image" src="../../pics/prototype-wearable-token.png" width="300"></td>
	</tr>
</tbody>
</table>

## II) Experimentation details

The experiments are conducted by two or more users carrying wearable DWM1001-DEV
devices. The devices will expose GATT service allowing to configure the application
parameters as well start/stop it. The same interface will allow to tag logs, for example
adding 'subway' to tag when the user was riding in the subway.

## II.A) Embedded Application

This test uses the [pepper_pm](https://anonymous.4open.science/r/EWSN-pepper-D6AD/apps/pepper_field)
application. Refer to the application `README` for details on required hardware.

Optionally the following flags can be added to also log individual BLE and UWB
measurements.

- `CONFIG_PEPPER_LOG_UWB`: is set to 1 to log individual UWB measurements
- `CONFIG_PEPPER_LOG_BLE`: is set to 1 to log individual BLE RSSI measurements

By default the application will use default DESIRE+PEPPER parameters:

- Advertisement per EBID slice: 20
- Epoch duration: 900s
- Advertisement interval: 1000ms
- Scan window: 1280 ms
- Scan interval: 5120 ms
- UWB listen window: 2ms
- Iterations: forever (0)

or in c...

```c
    pepper_start_params_t params = {
        .epoch_duration_s = 900,
        .epoch_iterations = 0,
        .adv_itvl_ms = 1000,
        .advs_per_slice = 20,
        .scan_win_ms = 1280,
        .scan_itvl_ms = 5120,
        .align = false,
    };
    pepper_start(&params);
```

### II.B) General Workflow

Upon flashing the devices are not yet performing contact tracing, they must be
configured to do so through their GATT interface. For any scenarios of interest
the workflow is described in the application [README](https://anonymous.4open.science/r/EWSN-pepper-D6AD/apps/pepper_field).

### III) Experiment Data Parsing

On the device `SDCARD` 1 to 3 files should be available:

- 'EPOCH.TXT': contact data logs in JSON format
- 'BLE.TXT' (optional): BLE metrics for each received advertisement, in JSON format
- 'UWB.TXT' (optional): UWB metrics for each successful TWR exchange, in JSON format
