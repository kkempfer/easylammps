# -*- coding: iso-8859-1 -*-
"""
Python library to manage LAMMPS DumpLocal file.
"""

import io
import gzip
import itertools
import pandas as pd
import numpy as np
import multiprocessing


class DumpLocal(object):
    """
    LAMMPS DumpLocal file reader.

    Iterator over each configuration written in LAMMPS DumpLocal file.
    Grouped averaged histograms of a field of the iterator can be computed, that
    effectively corresponds to the `average one` option in LAMMPS.

    Parameters
    ----------
    filename : str, default 'dump.local'
        LAMMPS Dump file.
    raw : bool, default True
        Keep raw information to transform later (for parallelisability).
    pandas : bool, default True
        Return atoms as a pandas DataFrame.

    See Also
    --------
    Dump : LAMMPS Dump file reader.

    Examples
    --------
    """

    def __init__(self, filename="dump.local", raw=True, pandas=True):

        self.filename = filename

        # Try first gzip and fall back to normal if failed
        try:
            self.f = gzip.open(filename, "rt")
            # Test the read
            line = self.f.readline().strip()
            if line != "ITEM: TIMESTEP":
                raise ValueError(
                    "File {:s} does not seem to be a valid LAMMPS DumpLocal file".format(
                        self.filename
                    )
                )
            self.f.close()
            # If OK, reopen it
            self.f = gzip.open(filename, "rt")
        except IOError:
            self.f = open(filename, "r")
            # Test the read
            line = self.f.readline().strip()
            if line != "ITEM: TIMESTEP":
                raise ValueError(
                    "File {:s} does not seem to be a valid LAMMPS DumpLocal file".format(
                        self.filename
                    )
                )
            self.f.close()
            # If OK, reopen it
            self.f = open(filename, "r")

        self.raw = raw
        self.pandas = pandas

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
        conf = {}

        # TimeStep
        line = next(self.f).strip()
        if line == "":
            raise StopIteration
        if line != "ITEM: TIMESTEP":
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS DumpLocal file".format(
                    self.filename
                )
            )
        conf["timestep"] = int(next(self.f))

        # Number of entries
        line = next(self.f).strip()
        if line != "ITEM: NUMBER OF ENTRIES":
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS DumpLocal file".format(
                    self.filename
                )
            )
        conf["nb_entries"] = int(next(self.f))

        # Box
        line = next(self.f).strip()
        if not line.startswith("ITEM: BOX BOUNDS"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS DumpLocal file".format(
                    self.filename
                )
            )
        conf["boundaries"] = line.split()[3:]
        if "xy xz yz" in line:
            is_tilt = True
        else:
            is_tilt = False

        conf["box"] = [(None, None), (None, None), (None, None)]
        conf["tilt"] = [0, 0, 0]
        for i in range(3):
            line = next(self.f)
            conf["box"][i] = (float(line.split()[0]), float(line.split()[1]))
            if is_tilt:
                conf["tilt"][i] = float(line.split()[2])

        # Entries
        line = next(self.f).strip()
        if not line.startswith("ITEM: ENTRIES"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS DumpLocal file".format(
                    self.filename
                )
            )
        conf["fields"] = line.split()[2:]

        # Keep raw information to transform later (for parallelisability)
        lines = itertools.islice(self.f, conf["nb_entries"])
        lines = list(lines)
        if self.raw:
            conf["raw"] = (conf["fields"], lines, self.pandas)
            conf["entries"] = None
        else:
            conf["entries"] = DumpLocal.raw2entries(conf["fields"], lines, self.pandas)

        return conf

    @staticmethod
    def raw2entries(fields, lines, pandas):
        """
        Transform raw information into entries.

        Parameters
        ----------
        fields : list of str
            List of entry attributes.
        lines : list of str
            Information to transform.
        pandas : bool
            Return atoms as a pandas DataFrame.

        Returns
        -------
        pandas.DataFrame or list of dict
            Entries.
        """
        # Entries is a pandas DataFrame
        if pandas:
            entries = pd.read_csv(
                io.StringIO("".join(lines)),
                " ",
                header=None,
                names=fields,
                index_col=False,
            )

        # Entries is a list of dictionnaries
        else:
            entries = []
            for line in lines:
                entry = {}
                values = line.split()
                for (field, value) in zip(fields, values):
                    try:
                        # Try for int or float
                        try:
                            entry[field] = int(value)
                        except ValueError:
                            entry[field] = float(value)
                    except ValueError:
                        entry[field] = value
                entries.append(entry)

        return entries

    def to_hist(
        self, processes=1, groupby=None, field=None, bins=10, _range=None, norm=True
    ):
        """
        Compute grouped averaged histograms of a field.

        Parameters
        ----------
        processes : int, default 1
            Number of processes.
        groupby : str, optional
            Group entries by this field.
        field : str, optional
            Entry attribute.
        bins : int, default 10
            Number of bins.
        _range : (float, float), optional
            The lower and upper range of the bins.
        norm : bool, default 'True'
            Add normalized 'Norm' column to pandas DataFrame.

        Returns
        -------
        names : list of str
            Names of the groups.
        dfs : list of pandas.DataFrame
            Histograms of the groups. MultiIndex pandas DataFrame,
            where the first index is the timestep and the second
            index is the bin index.
        """
        partial_func = functools.partial(
            DumpLocal.conf_compute_hist, *[groupby, field, bins, _range, False]
        )
        pool = multiprocessing.Pool(processes=processes)
        results = pool.imap(partial_func, self)

        # Use of dict because names may not be the same for each configuration
        d = {}

        for names, dfs in results:
            for name, df in zip(names, dfs):
                try:
                    # Elegant extraction of the timestep ?
                    timestep = df.index.get_level_values("TimeStep").values[0]
                    d[name].index.set_levels([timestep], level="TimeStep", inplace=True)
                    d[name]["Count"] += df["Count"]
                except KeyError:
                    d[name] = df[["Coord", "Count"]]

        # Do not forget to close all processes
        pool.close()
        pool.join()

        names = list(d.keys())
        dfs = list(d.values())

        for df in dfs:
            df["Count/Total"] = df["Count"] / df["Count"].sum()
            if norm:
                df["Norm"] = df["Count/Total"] / np.trapz(
                    df["Count/Total"], df["Coord"]
                )

        return names, dfs

    @staticmethod
    def conf_compute_hist(groupby, field, bins, _range, norm, conf):
        """
        Compute grouped averaged histograms of a field.

        Parameters
        ----------
        groupby : str, optional
            Group entries by this field.
        field : str, optional
            Entry attribute.
        bins : int, default 10
            Number of bins.
        _range : (float, float), optional
            The lower and upper range of the bins.
        norm : bool, default 'True'
            Add normalized 'Norm' column to pandas DataFrame.
        conf : dict
            Information of the current configuration.

        Returns
        -------
        names : list of str
            Names of the groups.
        dfs : list of pandas.DataFrame
            Histograms of the groups. MultiIndex pandas DataFrame,
            where the first index is the timestep and the second
            index is the bin index.
        """
        # Ensure entries array is a pandas DataFrame
        conf["raw"] = list(conf["raw"])
        conf["raw"][2] = True
        conf["raw"] = tuple(conf["raw"])

        # Entries array is generated here for parallelisability
        conf["entries"] = DumpLocal.raw2entries(*conf["raw"])

        names = []
        dfs = []

        for name, group in conf["entries"].groupby(groupby, sort=True):
            hist, bin_edges = np.histogram(
                group[field], bins=bins, range=_range, density=False
            )
            centered_bins = (bin_edges[:-1] + bin_edges[1:]) / 2

            iterables = [[conf["timestep"]], range(1, len(hist) + 1)]
            index = pd.MultiIndex.from_product(iterables, names=["TimeStep", "Bin"])

            df = pd.DataFrame(
                {"Coord": centered_bins, "Count": hist},
                index=index,
                columns=["Coord", "Count"],
            )
            df["Count/Total"] = df["Count"] / df["Count"].sum()
            if norm:
                df["Norm"] = df["Count/Total"] / np.trapz(
                    df["Count/Total"], df["Coord"]
                )

            names.append(name)
            dfs.append(df)

        return names, dfs
