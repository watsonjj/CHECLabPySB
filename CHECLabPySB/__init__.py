import os
import pandas as pd
import warnings
from CHECLabPy.utils.files import create_directory

_ROOT = os.path.abspath(os.path.dirname(__file__))
_DATA = os.path.expanduser("~/Data/CHECLabPySB/data")
_PLOT = os.path.expanduser("~/Data/CHECLabPySB/plots")
_CHECS = os.path.expanduser("/Volumes/gct-jason/data_checs/")


def get_data(path):
    data_path = os.path.join(_DATA, path)
    create_directory(os.path.dirname(data_path))
    return data_path


def get_plot(path):
    plot_path = os.path.join(_PLOT, path)
    create_directory(os.path.dirname(plot_path))
    return plot_path


def get_checs(path):
    tio_path = os.path.join(_CHECS, path)
    # create_directory(os.path.dirname(tio_path))
    return tio_path


class HDF5Writer:
    def __init__(self, path):
        self.path = path
        output_dir = os.path.dirname(path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print("Created directory: {}".format(output_dir))

        self.store = self.store = pd.HDFStore(
            path, mode='w', complevel=9, complib='blosc:blosclz'
        )
        print("HDF5 Created: {}".format(self.path))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store.close()

    def write(self, **kwargs):
        for key, value in kwargs.items():
            self.store[key] = value

    def write_mapping(self, mapping):
        self.store['mapping'] = mapping
        mapping_meta = mapping.metadata
        self.store.get_storer('mapping').attrs.metadata = mapping_meta

    def write_metadata(self, **metadata):
        self.store['metadata'] = pd.DataFrame()
        self.store.get_storer('metadata').attrs.metadata = metadata


class HDF5Reader:
    def __init__(self, path):
        self.path = path

        self.store = self.store = pd.HDFStore(
            path, mode='r', complevel=9, complib='blosc:blosclz'
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store.close()

    def read(self, table):
        return self.store[table]

    def read_mapping(self):
        mapping = self.store['mapping']
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            mapping.metadata = self.store.get_storer('mapping').attrs.metadata
        return mapping

    def read_metadata(self):
        metadata = self.store.get_storer('metadata').attrs.metadata
        return metadata
