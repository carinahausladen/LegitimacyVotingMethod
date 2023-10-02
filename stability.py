"resampling method to calculate stability of trait estimates, https://psyarxiv.com/2n6jq/"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def process_stimulus(stimulus_df):
    stimulus_sample_avgs = []
    for _ in range(150):
        sample_avgs = []
        for n in range(1, 150):
            sample = stimulus_df.sample(n, replace=True)
            sample_avg = sample.mean()
            sample_avgs.append(sample_avg)
        stimulus_sample_avgs.append(sample_avgs)
    return stimulus_sample_avgs

def get_plot_data(df, vote_name):
    df['trait_centered'] = df[vote_name].transform(lambda x: x - x.mean())
    results = process_stimulus(df['trait_centered'])

    data = []
    for i, averages in enumerate(results):
        for n, avg in enumerate(averages):
            data.append((vote_name, i, n, avg))

    df_avg = pd.DataFrame(data, columns=['which_method', 'iteration', 'n', 'average'])
    pivot_df = df_avg.pivot_table(values='average', index='iteration', columns='n', aggfunc=np.mean)

    intervals = pivot_df.apply(lambda x: (np.percentile(x, 2.5), np.percentile(x, 97.5)), axis=0)
    COS = (-0.5, 0.5)
    lower_bounds, upper_bounds = intervals.apply(lambda x: pd.Series(x[0]), axis=0), intervals.apply(
        lambda x: pd.Series(x[1]), axis=0)
    CI_within_COS = (lower_bounds >= COS[0]) & (upper_bounds <= COS[1])
    CI_within_COS_series = CI_within_COS.squeeze()

    point_of_stability = None
    for n in CI_within_COS_series.index:
        if CI_within_COS_series[n] and all(CI_within_COS_series.loc[n:]):
            point_of_stability = n
            break

    return {'intervals': intervals, 'pivot_df': pivot_df, 'point_of_stability': point_of_stability,
            'trait_name': vote_name}


df = pd.read_csv("df_legitimacy.csv")
df_wide = df.pivot(index='short_id', columns='which_method', values='rating_cvd').reset_index()
df_wide.columns.name = None  # Remove the columns' name created by pivot


# ----------------- PLOT
mv_plot_data = get_plot_data(df_wide, 'mv')
cav_plot_data = get_plot_data(df_wide, 'cav')
mbc_plot_data = get_plot_data(df_wide, 'mbc')
sv_plot_data = get_plot_data(df_wide, 'sv')


fig, axs = plt.subplots(4, figsize=(5, 5))

for i, plot_data in enumerate([mv_plot_data,cav_plot_data, mbc_plot_data,sv_plot_data]):
    axs[i].axhline(0, color='#D81B60', linewidth=1)
    axs[i].axhline(.5, color='#1E88E5', linewidth=1)
    axs[i].axhline(-.5, color='#1E88E5', linewidth=1)
    axs[i].axvline(plot_data['point_of_stability'], color='#004D40', linewidth=1)

    for col in plot_data['intervals'].columns:
        axs[i].plot([col, col], [plot_data['intervals'].loc[0, col], plot_data['intervals'].loc[1, col]], 'k--')

    for col in plot_data['pivot_df'].columns:
        axs[i].scatter([col] * len(plot_data['pivot_df']), plot_data['pivot_df'][col], s=1, alpha=.4, color='gray')

    axs[i].set_xlabel('n sampled')
    axs[i].set_ylabel(f'{plot_data["trait_name"]}')
    axs[i].set_ylim(2, -2)
    axs[i].set_xticks([0, 50, 100, 150, plot_data['point_of_stability']])


plt.tight_layout()
plt.savefig("stability_plot.pdf")
plt.show()
