# -*- coding: iso-8859-1 -*-
"""
Python library to manage LAMMPS AveHisto file.
"""

import logging
import gzip
import pandas as pd
import numpy as np


class AveHisto(object):
    """
    LAMMPS AveHisto file reader.

    Iterator over each histogram average written in the AveHisto file, obtained
    using `fix ave/chunk` command. The latter can directly be converted into
    a pandas DataFrame using `to_pandas()` method.

    Parameters
    ----------
    filename : str, default 'bond.histo'
        LAMMPS AveHisto file.

    Examples
    --------
    """

    def __init__(self, filename="bond.histo"):

        self.filename = filename

        # Try first gzip and fall back to normal if failed
        try:
            self.f = gzip.open(filename, "rt")
            # Test the read
            self.f.readline()
            self.f.close()
            # If OK, reopen it
            self.f = gzip.open(filename, "rt")
        except IOError:
            self.f = open(filename, "r")
            # Test the read
            self.f.readline()
            self.f.close()
            # If OK, reopen it
            self.f = open(filename, "r")

        # Read the first line header
        line = self.f.readline()
        if not line.startswith("# Histogrammed data for fix"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveHisto file".format(
                    self.filename
                )
            )
        self.header = line.split("#", 1)[1].strip()

        # Read the second line header
        line = self.f.readline()
        if (
            line.strip()
            != "# TimeStep Number-of-bins Total-counts Missing-counts Min-value Max-value"
        ):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveHisto file".format(
                    self.filename
                )
            )

        # Read the third line header
        line = self.f.readline()
        if line.strip() != "# Bin Coord Count Count/Total":
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveHisto file".format(
                    self.filename
                )
            )

        self.fields = line.split("#")[1].split()

    def __del__(self):
        try:
            self.f.close()
        except Exception:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        """
        Generate and return the next configuration.

        Returns
        -------
        dict
            Information of the current configuration.
        """
        stats = {}

        line = self.f.readline()
        if line == "":
            raise StopIteration

        # First line
        values = line.split()
        stats["TimeStep"] = int(values[0])
        stats["Number-of-bins"] = int(values[1])
        stats["Total-counts"] = int(
            float(values[2])
        )  # Integer is written in scientific notation
        stats["Missing-counts"] = int(values[3])
        stats["Min-value"] = float(values[4])
        stats["Max-value"] = float(values[5])

        # Check if missing counts
        if stats["Missing-counts"] != 0:
            logging.warning(
                "Missing counts is not zero ({:d}).".format(stats["Missing-counts"])
            )

        # Next Number-of-bins lines
        for field in self.fields:
            stats[field] = []
        for _ in range(stats["Number-of-bins"]):
            line = self.f.readline()
            values = line.split()
            for field, value in zip(self.fields, values):
                try:
                    stats[field].append(int(value))
                except ValueError:
                    stats[field].append(float(value))

        return stats

    def to_pandas(self, is_norm=True):
        """
        Convert :class:`AveChunk` into a pandas DataFrame.

        Parameters
        ----------
        is_norm : bool, default 'True'
            Compute and add normalized 'Norm' column to pandas DataFrame ?

        Returns
        -------
        pandas.DataFrame
            MultiIndex pandas DataFrame, where the first index
            is the timestep and the second index is the first field.
        """
        df = pd.DataFrame([])

        for stats in self:
            iterables = [[stats["TimeStep"]], stats[self.fields[0]]]
            index = pd.MultiIndex.from_product(
                iterables, names=["TimeStep", self.fields[0]]
            )
            columns = self.fields[1:]

            df_ = pd.DataFrame(stats, index=index, columns=columns)
            if is_norm:
                df_["Norm"] = df_[self.fields[2]] / np.trapz(
                    df_[self.fields[2]], df_[self.fields[1]]
                )
            df = pd.concat([df, df_])

        return df
