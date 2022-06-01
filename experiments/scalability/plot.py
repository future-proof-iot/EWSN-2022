#!/usr/bin/env python3
import os
import pathlib

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np

DIRECTORY = os.path.dirname(pathlib.Path(__file__))

# Set style
plt.style.use(["science"])
sns.set_context("paper")
sns.set_style("whitegrid")
COLORS = sns.color_palette("colorblind", 3)


def _df_add_twr_rates(df):
    df["uwb_req_rate"] = df["uwb_req_count"] / df["uwb_req_scheduled"]
    df["uwb_lst_count"] = (
        df["uwb_lst_scheduled"] - df["uwb_lst_timeout"] - df["uwb_lst_aborted"]
    )
    df["uwb_lst_rate"] = (df["uwb_lst_count"]) / df["uwb_lst_scheduled"]
    df["mock"] = np.where(df["nei_count"] > 13, True, False)


# Load dataset with 25% scan period
df = pd.read_csv(os.path.join("datasets", "ds-scale.csv"))
df["nei_count"].astype("int")
_df_add_twr_rates(df)

# Expected success rate
k = round(1000 / (2 * 3))
r = np.array(range(1, 14))
E = np.array([n * ((k - 1) / k) ** (n - 1) for n in r])

# Plot
fig, ax1 = plt.subplots()
## Plot Expected success rate
sns.lineplot(x=r, y=(E / r), color="black", linestyle="--", lw=2, ax=ax1)
## Plot Experimental Results
sns.lineplot(
    data=df,
    x="nei_count",
    y="uwb_lst_rate",
    ax=ax1,
    hue="backoff",
    style="backoff",
    palette="colorblind",
    markers=True,
    dashes=False,
)
ax1.set_ylabel("Success Rate")
ax1.set_xlabel("Neighbors")

# Modify Legends
legend_elements = [
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label=" 0s",
        markerfacecolor=COLORS[0],
        markersize=10,
    ),
    Line2D(
        [0],
        [0],
        marker="X",
        color="w",
        label="10s",
        markerfacecolor=COLORS[1],
        markersize=10,
    ),
    Line2D(
        [0],
        [0],
        marker="s",
        color="w",
        label="30s",
        markerfacecolor=COLORS[2],
        markersize=10,
    ),
    Line2D([0], [0], color="black", lw=4, label="0s, E(V)/n"),
]
ax1.legend(handles=legend_elements, title="TWR_Expiry Time")

plt.show(block=False)
input("Press enter to exit")
fig.savefig(f"{DIRECTORY}/figures/pepper_scale.pdf")
fig.savefig(f"{DIRECTORY}/figures/pepper_scale.pgf")
fig.savefig(f"{DIRECTORY}/figures/pepper_scale.jpg", dpi=300)
