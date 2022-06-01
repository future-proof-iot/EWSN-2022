import matplotlib.pyplot as plt
import os
import pathlib
import pandas as pd
import seaborn as sns

plt.style.use(["science"])
sns.set_style("whitegrid")
sns.set_context("paper")
COLORS = sns.color_palette("colorblind", 5)

DIRECTORY = os.path.dirname(pathlib.Path(__file__))

def plot_pm_details(df, title):
    ax = df.plot(x="comp", kind='bar', stacked=True, title=title, color=COLORS)
    ax.legend(loc='upper center', ncol=3, fancybox=True, bbox_to_anchor=(0.5, -0.05),
          shadow=True, )
    ax.set_ylabel("Power [mW]")
    ax.set_xlabel("")
    for label in ax.get_xticklabels():
        label.set_rotation(0)

    return ax

if __name__ == "__main__":
    df_uwb = pd.read_csv(os.path.join(DIRECTORY, "datasets/uwb_pm.csv"))
    df_ble = pd.read_csv(os.path.join(DIRECTORY, "datasets/ble_pm.csv"))
    ax_uwb = plot_pm_details(df_uwb, title="")
    ax_ble = plot_pm_details(df_ble, title="")
    plt.show(block=False)
    input("Press enter to exit")
    ax_ble.get_figure().savefig(f"{DIRECTORY}/figures/ble_pm_details.pdf")
    ax_ble.get_figure().savefig(f"{DIRECTORY}/figures/ble_pm_details.jpg", dpi=300)
    ax_uwb.get_figure().savefig(f"{DIRECTORY}/figures/uwb_pm_details.pdf")
    ax_uwb.get_figure().savefig(f"{DIRECTORY}/figures/uwb_pm_details.jpg", dpi=300)
