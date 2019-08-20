from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190730_pedestal import all_files
from target_calib import PedestalArrayReader
import numpy as np
import pandas as pd
from tqdm import tqdm
from IPython import embed


class ComparisonPlotter(Plotter):
    def plot(self, name, y, yerr):
        x = np.arange(y.size)
        (_, caps, _) = self.ax.errorbar(
            x, y, yerr=yerr, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

        # self.ax.plot(x, max_, '-')
        # self.ax.plot(x, y, 'x')

        self.ax.set_xticks(x)
        # Set ticks labels for x-axis
        self.ax.set_xticklabels(name, rotation=90, fontsize=4)
        self.ax.grid(alpha=0.4)
        self.ax.set_ylabel("Residuals (ADC)")




def main():
    d_list = []
    for file in all_files[2:]:
        adict = np.load(file.reduced_residuals)
        d_list.append(dict(
            name=file.name,
            mean=adict['mean'],
            std=adict['std'],
        ))
    df = pd.DataFrame(d_list)

    p_std = ComparisonPlotter()
    p_std.plot(df['name'].values, df['mean'].values, df['std'].values)
    p_std.save(get_plot("d190730_pedestal/residuals.pdf"))


if __name__ == '__main__':
    main()
