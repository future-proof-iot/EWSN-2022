# EWSN-2022


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

- [Baseline]():
- [Accuracy]():
- [Power Consumption]():
- [Field Test](experiments/field-test/README.md):

## III) Contact Tracing Demonstrator

Reference CoAP-server and others
