#!/usr/bin/env python3
from __future__ import annotations
from ast import Tuple
import math
import os
from dataclasses import dataclass
import argparse
import logging
from typing import ClassVar, Dict, List

import matplotlib.pyplot as plt
import re
import seaborn as sns
import pandas as pd

plt.style.use(["science", "ieee"])


LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
LOG_LEVELS = ("debug", "info", "warning", "error", "fatal", "critical")
LOGGER = logging.getLogger("")

USAGE_EXAMPLE = """example:
"""

PARSER = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter, epilog=USAGE_EXAMPLE
)
PARSER.add_argument(
    "csv_file",
    help="CSV base file_name for guessing the 3 csv files (ble, uwb, pepper) containg raw measurements",
)
PARSER.add_argument(
    "--loglevel", choices=LOG_LEVELS, default="info", help="Python logger log level"
)
PARSER.add_argument("--plot", "-p", dest="output_folder", help="Plot output_folder")


PLOT_HANDLERS = {"bar": sns.barplot, "box": sns.boxplot, "violin": sns.violinplot}


@dataclass
class Datasets:
    DATASET_FRAMES: ClassVar[List[str]] = ["ble", "uwb", "pepper"]
    path: str
    csv_file_basename: str
    frames: Dict[str, pd.DataFrame] = None

    def csv_filename(self, data_type: str) -> str:
        ds_fname_base, ds_fname_ext = os.path.splitext(self.csv_file_basename)
        return f"{ds_fname_base}-{data_type}{ds_fname_ext}"

    def frame(self, data_type: str) -> pd.DataFrame:
        if data_type in Datasets.DATASET_FRAMES:
            return self.frames[data_type]
        return None

    def to_csv_file(self, output_path: str, data_type: str):
        self.frame(data_type).to_csv(output_path)

    def to_csv_files(self):
        for data_type in self.DATASET_FRAMES:
            csv_file = os.path.join(self.path, self.csv_filename(data_type))
            self.to_csv_file(csv_file, data_type)

    @classmethod
    def from_csv_files(cls, dataset_dir: str, csv_file_basename: str) -> Datasets:
        df_columns, _ = Datasets.data_model()
        obj = cls(path=dataset_dir, csv_file_basename=csv_file_basename)

        # load data frames
        all_df = {}
        for data_type in Datasets.DATASET_FRAMES:
            csv_file = os.path.join(dataset_dir, obj.csv_filename(data_type))
            all_df[data_type] = pd.read_csv(csv_file, index_col=0)
            assert (
                list(all_df[data_type].columns) == df_columns[data_type]
            ), f"Malformed csf file {csv_file}. Columns do not comply with [{data_type}] convetion: {df_columns[data_type]}"

        obj.frames = all_df
        return obj

    @staticmethod
    def data_model() -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        # cols
        df_columns = {}
        df_columns["ble"] = [
            "env",
            "orientation",
            "d",
            "time",
            "src",
            "nei",
            "rssi",
            "d_est",
            "d_err_absolute",
            "d_err_relative",
        ]
        df_columns["uwb"] = df_columns["ble"].copy()
        df_columns["pepper"] = [
            "env",
            "orientation",
            "d",
            "epoch",
            "src",
            "nei",
            "etl",
            "rtl",
            "uwb_exposure",
            "uwb_lst_scheduled",
            "uwb_lst_aborted",
            "uwb_lst_timeout",
            "uwb_req_scheduled",
            "uwb_req_aborted",
            "uwb_req_timeout",
            "uwb_req_count",
            "uwb_avg_d_cm",
            "uwb_avg_los",
            "uwb_avg_rssi",
            "ble_exposure",
            "ble_ble_scan_count",
            "ble_avg_rssi",
            "ble_avg_d_cm",
        ]
        # rows
        df_data = {"ble": [], "uwb": [], "pepper": []}

        return df_columns, df_data


def plot_uwb_rng_data(
    datasets: Datasets,
    env_list: List[str] = None,
    dist_bound: Tuple = [-math.inf, math.inf],
    d_critical=2.0,
):
    sns.set(palette="colorblind")

    df = datasets.frames["uwb"]
    print("UWB: ", env_list)
    if env_list:
        df = df.loc[df["env"].isin(env_list)]
    df = df.loc[df["d"].between(dist_bound[0], dist_bound[1])]
    for node, node_data in df.groupby("src"):
        nei_list = node_data["nei"].drop_duplicates()
        assert len(nei_list) == 1, f"node {node} has more than 1 neighbor ({nei_list})"
        nei = nei_list.values[0]

        fig = plt.figure()
        # legend_order = node_data["env"].drop_duplicates().sort_values().values
        with sns.axes_style("ticks"):
            ax = sns.lineplot(
                x="d",
                y=f"d_est",
                data=node_data,
                hue="env",
                style="env",
                palette="colorblind",
                ci="sd",
                hue_order=env_list,
                markers=True,
                dashes=False,
            )

            ax.axis("tight")
            ax.set_xlabel("d (m)")
            ax.set_ylabel("TWR distance (m)")
            # ax.xaxis.set_tick_params(which="minor", bottom=False)
            # FIXME: manual cleanup for legend
            lgd = ax.get_legend()
            _handles = lgd.legendHandles
            _labels = [str(x._text) for x in lgd.texts]
            for i, label in enumerate(_labels):
                if re.match(r"(?P<env>.*)_(?P<orient>\w+)", label):
                    _labels[i] = label[: label.rindex("_")]
            ax.legend(
                handles=_handles,
                labels=_labels,
                loc="lower left",
                ncol=2,
                bbox_to_anchor=(0, -0.5),
                columnspacing=1,
            )
            ax.grid(axis="y")
            # horizontal line
            ax.axhline(d_critical, linestyle=":", color="black")

            fig.suptitle(
                f"UWB ranging data for {node} $\\rightarrow$ {nei}",
                fontsize=15,
            )
            sns.set_context("paper")
            # fig.tight_layout()


def plot_ble_rng_data(
    datasets: Datasets,
    env_list: List[str] = None,
    dist_bound: Tuple = [-math.inf, math.inf],
    d_critical=2.0,
):
    sns.set(palette="colorblind")

    df = datasets.frames["ble"]
    print("BLE: ", env_list)
    if env_list:
        df = df.loc[df["env"].isin(env_list)]
    df = df.loc[df["d"].between(dist_bound[0], dist_bound[1])]
    for node, node_data in df.groupby("src"):
        nei_list = node_data["nei"].drop_duplicates()
        assert len(nei_list) == 1, f"node {node} has more than 1 neighbor ({nei_list})"
        nei = nei_list.values[0]

        fig = plt.figure()
        # legend_order = node_data["env"].drop_duplicates().sort_values().values
        # opts = {"showmeans":True} if plot_type == "box" else {}
        with sns.axes_style("ticks"):
            ax = sns.lineplot(
                x="d",
                y="rssi",
                data=node_data,
                hue="env",
                style="env",
                palette="colorblind",
                ci="sd",
                hue_order=env_list,
                markers=True,
                dashes=False,
            )
            ax.axis("tight")
            ax.set_xlabel("d (m)")
            ax.set_ylabel("rssi (dBm)")
            # ax.xaxis.set_tick_params(which="minor", bottom=False)
            ax.grid(axis="y")
            rssi_critical = df.loc[
                (df["d"] == d_critical) & (df["env"].str.startswith("los_"))
            ].rssi.mean()
            # horizontal line
            ax.axhline(rssi_critical, linestyle=":", color="black")
            # FIXME: manual cleanup for legend
            lgd = ax.get_legend()
            _handles = lgd.legendHandles
            _labels = [str(x._text) for x in lgd.texts]
            for i, label in enumerate(_labels):
                if re.match(r"(?P<env>.*)_(?P<orient>\w+)", label):
                    _labels[i] = label[: label.rindex("_")]
            ax.legend(
                handles=_handles,
                labels=_labels,
                loc="lower left",
                ncol=2,
                bbox_to_anchor=(0, -0.5),
                columnspacing=1,
            )
            fig.suptitle(
                f"BLE distribution of RSSI  for {node} $\\rightarrow$ {nei}",
                fontsize=15,
            )
            sns.set_context("paper")


def save_all_pics(output_folder="./plots", clear_title=False):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(f"plt.get_fignums = {plt.get_fignums()}")
    for i in plt.get_fignums():
        print(f"saving {i}")
        fig = plt.figure(i)
        if clear_title:
            fig.suptitle(None)
        output_file = f"{output_folder}/Figure_{i}"
        if os.path.isfile(output_file):
            os.remove(output_file)
        fig.savefig(
            f"{output_file}.png", format="png", bbox_inches="tight"
        )  # , transparent=True)
        print(f"plt.savefig({output_file}.pgf)")
        plt.savefig(f"{output_file}.pgf")


def paper_plot_and_save(
    datasets: Datasets,
    output_folder: str = "./plots",
):

    plot_uwb_rng_data(
        datasets,
        env_list=["los_front", "plexiglass_front", "whiteboard_front", "door_front"],
        # dist_bound=[-math.inf, 2.5],
    )

    plot_ble_rng_data(
        datasets,
        env_list=["los_front", "plexiglass_front", "whiteboard_front", "door_front"],
        # dist_bound=[-math.inf, 2.5],
    )

    plot_uwb_rng_data(
        datasets,
        env_list=["los_front", "body_front", "pocket_back", "backpack_front"],
    )
    plot_ble_rng_data(
        datasets,
        env_list=["los_front", "body_front", "pocket_back", "backpack_front"],
    )

    plt.show(block=False)
    save_all_pics(f"{output_folder}")


def main():
    args = PARSER.parse_args()

    # setup logger
    if args.loglevel:
        loglevel = logging.getLevelName(args.loglevel.upper())
        LOGGER.setLevel(loglevel)

    LOGGER.addHandler(LOG_HANDLER)
    LOGGER.propagate = False

    # exp_data = FramedExperimentData(path=args.csv_file)
    dataset = Datasets.from_csv_files(*os.path.split(args.csv_file))

    # set env column as a  compound key column to simplify plotting
    # FIXME: hack merge columns env and orientation to ease plotting
    for df in dataset.frames.values():
        df["env"] = df.env + "_" + df.orientation

    paper_plot_and_save(dataset, output_folder=args.output_folder)
    input("Press ENTER to exit")


if __name__ == "__main__":
    main()
