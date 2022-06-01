# Baseline

The experiment aims to evaluate ranging performance between two static nodes at a
fixed known distance comparing RIOT `uwb-core` and Decawave default firmware.

## I) Prerequisites

- Add these pythonlibs to your python path:
    - [pepper/pythonlibs](https://gitlab.inria.fr/pepper/riot-desire/-/tree/develop/dist/pythonlibs)
    - `rng-eval/dist/pythonlibs`
    - [RIOT/dist/pythonlibs](https://github.com/RIOT-OS/RIOT/tree/master/dist/pythonlibs)
- `pip install -r requirements.txt`

_Note_: if using `virtualenvwrapper`: `add2virtualenv dist/pythonlibs/`, or add to
`PYTHONPATH`: `export PYTHONPATH="$PYTHONPATH:<the path>/dist/pythonlibs/"`.

## II) Experimentation details


## II.A) Embedded Application

For the RIOT side the target application is [twr_aloha](https://github.com/RIOT-OS/RIOT/blob/master/examples/twr_aloha/README.md)
in RIOT master.
For Decawave the target application is.

### II.B) General Workflow

1. Flash the application
```shell
make -C
```

## IV) Exposed datasets

This section provides an overview of the [datasets](./datasets)

| Dataset | Description |
|---------|-------------|
| [ds-baseline.csv](./datasets/ds-baseline.csv) | TWR ranging captures |
