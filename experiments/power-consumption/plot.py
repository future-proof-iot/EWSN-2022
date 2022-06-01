import os
import pathlib
from pickle import MARK

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D

AVG_CURRENT_BLE = 1.69
AVG_CURRENT_UWB_RESP_NUM_FIX = 0.19
AVG_CURRENT_UWB_INIT_NUM_FIX = 0.11
AVG_CURRENT_UWB_RESP_NUM = 0.093
AVG_CURRENT_UWB_INIT_NUM = 0.096

AVG_UWB_REQUEST_MISS = 5

NEIGH_MAX = 16

SEC_PER_MIN = 60

DIRECTORY = os.path.dirname(pathlib.Path(__file__))

plt.style.use(["science"])
sns.set_style("whitegrid")
sns.set_context("paper")

COLORS = sns.color_palette("colorblind", 3)
PALLETTE = {0: COLORS[0], 10: COLORS[1], 30: COLORS[2]}
MARKERS = ["o", "X", "s"]


def _avg_current_num(
    neigh: int, backoff: int, resp_cur: float, init_cur: float
) -> float:
    """Returns theoretical backoff considering that the nodes do not fail any encounter"""
    return round(
        AVG_CURRENT_BLE
        + (resp_cur) * neigh / max(1, backoff)
        + min(max(1, backoff), AVG_UWB_REQUEST_MISS)
        * (init_cur)
        * neigh
        / max(1, backoff),
        2,
    )


def _get_num_df(tag: str, resp_cur: float, init_cur: float):
    backoff_col = np.array(
        [
            np.concatenate(
                np.array([[0, 10, 30]], dtype=int).T
                * np.ones((1, NEIGH_MAX + 1), dtype=int)
            )
        ]
    )
    neighbors_col = np.array(
        [np.concatenate([np.arange(NEIGH_MAX + 1)] * 3)], dtype=int
    )
    _iterable = (
        _avg_current_num(n, b, resp_cur, init_cur)
        for (n, b) in zip(np.concatenate(neighbors_col), np.concatenate(backoff_col))
    )
    avg_mA_col = np.array([np.fromiter(_iterable, float)])
    rows = np.concatenate((neighbors_col.T, backoff_col.T, avg_mA_col.T), axis=1)
    df = pd.DataFrame(rows, columns=["neighbors", "back-off", "avg_mA"])
    # Change type to int, TOC
    df[df.columns[0]] = df[df.columns[0]].astype(int)
    df[df.columns[1]] = df[df.columns[1]].astype(int)
    # Add 'theoretic' type
    df["type"] = tag
    return df


def plot_avg_mA(ax, df, df_th):
    for color, marker, group in zip(COLORS, MARKERS, df.groupby("back-off")):
        label = group[0]
        _df = group[1]
        sns.regplot(
            data=_df,
            x="neighbors",
            y="avg_mA",
            ax=ax,
            label=label,
            color=color,
            line_kws={"linestyle": ":"},
            marker=marker,
        )
    # Modify Legends
    legend_elements = [
        Line2D(
            [0],
            [0],
            color=COLORS[0],
            linestyle=":",
            markerfacecolor=COLORS[0],
            ms=5,
            marker=MARKERS[0],
            label="PEPPER-0s",
        ),
        Line2D(
            [0],
            [0],
            linestyle=":",
            color=COLORS[1],
            markerfacecolor=COLORS[1],
            ms=5,
            marker=MARKERS[1],
            label="PEPPER-10s",
        ),
        Line2D(
            [0],
            [0],
            color=COLORS[2],
            linestyle=":",
            markerfacecolor=COLORS[2],
            ms=5,
            marker=MARKERS[2],
            label="PEPPER-30s",
        ),
    ]
    if df_th:
        sns.lineplot(
            data=df_th,
            x="neighbors",
            y="avg_mA",
            ax=ax,
            linestyle="--",
            dashes=(None, None),
            hue="back-off",
            palette=PALLETTE,
            legend=False,
        )
        legend_elements.append(
            Line2D([0], [0], color="k", lw=1, linestyle="--", label="Datasheet")
        )
        legend_elements.append(
            Line2D([0], [0], color="k", lw=1, linestyle=":", label="Reg. Fit.")
        )
    N = len(df["neighbors"]) - 1
    sns.lineplot(
        x=list(range(0, N)),
        y=[AVG_CURRENT_BLE] * N,
        ax=ax,
        color="k",
        legend=False,
        linestyle="--",
    )

    legend_elements.append(Line2D([0], [0], color="k", label="DESIRE", linestyle="--"))

    ax.legend(
        handles=legend_elements,
        title="TWR_Expiry Time",
        title_fontsize="8",
        prop={"size": 8},
    )
    ax.set_ylabel("Average Current [mA]")
    ax.set_xlabel("Neighbors")


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(DIRECTORY, "datasets/pepper_pm.csv"))
    df_th = _get_num_df("Numeric", AVG_CURRENT_UWB_RESP_NUM, AVG_CURRENT_UWB_INIT_NUM)

    fig, ax = plt.subplots()
    plot_avg_mA(ax, df, None)
    # plot_avg_mA(ax, df, df_th,)
    plt.show(block=False)
    input("Press enter to exit")
    fig.savefig(f"{DIRECTORY}/figures/pepper_pm.pdf")
    fig.savefig(f"{DIRECTORY}/figures/pepper_pm.pgf")
    fig.savefig(f"{DIRECTORY}/figures/pepper_pm.jpg", dpi=300)
