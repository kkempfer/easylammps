# -*- coding: iso-8859-1 -*-
"""
Python library to manage LAMMPS AveChunk file.
"""

import gzip
import pandas as pd


class AveChunk(object):
    """
    LAMMPS AveChunk file reader.

    Iterator over each profile average written in LAMMPS AveChunk file, obtained
    using `fix ave/chunk` command. The latter can directly be converted into
    a pandas DataFrame using `to_pandas()` method.

    Parameters
    ----------
    filename : str, default 'velocity.chunk'
        LAMMPS AveChunk file.

    Examples
    --------
    """

    def __init__(self, filename="velocity.chunk"):

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
        if not line.startswith("# Chunk-averaged data for fix"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveChunk file".format(
                    self.filename
                )
            )
        self.header = line.split("#", 1)[1].strip()

        # Read the second line header
        line = self.f.readline()
        if line.strip() != "# Timestep Number-of-chunks Total-count":
            # For some reason, TimeStep is written Timestep by default (typography mistake)
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveChunk file".format(
                    self.filename
                )
            )

        # Read the third line header
        line = self.f.readline()
        if not line.startswith("# Chunk"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveChunk file".format(
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
        stats["Number-of-chunks"] = int(values[1])

        # Next Number-of-chunks lines
        for field in self.fields:
            stats[field] = []
        for _ in range(stats["Number-of-chunks"]):
            line = self.f.readline()
            values = line.split()
            for field, value in zip(self.fields, values):
                try:
                    stats[field].append(int(value))
                except ValueError:
                    stats[field].append(float(value))

        return stats

    def to_pandas(self):
        """
        Convert into a pandas DataFrame.

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
            df = pd.concat([df, df_])

        return df
