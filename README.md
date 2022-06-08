# EWSN-2022

This repository is a companion for the paper "PEPPER: Precise Contact Tracing and
Privacy Preservation using Cheap Tokens with BLE and UWB"

> Precise and privacy-preserving contact tracing has become a necessity around the globe,
> for epidemiological reasons, due to the resurgence of global pandemics. To that effect,
> a variety of smartphone-based solutions for contact tracing have been developed in a rush
> and massively deployed, with mixed results, and amid controversies. In reality, achieving
> trustworthy and effective contact tracing at large scale is still an open problem.
> In this paper, we contribute to this field by providing a fully open source software platform leveraging jointly Bluetooth and Ultra-Wide Band (UWB) radios, on top of which various contact tracing solutions can be quickly developed and tested.
> To illustrate the capability of this platform,
> we design and implement \pepper, a technique which leverages jointly Bluetooth and UWB radios (to provide more reliable distance estimations), combined with an adaptation of \desire (an existing contact tracing protocol).
> We show that DESIRE+PEPPER can operate on cheap physical tokens based on low-power microcontrollers.
> We evaluate the complementarity of Bluetooth and UWB in this context, via experiments mimicking various scenarios relevant for contact tracing.
> We show that compared to using only BLE, UWB-based contact event classification can decrease false negatives, but tends to increase false positives.
> Our results suggest that, while DESIRE+PEPPER improves precision over state-of-the-art, further research is required to harness UWB-BLE synergy for contact tracing in practice.
> To this end, our open source platform (which can run on an open-access testbed) provides a useful playground for the research community in this domain.

Experiments where realized with [DWM1001-DEV](https://www.decawave.com/product/mdek1001-deployment-kit/) based boards.
Some of them need a specific, but easy to reproduce setup, while others where performed on the [FIT IoT-LAB](https://www.iot-lab.info/) testbed
and can therefore be reproduced with no hardware requirements.

The remained is organized as follows:

- Section I: specifies common pre requirements shared for all experiments.
- Section II: provides an overview of the different experiments, in cases where those results where used in the paper,
  the matching sections is described.
- Section III: a brief mention to a full contact tracing demonstrator based on a CoAP server to which nodes can offload
  their contact tracing information.

Additionally the individual experiments will often mention

- Additional specific setup and requirements
- Details on the experiment configuration, such as the embedded application (Public Open-source), and the experiment workflow
- Exposed datasets if any as well as tools to analyze/plot those datasets

:warning: Based on this guide, the reader can either:
  - plot the paper results from the datasetsI;
  - **or** generate new datasets using the same software stack;

---

## I) Common Prerequisites
In order to run the provided scripts, the user must fulfil the following steps:

1. Have a complete RIOT build environment, this will allow building and interacting
   with the embedded applications firmwares.

   This step is required if the user wants to collect new datasets.

   **Option 1: Docker-based build**
   Have docker installed with the `riot/riotbuild` image pulled

   ```shell
   $ docker pull riot/riotbuild
   ```
   and add this line to your `.bashrc` or execute it in your terminal before running the experiments scripts (runner script)

   ```shell
   $ export BUILD_IN_DOCKER=1
   ```

   **Option 2: native build (Linux/Mac)**
   - GNU Arm Embedded Toolchain: we used this version `arm-none-eabi-gcc (GNU Arm Embedded Toolchain 10.3-2021.10) 10.3.1 20210824 (release)`
   - GNU Make version 4.0: we used `GNU Make 4.3`

2. DWM1001-DEV devices, either physically or remotely on FIT IoT-LAB

3. Clone the following repository...

## I.A) IoT-LAB Prerequisites

1. Create an IoT lab account to access the testbed: [signup](https://www.iot-lab.info/testbed/signup)
2. Have python `3.7` or higher installed along with its `pip` package manager, then do the following to install the required packages, better in a dedicated [virtualenv](https://docs.python.org/3/tutorial/venv.html) to avoid any conflicts:

  ```shell
  $ python --version
    Python 3.7.9

  $ pip install -r requirements.txt
  ```

  If you are using [conda](https://docs.conda.io/projects/conda/en/latest/index.html), you can alternatively create a new virtual environment using the provided [environment.yml](./environment.yml) file that lists the required python dependencies and creates an environment named `ewsn2022`:

  ```shell
  $ conda env create -f environment.yml

  $ conda env list
    # conda environments:
    #
    base                  *  /Users/rdagher/opt/anaconda3
    ewsn2022                /Users/rdagher/opt/anaconda3/envs/ewsn2022
  $ conda activate ewsn2022
 (ewsn2022)
  ```

3. Authenticate on the testbed (this will store a hidden credentials file in your homedir eg. `$HOME/.iotlabrc`):

  ```shell
  $ iotlab-auth -u <login>
  ```
  where `<login>` is the username for connecting to the testbed (from step 1) and the password will be prompted.

4. Test your installation and remote access to the testbed by showing the available dwm1001 nodes (url, position, etc.)

  ```shell
  $ iotlab-status --nodes --site lille --archi dwm1001
  ```
the output is a json list of nodes information. If this fails, check your credentials in step 3

  ```json
  {
      "items": [
          {
              "archi": "dwm1001:dw1000",
              "camera": 0,
              "mobile": 0,
              "mobility_type": " ",
              "network_address": "dwm1001-1.lille.iot-lab.info",
              "site": "lille",
              "state": "Alive",
              "uid": " ",
              "x": "5.52",
              "y": "68.3",
              "z": "6"
          },
          ...
          ...
          {
              "archi": "dwm1001:dw1000",
              "camera": 0,
              "mobile": 0,
              "mobility_type": " ",
              "network_address": "dwm1001-14.lille.iot-lab.info",
              "site": "saclay",
              "state": "Alive",
              "uid": " ",
              "x": "4.34",
              "y": "64.6",
              "z": "6"
          }
      ]
  ```

## II) Experimentation details

- [Baseline](experiments/baseline): UWB baseline evaluations, RIOT UWB support vs Decawave PANS R2 firmware
- [7.1 Accuracy](experiments/accuracy): PEPPER+DESIRE UWB & BLE metrics accuracy analysis
- [7.3 Scalability](experiments/scalability): PEPPER+DESIRE scalability with an increasing number of neighbors
- [7.2 Power Consumption](experiments/power-consumption): PEPPER+DESIRE power consumption evaluation as well as numerical projections
- [Field Test](experiments/field-test): PEPPER field tests in non controlled environments

## III) Contact Tracing Demonstrator

For the interested reader a Contact Tracing Demo where nodes offload there
contact data over CoAP to an IPv6 over BLE proxy is described [here](https://github.com/future-proof-iot/EWSN-pepper/tree/master/apps/pepper_demo).
