# Accuracy
This experiment aims to evaluate the environment effect on the PEPPER+DESIRE proximity accuracy under contact-tracing relevant scenarios. To this end, a pair of static nodes are deployed and the protocol's range estimates are monitored both during and at the end of the epoch (EBID rotation event).
By taking Line-Of-Sight (LOS) results as a reference, we investigate the effect of physical separations and human body presence on the proximity metrics for both BLE and UWB.
In a nutshell, the main takeaway is that deciding the contact based on BLE RSSI or UWB ranging alone, is not sufficient for CT. Both types of metrics should be jointly used for an optimal classification.

## I) Experimentation details
We deploy one static node and one mobile node (carried as a wear-able shown in Figure and Table below). The experiments consist in 3 minute captures, over distances of $\left[0.5m, 1m, 1.5m, 2m, 2.5m, 3.5m\right]$, as we are mostly interested in accuracy when two tokens are near the critical distance for contact tracing, $d_c = 2m$. 
<table>
<caption>CT-relevant scenarios for proximity measurements [pics]</caption>
<tbody>
	<tr>
		<td><input type="image" src="./pics/setup_ct_pocket_back.jpg" width="230"></td>
        <td><input type="image" src="./pics/setup_ct_los.png" width="230"></td>
        <td><input type="image" src="./pics/setup_ct_backpack.jpg" width="230"></td>
	</tr>
    <tr>
		<td>(a) Pocket</td>
        <td>(b) Line Of Sight</td>
        <td>(c) Backpack </td>
	</tr>
    <!---------------------------->
    <tr>
		<td><input type="image" src="./pics/setup_ct_body.jpg" width="230"></td>
        <td><input type="image" src="./pics/setup_ct_whiteboard.jpg" width="230"></td>
        <td><input type="image" src="./pics/setup_ct_plexiglass.jpg" width="230"></td>
	</tr>
    <tr>
		<td>(d) Human Body </td>
        <td>(e) Whiteboard </td>
        <td>(f) Plexiglass </td>
	</tr>
</tbody>
</table>

<table>
<caption>CT-relevant scenarios for proximity measurements</caption>
<thead>
	<tr>
		<th colspan="3", align="left"><b>Occlusions: Persons in proximity and in contact (no shield)</b></th>
	</tr>
</thead>
<tbody>
	<tr>
		<td><i>Backpack<i></td>
		<td colspan="2">One of the devices is inside a backpack, behind 3 books (total 6cm thickness)</td>
	</tr>
	<tr>
		<td><i>Body</i></td>
		<td colspan="2">A human is occluding the LOS path and equidistant between the devices</td>
	</tr>
    <tr>
		<td><i>Pocket</i></td>
		<td colspan="2">One of the tokens inside the pocket of a volunteer with the body occluding the LOS. The devices are in opposite orientation compared to LOS experiment.</td>
	</tr>
</tbody>
<thead>
	<tr>
		<th colspan="3", align="left"><b>Physical barriers: Persons in proximity but not in contact</b></th>
	</tr>
</thead>
<tbody>
	<tr>
		<td><i>Door</i></td>
		<td colspan="2">A 4cm thick wooden door, made of 32mm chipped wood core with a 4mm mdf panel on both sides.</td>
	</tr>
	<tr>
		<td><i>Whiteboard</i></td>
		<td colspan="2">A double sided 172 × 120 × 4 cm whiteboard.</td>
	</tr>
    <tr>
		<td><i>Plexiglass</i></td>
		<td colspan="2">A 60 × 120 × 0.4cm plexiglass panel, 1m above the floor.</td>
	</tr>
</tbody>
</table>

## II) Prerequisites
The minimal requirements to collect the experimental data
- Hardware: Two raspberry pi boards + their dwm1001-dev attached by usb, mounted on tripods
- Minimal environment for running [pepper_experience](https://github.com/future-proof-iot/EWSN-pepper/tree/ewsn/apps/pepper_experience) : 
    - Add these pythonlibs to your python path:
        - [pepper/pythonlibs](https://github.com/future-proof-iot/EWSN-pepper/tree/ewsn/dist/pythonlibs)
        - [RIOT/dist/pythonlibs](https://github.com/RIOT-OS/RIOT/tree/master/dist/pythonlibs)
    - `pip install -r requirements.txt`
    _Note_: if using `virtualenvwrapper`: `add2virtualenv dist/pythonlibs/`, or add to
    `PYTHONPATH`: `export PYTHONPATH="$PYTHONPATH:<the path>/dist/pythonlibs/"`.

## II.A) Embedded Application
The target application is [pepper_experience](https://github.com/future-proof-iot/EWSN-pepper/tree/ewsn/apps/pepper_experience).

Compared to the [pepper_simple](https://github.com/future-proof-iot/EWSN-pepper/tree/ewsn/apps/pepper_simple) application some extra modules and configurations have been added.

- `pepper_current_time`: to listen for current time advertisements
- `pepper_srv_storage`: to enable logging
- `pepper_status_led`: to show when module is active
- `ed_ble`: to enable storage of BLE encounter data (RSSI)
- `ed_uwb_stats`: to store information on timeout, missed TWR encounters
- `ed_uwb_los` and `ed_uwb_rssi`: to log UWB LoS and RSSI data
- `current_time_shell`: to add shell commands to configure the current time (`ZTIMER_EPOCH`)

- `CONFIG_PEPPER_LOG_UWB`: is set to 1 to log individual UWB measurements
- `CONFIG_PEPPER_LOG_BLE`: is set to 1 to log individual BLE RSSI measurements

**Parameters summary:**

For the capture we reduced the measurement times to x5. This was mainly to speed up captures. No
impact from this change is to be expected since as the window is scaled accordingly with
the capture rate, so fast-fading effect should be equally mitigated through averaging. The impact
of this scaling would only be perceived in power or in respect to collisions when many
devices are present. Shadowing and slow fading remains the same as devices are static. Without sampling frequencies (5Hz) we can consider Rayleigh fading.

- Advertisement per EBID slice: 2
- Epoch duration: 180s
- Advertisement interval: 200ms
- Scan window: 256 ms
- Scan interval: 256 ms
- UWB listen window: 2ms
- Iterations: 1

or in c...

```c
    pepper_start_params_t params = {
        .epoch_duration_s = 180,
        .epoch_iterations = 1,
        .adv_itvl_ms = 200,
        .advs_per_slice = 2,
        .scan_win_ms = 256,
        .scan_itvl_ms = 256,
        .align = false,
    };
    pepper_start(&params);
```

### II.B) General Workflow 
The experimental workflow can be summarized as follows : 
1. Deploy the nodes : flash the firmware
2. Annotate the physical distance, and the environment type (LOS, Pocket, etc)
3. Collect the epoch data on serial port and store into raw files
4. Merge and split the captured data into three panda frames and export them to csv : BLE epoch data, UWB epoch data and Pepper encounter data that is generated at the end of the epoch. Section III provides a brief description on the collected datasets.


## III) Exposed datasets
The collected dataset is described below.
| Dataset | Description |
|---------|-------------|
| [ds-one-to-one-ble.csv](./datasets/ds-one-to-one-ble.csv) | BLE RSSI proximity data |
| [ds-one-to-one-uwb.csv](./datasets/ds-one-to-one-uwb.csv) | UWB TWR ranging proximity data |
| [ds-one-to-one-pepper.csv](./datasets/ds-one-to-one-pepper.csv) | End of epoch data(for the record) |

For BLE data, there is no rssi-based range estimation but only raw RSSI values that 
are expected to correlate do physical distance between nodes. 
Below an overview of the BLE raw data with 
```python
>>> import pandas as pd
>>> data = pd.read_csv('datasets/ds-one-to-one-ble.csv', index_col=0)
>>> data["env"].unique()
array(['plexiglass', 'los', 'pocket', 'backpack', 'db-glass-op',
       'plaster', 'body', 'whiteboard', 'door', 'glass', 'db-glass'],
      dtype=object)
>>> data["d"].unique()
array([0.5 , 1.  , 2.5 , 2.  , 3.5 , 1.5 , 3.  , 0.66])
>>> data.groupby("env").head(1)
               env orientation    d   time  ...  rssi d_est  d_err_absolute  d_err_relative
0       plexiglass       front  0.5  24915  ... -49.0   NaN             NaN             NaN
1700           los       front  1.0  26112  ... -53.0   NaN             NaN             NaN
3349        pocket       front  2.5  23581  ... -68.0   NaN             NaN             NaN
4968      backpack       front  0.5  23372  ... -64.0   NaN             NaN             NaN
8184   db-glass-op       front  3.5  23529  ... -76.0   NaN             NaN             NaN
9660       plaster       front  3.5  24476  ... -72.0   NaN             NaN             NaN
14440         body       front  2.5  23552  ... -71.0   NaN             NaN             NaN
15973   whiteboard       front  1.5  24855  ... -60.0   NaN             NaN             NaN
28583         door       front  1.5  29153  ... -61.0   NaN             NaN             NaN
47469        glass       front  0.5  24266  ... -83.0   NaN             NaN             NaN
47909     db-glass       front  1.5  26163  ... -83.0   NaN             NaN             NaN

[11 rows x 10 columns]
```
Same operations can be done on other csv files for examining the data.
For UWB:
```python
>>> data = pd.read_csv('datasets/ds-one-to-one-uwb.csv', index_col=0)
>>> data.groupby("env").head(1)
               env orientation    d   time  ...       rssi d_est  d_err_absolute  d_err_relative
0       plexiglass       front  0.5  26741  ...        NaN  0.40            0.10        0.200000
1548           los       front  1.0  27736  ...        NaN  0.97            0.03        0.030000
3147        pocket       front  2.5  24974  ...        NaN  2.66            0.16        0.064000
4451      backpack       front  0.5  24619  ...        NaN  0.51            0.01        0.020000
7228   db-glass-op       front  3.5  25279  ...        NaN  4.17            0.67        0.191429
8631       plaster       front  3.5  26451  ... -83.632965  3.87            0.37        0.105714
12814         body       front  2.5  25543  ...        NaN  3.63            1.13        0.452000
14234   whiteboard       front  1.5  26421  ...        NaN  1.41            0.09        0.060000
25942         door       front  1.5  31068  ...        NaN  1.51            0.01        0.006667

[9 rows x 10 columns]
>>> 
```
For PEPPER:
```python
>>> data = pd.read_csv('datasets/ds-one-to-one-pepper.csv', index_col=0)
>>> data.groupby("env").head(1)
>>> data.groupby("env").head(1)
            env orientation    d  ...  ble_ble_scan_count ble_avg_rssi ble_avg_d_cm
0    plexiglass       front  0.5  ...                 858   -48.985497            9
2           los       front  1.0  ...                 837   -51.001427           13
4        pocket       front  2.5  ...                 822   -58.282833           43
6      backpack       front  0.5  ...                 851   -62.747478           86
10  db-glass-op       front  3.5  ...                 753   -76.280449          729
12      plaster       front  3.5  ...                 754   -66.121658          147
18         body       front  2.5  ...                 758   -66.789467          164
20   whiteboard       front  1.5  ...                 771   -56.606709           33
36         door       front  1.5  ...                 853   -57.900284           40

[9 rows x 23 columns]
```
## IV) Results
The experiment results are plotted below: the proximity data with respect to the LOS reference (blue curves): in case of a contact ((a), (b)), and no contact ((c), (d)).
|![baseline_distance](./figures/Figure_5.png)|![baseline_distance](./figures/Figure_7.png)|
|:------------------------------------------:|:------:|
|  (a) Contact Scenarios: **UWB** proximity data  | (b) Contact Scenarios: **BLE** proximity data |     
|![baseline_distance](./figures/Figure_1.png)|![baseline_distance](./figures/Figure_3.png)|
|(c) No Contact Scenarios: **UWB** proximity data | (d) No Contact Scenarios: **BLE** proximity data  |     

Being RSSI-based, BLE is more sensitive to environmental conditions (farther from LOS) than UWB Time-of-Flight approach.
Overall we can see that UWB-based metrics would allow to reduce False Negatives, but at the cost of more False Positives in cases where BLE metrics could be sufficiently attenuated to avoid such detection errors. 