#!/usr/bin/env python3
import os
from dataclasses import dataclass, field
import argparse
import logging
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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
    help="CSV file containg the merged raw measurements of the baseline experiment",
)
PARSER.add_argument(
    "--loglevel", choices=LOG_LEVELS, default="info", help="Python logger log level"
)
PARSER.add_argument(
    "--errors",
    "-e",
    choices=("absolute", "relative"),
    default=None,
    help="Show ranging errors instead of distances",
)
PARSER.add_argument(
    "--plot",
    "-p",
    dest="plot_type",
    choices=("bar", "box", "violin"),
    default="box",
    help="Plot type",
)
PARSER.add_argument(
    "--filter",
    "-f",
    nargs=2,
    type=float,
    help="Filter the range measurements by dropping all samples outside the boundary [d_min, d_max] in meters",
)
PARSER.add_argument(
    "--orient-distance",
    "-d",
    default=2.0,
    type=float,
    help="Varying orientation at fixed distance",
)


@dataclass
class FramedExperimentData:
    path: str
    df: pd.DataFrame = field(init=False)

    def __post_init__(self):
        self.df = pd.read_csv(self.path, index_col=0)
        df_columns = list(self.df.columns)
        # TODO get this from merge module
        # ensure columns are ok
        assert df_columns == [
            "env",
            "method",
            "orientation",
            "d",
            "src",
            "nei",
            "d_est",
            "d_err_absolute",
            "d_err_relative",
        ]
        # TODO ensure exactly one pair of nodes

    def filter_df(self, low: float, high: float) -> pd.DataFrame:
        return self.df[(self.df.d_est >= low) & (self.df.d_est <= high)]

    @staticmethod
    def nei_to_distance(df: pd.DataFrame, nei: str, precision: int) -> float:
        # map neighbor id to distance
        d = df[df.nei == nei].drop_duplicates(subset="d", ignore_index=True).d[0]
        return round(d, precision)


PLOT_HANDLERS = {"bar": sns.barplot, "box": sns.boxplot, "violin": sns.violinplot}


def plot_rng_data(
    exp_data: FramedExperimentData,
    errors: str = None,
    orientation: str = "front",
    plot_type: str = "box",
    rng_filter_m: Tuple[float, float] = None,
):
    sns.set(palette="colorblind")
    df = (
        exp_data.filter_df(low=rng_filter_m[0], high=rng_filter_m[1])
        if rng_filter_m
        else exp_data.df
    )
    df = df.loc[df["orientation"] == orientation]

    for node, node_data in df.groupby("src"):
        nei_list = node_data["nei"].drop_duplicates()
        assert len(nei_list) == 1, f"node {node} has more than 1 neighbor ({nei_list})"
        nei = nei_list.values[0]

        fig = plt.figure()
        legend_order = node_data["method"].drop_duplicates().sort_values().values
        with sns.axes_style("ticks"):
            ax = PLOT_HANDLERS[plot_type](
                x="d",
                y=f"d_err_{errors}" if errors else "d_est",
                dodge=True,
                data=node_data,
                hue="method",
                hue_order=legend_order,
            )
            #ax.axis("tight")
            ax.set_xlabel("d (m)")
            if errors:
                ax.set_ylabel("d_err")
            ax.legend(loc='lower left', ncol=2, bbox_to_anchor=(0,-0.4), columnspacing=3)
            ax.xaxis.set_tick_params(which="minor", bottom=False)
            ax.grid(axis='y')

            fig.suptitle(
                f"UWB ranging {'errors' + f'({errors})' if errors else 'data'} for {node} -- {nei}",
                fontsize=15,
            )
            sns.set_context("paper")
            #fig.tight_layout()


def plot_cmp_rng_data(
    exp_data: FramedExperimentData,
    errors: str = None,
    distance: float = 2.0,
    plot_type: str = "box",
    rng_filter_m: Tuple[float, float] = None,
):
    sns.set(palette="colorblind")
    df = (
        exp_data.filter_df(low=rng_filter_m[0], high=rng_filter_m[1])
        if rng_filter_m
        else exp_data.df
    )
    df = df.loc[df["d"] == distance]

    for node, node_data in df.groupby("src"):
        nei_list = node_data["nei"].drop_duplicates()
        assert len(nei_list) == 1, f"node {node} has more than 1 neighbor ({nei_list})"
        nei = nei_list.values[0]

        fig = plt.figure()
        legend_order = node_data["method"].drop_duplicates().sort_values().values
        with sns.axes_style("ticks"):
            ax = PLOT_HANDLERS[plot_type](
                x="orientation",
                y=f"d_err_{errors}" if errors else "d_est",
                dodge=True,
                data=node_data,
                hue="method",
                hue_order=legend_order,
            )
            #ax.axis("tight")
            ax.set_xlabel("orientation")
            if errors:
                ax.set_ylabel("d_err")
            ax.legend(loc='lower left', ncol=2, bbox_to_anchor=(0,-0.4), columnspacing=3)
            ax.xaxis.set_tick_params(which="minor", bottom=False)
            ax.grid(axis='y')

            fig.suptitle(
                f"UWB ranging {'errors' + f'({errors})' if errors else 'data'} for {node} -- {nei} at d={distance} m",
                fontsize=15,
            )
            sns.set_context("paper")
            #fig.tight_layout()


def __save_all_pics(output_folder="./plots"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i in plt.get_fignums():
        fig = plt.figure(i)
        output_file = f"{output_folder}/Figure_{i}"
        if os.path.isfile(output_file):
            os.remove(output_file)
        fig.savefig(
            f"{output_file}.png", format="png", bbox_inches="tight"
        )  # , transparent=True)

import matplotlib
matplotlib.use("pgf")
plt.style.use(["science"])

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'text.usetex': True,
    'pgf.rcfonts': False
})

import tikzplotlib
def save_all_pics(output_folder="./plots"):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(f"plt.get_fignums = {plt.get_fignums()}")
    for i in plt.get_fignums():
        print(f"saving {i}")
        fig = plt.figure(i)
        fig.suptitle(None)
        output_file = f"{output_folder}/Figure_{i}"
        if os.path.isfile(output_file):
            os.remove(output_file)
        fig.savefig(
            f"{output_file}.png", format="png", bbox_inches="tight"
        )  # , transparent=True)
        print(f"plt.savefig({output_file}.pgf)")
        #plt.savefig( f"{output_file}.pgf")
        fig.savefig(
            f"{output_file}.pgf", format="pgf", bbox_inches="tight"
        )
        tikzplotlib.save(f"{output_file}.tikz")


def main():
    args = PARSER.parse_args()

    # setup logger
    if args.loglevel:
        loglevel = logging.getLevelName(args.loglevel.upper())
        LOGGER.setLevel(loglevel)

    LOGGER.addHandler(LOG_HANDLER)
    LOGGER.propagate = False

    exp_data = FramedExperimentData(path=args.csv_file)

    # plot ranging errors with varying distance
    plot_rng_data(
        exp_data,
        errors=args.errors,
        rng_filter_m=args.filter,
        plot_type=args.plot_type,
    )

    # plot ranging errors with varying orientation at fixed distance d=2.0
    plot_cmp_rng_data(
        exp_data,
        errors=args.errors,
        distance=args.orient_distance,
        rng_filter_m=args.filter,
        plot_type=args.plot_type,
    )

    plt.show(block=False)
    save_all_pics("./plots")
    input("Press enter to exit")


if __name__ == "__main__":
    main()
