import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# CSVファイルの読み込み
df = pd.read_csv("./_input/test.csv", sep="\t")


def adjust_steps(df, new_step_duration):
    steps = df["step"].unique()
    adjust_df = []
    for step in steps:
        step_df = df[df["step"] == step]
        step_in_time = step_df["time"].iloc[0]
        step_out_time = step_df["time"].iloc[-1]

        # 新しい時間ステップを作成
        adjust_time = np.linspace(step_in_time, step_out_time, new_step_duration)

        # Piecewise Linear補間を使用してデータを調整
        linear_interp = interp1d(step_df["time"], step_df["value"], kind="linear")
        adjust_value = linear_interp(adjust_time)

        # 新しいデータフレームを作成
        adjust_step_df = pd.DataFrame(
            {
                "value": adjust_value,
                "step": [step] * len(adjust_time),
            }
        )
        adjust_df.append(adjust_step_df)

    # すべてのステップを結合し、インデックスをリセット
    adjust_df = pd.concat(adjust_df).reset_index(drop=True)
    return adjust_df


# durationを等間隔にスケーリングしたデータを作成
new_df = adjust_steps(df, 5).reset_index()

# グラフをプロット
step_start_times = new_df.groupby("step")["index"].min()
min_value = new_df["value"].min()
max_value = new_df["value"].max()
fig, ax = plt.subplots()
ax.vlines(step_start_times, min_value, max_value, color="gray", alpha=0.5)
ax.plot(new_df.index, new_df["value"], label="Original Data")


# x軸のカスタムラベルを設定
ax.set_xticks(step_start_times)
ax.set_xticklabels(step_start_times.index)

plt.xlabel("Step")
plt.ylabel("Value")
plt.title("Piecewise Linear Interpolation with Steps")
plt.legend()
plt.show()
