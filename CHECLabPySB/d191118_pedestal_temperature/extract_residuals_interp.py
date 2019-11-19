from CHECLabPySB import get_data, get_checs
from CHECLabPy.core.io import HDF5Writer
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB.stats import OnlineStats, OnlineHist
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
import re
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from glob import glob
from copy import deepcopy
from IPython import embed


class PedestalDB:
    def __init__(self, paths):
        self.pedestal_instance = None

        temperature_list = []
        pedestal_list = []
        for path in paths:
            regex_r0 = re.search(r".+_tc([\d.]+)_tmc([\d.]+)_ped.tcal", path)
            temperature_primary = float(regex_r0.group(2))
            pedestal = PedestalTargetCalib.from_tcal(path)

            temperature_list.append(temperature_primary)
            pedestal_list.append(pedestal._pedestal)
            if self.pedestal_instance is None:
                self.pedestal_instance = pedestal

        self.interp_f = interp1d(
            temperature_list, pedestal_list, axis=0, fill_value="extrapolate"
        )

    def get_pedestal(self, temperature):
        self.pedestal_instance._pedestal = self.interp_f(temperature)
        return self.pedestal_instance


def main():
    r0_paths = glob(get_checs("d191118_pedestal_temperature/data/*.tio"))
    pedestaldb = PedestalDB(glob(get_checs("d191118_pedestal_temperature/lookup/*_ped.tcal")))

    data = []

    for ipath, r0_path in enumerate(r0_paths):
        print(f"Processing: {ipath+1}/{len(r0_paths)}")
        regex_r0 = re.search(r".+_tc([\d.]+)_tmc([\d.]+).tio", r0_path)
        temperature_r0_primary = float(regex_r0.group(2))

        pedestal = pedestaldb.get_pedestal(temperature_r0_primary)
        reader = TIOReader(r0_path)

        online_stats = OnlineStats()
        online_hist = OnlineHist(bins=100, range_=(-10, 10))

        # Subtract Pedestals
        desc = "Subtracting pedestal"
        for wfs in tqdm(reader, total=reader.n_events, desc=desc):
            if wfs.missing_packets:
                continue

            subtracted_tc = pedestal.subtract_pedestal(wfs, wfs.first_cell_id)
            online_stats.add_to_stats(subtracted_tc)
            online_hist.add(subtracted_tc)

        data.append(dict(
            temperature_r0_primary=temperature_r0_primary,
            mean=online_stats.mean,
            std=online_stats.std,
            hist=online_hist.hist,
            edges=online_hist.edges,
        ))

    output_path = get_data(f"d191118_pedestal_temperature/residuals_interp.h5")
    with HDF5Writer(output_path) as writer:
        writer.write(data=pd.DataFrame(data))


if __name__ == '__main__':
    main()
