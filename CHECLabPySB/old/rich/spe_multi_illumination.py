import os
import yaml
from tqdm import tqdm
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
from CHECLabPy.plotting.setup import Plotter


class SpectrumPlotter(Plotter):
    def plot(self, hist, edges, between, fit_x, fit, lambda_):
        lambda_str = "{:.1f}".format(lambda_)
        color = next(self.ax._get_lines.prop_cycler)['color']

        lines, _, _ = self.ax.hist(between, bins=edges, weights=hist,
                                   histtype='step',  color=color)
        self.ax.plot(fit_x, fit, color=color, label=lambda_str)

    def finish(self):
        self.add_legend(title="Mean Illumination")
        self.ax.set_xlabel("Charge (ADC.ns)")
        # self.ax.set_yscale('log')
        # self.ax.set_ylim(bottom=10)


def main():
    poi = 1920

    files = [
        "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43520_dl1.h5",
        # "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43519_dl1.h5",
        "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43518_dl1.h5",
        # "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43517_dl1.h5",
        "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43516_dl1.h5",
        # "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43515_dl1.h5",
        "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43514_dl1.h5",
        # "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43513_dl1.h5",
        "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43512_dl1.h5",
        # "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43511_dl1.h5",
        "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43510_dl1.h5",
        # "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_poly/Run43509_dl1.h5",
    ]
    readers = [DL1Reader(i) for i in files]

    output_dir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    charges = []
    desc = "Extracting charges from files"
    for r in tqdm(readers, desc=desc):
        p, c = r.select_columns(['pixel', 'charge'])
        c_pixel = c[p == poi]
        charges.append(c_pixel)
        # charges.append(c)

    fitter = GentileFitter(n_illuminations=len(charges))
    fitter.range = [-25, 170]

    fitter.apply(*charges)

    coeff = fitter.coeff
    print(yaml.dump(coeff, indent=3))

    p_spectrum = SpectrumPlotter()

    for i in range(len(readers)):
        hist = fitter.hist[i]
        edges = fitter.edges
        between = fitter.between
        fit_x = fitter.fit_x
        fit = fitter.fit[i]
        lambda_ = fitter.coeff['lambda_{}'.format(i)]
        p_spectrum.plot(hist, edges, between, fit_x, fit, lambda_)

    p_spectrum.save(os.path.join(output_dir, "multi_spectrum.pdf"))


if __name__ == '__main__':
    main()