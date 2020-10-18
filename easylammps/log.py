# -*- coding: iso-8859-1 -*-
"""
Python library to manage LAMMPS Log file.
"""

import logging
import gzip
import pandas as pd


class Log(object):
    """
    LAMMPS Log file reader.

    Iterator over each configuration written in LAMMPS Log file. The latter
    can directly be converted into a pandas DataFrame using `Log().to_pandas()`.

    Parameters
    ----------
    filename : str, default 'log.lammps'
        LAMMPS Log file.
    run : int, default 0, meaning all runs
        Extract only ith run.

    Examples
    --------
    Memory efficient iteration over each configuration:

    >>> log = Log("log.27Nov18.colloid.g++.4")
    >>> next(log)
    {'Step': 0.0, 'Temp': 1.44, 'E_pair': -2.2136534e-06, 'TotEng': 1.4383978, 'Press': 0.014383923, 'Volume': 90000.0}
    >>> next(log)
    {'Step': 1000.0, 'Temp': 1.9572809, 'E_pair': -0.00036743274, 'TotEng': 1.9547388, 'Press': 0.017982269, 'Volume': 98935.161}
    >>> next(log)
    {'Step': 2000.0, 'Temp': 2.068567, 'E_pair': -0.0010518227, 'TotEng': 2.0652168, 'Press': 0.019466739, 'Volume': 96307.439}

    Direct conversion into a pandas DataFrame:

    >>> log = Log("log.27Nov18.colloid.g++.4").to_pandas()
    >>> type(log)
    <class 'pandas.core.frame.DataFrame'>
    >>> log.head(3)
         Step      Temp    E_pair    TotEng     Press     Volume
    0     0.0  1.440000 -0.000002  1.438398  0.014384  90000.000
    1  1000.0  1.957281 -0.000367  1.954739  0.017982  98935.161
    2  2000.0  2.068567 -0.001052  2.065217  0.019467  96307.439
    """

    def __init__(self, filename="log.lammps", run=0):

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

        self.run = run

        # Seek to the start of the thermodynamic information
        self.fields = None
        self.current_run = 0
        for _ in range(self.run):
            self.seek_next_run()
        if self.run == 0:
            self.seek_next_run()

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

        line = self.f.readline()

        if line == "":
            raise StopIteration
        if line.startswith("WARNING"):
            logging.warning(line.strip())
            return next(self)
        if line.startswith("ERROR"):
            logging.error(line.strip())
            raise StopIteration
        if line.startswith("Loop"):
            if self.run == 0:
                self.seek_next_run()
                return next(self)
            else:
                raise StopIteration

        values = line.split()
        for field, value in zip(self.fields, values):
            conf[field] = float(value)

        return conf

    def seek_next_run(self):
        """
        Seek to next run and set both `self.field` and `self.current_run`.
        """
        for i, line in enumerate(self.f):
            if line.startswith("WARNING"):
                logging.warning(line.strip())
                continue
            if line.startswith("ERROR"):
                logging.error(line.strip())
                continue
            # Read the header to store in fields
            if line.startswith("Per MPI rank memory allocation") or line.startswith(
                "Memory usage per processor"
            ):
                self.fields = next(self.f).strip().split()
                self.current_run += 1
                break

    def to_pandas(self):
        """
        Convert :class:`Log` into a pandas DataFrame.
        """
        return pd.DataFrame(list(self))
