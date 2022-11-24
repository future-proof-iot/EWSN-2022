# Scalability

This experiment wants to evaluate the PoC performance as network congestion increases.
To do so it logs the results of a single EPOCH for a defined set of devices. It the
repeats this for different TWR expiry values. The experiment wants to verify two
things:

- the PoC can handled a relatively large amount of neighbors (+10)
- performance does not decrease with the use of a TWR expiry time

## I) Prerequisites

See [IoT-LAB requirements](../../README.md).

## II) Experimentation details

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

## II.A) Embedded Application

This test uses the [pepper_iotlab](https://anonymous.4open.science/r/EWSN-pepper-D6AD/apps/pepper_iotlab)
application, see the [README.md](https://anonymous.4open.science/r/EWSN-pepper-D6AD/apps/pepper_iotlab/README.md) for more details. This application enables a module to log TWR missed encounters, which will be used to calculate a TWR exchange success rate.

### II.B) General Workflow

1. Book an IoT-LAB experiment for all available nodes
```shell
iotlab-experiment submit -n "ewsn2022" -d 60 -l 14,archi=dwm1001:dw1000+site=lille
```

2. Wait for the experiment to be in the Running state:

```shell
$ iotlab-experiment wait --timeout 30 --cancel-on-timeout
```

3. Compile the application
```
make -C apps/pepper_iotlab
```

4. Flash all nodes

```
iotlab-node --flash <PATH_TO_APPS>/apps/pepper_iotlab/bin/dwm1001/pepper_iotlab.elf -i <exp_id>
```

Alternatively flash all nodes individually, first get the nodes list

```shell
$ iotlab-experiment  --jmespath="items[*].network_address | sort(@)" get --nodes
[
    "dwm1001-1.lille.iot-lab.info",
    ...
]
```

When flashing the devices set `IOTLAB_NODE` to one of the above values, e.g. for
the firs node: `IOTLAB_NODE=dwm1001-1.lille.iot-lab.info`.

```
IOTLAB_NODE=dwm1001-1.lille.iot-lab.info make -C apps/pepper_iotlab flash
```

5. For a set a of nodes (start with 2) start pepper for a single iteration:

```shell
pepper start
```

At the end of the epoch contact data with TWR exchange metrics for each contact will be logged over serial.

6. Repeat step 13 times, adding one more neighbor on each iteration.

## III) Exposed datasets

This section provides an overview of the [datasets](./datasets)

| Dataset | Description |
|---------|-------------|
| [ds-scale.csv](./datasets/ds-scale) | CSV wit contact data for every IoT-LAB device under test, across the different configurations|

## III.A) TWR rendez-vous success rate

For the rendez-vous success rate we look only at the responder side. This because
since devices are scanning only a fraction of the time (25%), many advertisements
are missed, so will on average be 25%, but as a TWR request timeouts early, we
are concerned with how many times a RX window is opened for no TWR request to arrive.

The [ds-scale.csv](./datasets/ds-scale.csv) dataset ca be plotted with.

```python
python plot.py
```

<img src="./figures/pepper_scale.jpg" width="300">

---
# Notes on Memory Scalability
The generated data during an epoch requires RAM for tracking the encounters during the epoch, and FLASH storage for off-line infection risk analysis. Since the amount of
data increases with the number of neighbors and encounters,
data aggregation is necessary to tract the size and cost of the
embedded device. We therefore consider the memory footprint analysis under the following:
1. 14 days of contact information, stored in non-volatile storage (see Table 1);
2. encounter information, re-used for every epoch (see Table 2),
conditioned by two parameters: the average number $N_{contacts}$
of daily contacts, and the average number $N_{encounters}$ per
epoch.

| **Item** | **day** | **PETs** | **dist.** | **RSSI** | **time** | **num** | **Total** |
|----------|---------|----------|-----------|----------|----------|---------|-----------|
| UWB      | 2B      | 2x32B    | 2B        | 0B       | 2B       | 2B      | **70B**   |
| BLE      | 2B      | 2x32B    | 0B        | 15x2B    | 15x2B    | 15x2B   | **156B**  |

**Table 1** - Footprint ROM: Contact Data.<br>
<font size="2">*RSSI values are averaged over 15 windows per epoch in DESIRE</font>

| **Item** | **EBID** | **dist.** | **count** | **RSSI** | **time[s]** | **Total** |
|----------|----------|-----------|-----------|----------|-------------|-----------|
| UWB      | 32B      | 4B        | 2B        | 0B       | 3x2B        | **44B**   |
| BLE      | 32B      | 0         | 15x2B     | 15x4B    | 15x2xB      | **182B**  |

**Table 2** - Footprint RAM: Encounter Data.<br>
<font size="2">*RSSI values are averaged over 15 windows per epoch in DESIRE</font>

**Memory footprint**<br>
Let us consider the **D2** or **D3** deployment, where the device depends on a proxy for matching PETS and performing risk evaluation, but must still keep
track of contacts locally. If we consider 100 contacts per day,
this translates into 98 kB and 218.4kB for distance and RSSI
based metrics respectively. This amount of data is rather low
and could even be stored in internal flash to lower device
cost (note that for exposure requests one of the PET is not
transmitted).

**On-device encounter filtering**<br> 
To evaluate the effect of contact data filtering on memory footprint, we ran an experiment on all DWM1001-DEV nodes
on the FIT-IoT-LAB. In the selected experiment, all nodes are in LOS, but only 10 pairs of them are
closer than 2.25m (20 true contacts). We filtered contacts independently using RSSI and UWB metrics,
and in both cases a minimum encounter time of 10~minutes was required.
Applying a distance threshold of $2.25m$, we reduced logged contacts to 20 (0 False Negatives).
Likewise, using an RSSI threshold of -67dB, we were able to reduce the logged
contacts to 138 (stricter filters would mean discarding True Positives).

**In-epoch encounter data**<br>
At the end of an epoch, encounters can be filtered to reduce ROM memory footprint. 
But during the epoch, the device must keep track of all neighbors, and once a neighbor is deemed an encounter it must also keep
track of contact tracing metrics.
If we consider 200 encounters per epoch (e.g., busy subway ride), then RSSI based metrics would require 30kB of RAM, almost
half the available RAM on nRF52832, while distance based metrics would require only
8.8kB.
