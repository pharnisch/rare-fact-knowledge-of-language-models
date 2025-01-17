from pathlib import Path
import os
import json
from statistics import mean
from scipy import stats
import argparse

base_path = Path(__file__).parent.parent

prefixes = [
    "bert-base-cased_pretrained_",
    "CorBert-12-1-4096-0.000500-9-1.359077-0.713-checkpoint.pth_",
    "CorDistilBert-12-1.0-4096-0.000100-9-1.693901-0.6584-checkpoint.pth_"
]

relations = [
    "test",
    "date_of_birth",
    "place_of_birth",
    "place_of_death",
    "P17",
    "P19",
    "P20",
    "P27",
    "P30",
    "P31",
    "P36",
    "P37",
    "P39",
    "P47",
    "P101",
    "P103",
    "P106",
    "P108",
    "P127",
    "P131",
    "P136",
    "P138",
    "P140",
    "P159",
    "P176",
    "P178",
    "P190",
    "P264",
    "P276",
    "P279",
    "P361",
    "P364",
    "P407",
    "P413",
    "P449",
    "P463",
    "P495",
    "P527",
    "P530",
    "P740",
    "P937",
    "P1001",
    "P1303",
    "P1376",
    "P1412"
]

suffix = "_False_False_0_100000000_0_1_1000"

freq_type = "relative_frequency"


def scatter():
    # PARSE CONSOLE ARGUMENTS
    parser = argparse.ArgumentParser(description='Evaluation of pretrained Language Models.')
    parser.add_argument("-mi", '--model-index', action='store', nargs='?', type=int, default=0, help='Checkpoint within /models.')
    parser.add_argument("-a", "--amount", action='store', nargs='?', type=float, default=0.97)

    args = parser.parse_args()
    model_index = args.model_index
    if model_index >= 0 and model_index <= 2:
        prefix = prefixes[model_index]
    else:
        quit()

    dp = []
    for relation in relations:
        with open(f"{base_path}/metrics/standard/{prefix}{relation}{suffix}", "r") as f:
            json_text = f.read()
            metrics_dict = json.loads(json_text)

            relation_dp = metrics_dict["metrics"]["data_points"]
            dp.extend(relation_dp)

    n = len(dp)
    amount = args.amount
    print(f" ... filtering out {(1 - amount) * 100} % ...")
    border_index = int(n * amount)
    dp.sort(key=lambda x: x["rank"])
    border_rank = dp[border_index]["rank"]
    dp.sort(key=lambda x: x[freq_type])
    border_frequency = dp[border_index][freq_type]

    filtered_dp = [x for x in dp if x["rank"] <= border_rank and x[freq_type] <= border_frequency]
    filtered_n = len(filtered_dp)

    texts = []
    texts.append(r"""
        \begin{subfigure}[t]{0.45\textwidth}
        \begin{adjustbox}{width=\linewidth, height=6cm}% rescale box
            \begin{tikzpicture}
            \begin{axis}[%
                xticklabel style={rotate=-60},
                xlabel={frequency},
                xlabel near ticks,
            """)
    #texts.append(f"ymax = {border_rank * 1.75},")
    texts.append(r"""
                %xmode = log,
                ylabel={rank},
                scatter/classes={%
                a={mark=x,draw=black}}]
            \addplot[scatter,only marks,%
                scatter src=explicit symbolic]%
            table[meta=label] {
            x y label
            """)
    tmp = ""
    for p in filtered_dp:
        tmp += f"{p[freq_type]} {p['rank']} a\n"

    texts.append(tmp)
    texts.append(r"""
            };
            """)

    texts.append(r"""
            \end{axis}
                \end{tikzpicture}
        \end{adjustbox}%
            """)
    texts.append(f"\\subcaption{{Scatterplot of {model_index}, N = {n} ({filtered_n} visible).}}")
    texts.append(r"""   
        %\subcaption{Histogram.}
        \end{subfigure}%
        \hfill """)

    txt_all = "".join(texts)

    #f = open(f"scatter_plot_ALL_{model_index}.tex", "x")
    #f.write(txt_all)
    #f.close()
    #print(prefix)

    import numpy as np
    import matplotlib.pyplot as plt

    var_x = [m[freq_type] for m in filtered_dp]
    var_y = [m["rank"] for m in filtered_dp]

    plt.scatter(var_x, var_y, alpha=1, marker="x", color="black")
    plt.xlabel(freq_type)
    plt.ylabel("rank")
    plt.savefig(f"figures/{freq_type}_scatter_plot_ALL_{model_index}_{amount}.png", bbox_inches='tight')

    print(f", N = {n} ({filtered_n} visible).")

if __name__ == "__main__":
    scatter()