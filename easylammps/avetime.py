"""Python library to manage LAMMPS AveTime file."""

import gzip
import pandas as pd


class AveTime(object):
    """
    LAMMPS AveTime file reader.

    Iterator over each time average written in LAMMPS AveTime file, obtained
    using `fix ave/time` command. The latter can directly be converted into
    a pandas DataFrame using `to_pandas()` method.

    Parameters
    ----------
    filename : str, default 'rdf.time'
        LAMMPS AveTime file.
    run : str, default 'vector'
        `mode` in LAMMPS `fix ave/time` command.

    Examples
    --------
    """

    def __init__(self, filename="rdf.time", mode="vector"):

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
        if not line.startswith("# Time-averaged data for fix"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS AveTime file".format(
                    self.filename
                )
            )
        self.header = line.split("#", 1)[1].strip()

        self.mode = mode

        # Read the second line header
        line = self.f.readline()

        if self.mode == "vector":
            if line.strip() != "# TimeStep Number-of-rows":
                raise ValueError(
                    "File {:s} does not seem to be a valid LAMMPS AveTime file".format(
                        self.filename
                    )
                )

        elif self.mode == "scalar":
            if not line.startswith("# TimeStep"):
                raise ValueError(
                    "File {:s} does not seem to be a valid LAMMPS AveTime file".format(
                        self.filename
                    )
                )

            self.fields = line.split("# TimeStep")[1].split()

        # Read the third line header only if mode is vector
        if self.mode == "vector":
            line = self.f.readline()
            if not line.startswith("# Row"):
                raise ValueError(
                    "File {:s} does not seem to be a valid LAMMPS AveTime file".format(
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
        conf = {}

        line = self.f.readline()
        if line == "":
            raise StopIteration

        values = line.split()
        conf["TimeStep"] = int(values[0])

        if self.mode == "vector":

            conf["Number-of-rows"] = int(values[1])

            # Next Number-of-rows lines
            for field in self.fields:
                conf[field] = []
            for _ in range(conf["Number-of-rows"]):
                line = self.f.readline()
                values = line.split()
                for field, value in zip(self.fields, values):
                    try:
                        conf[field].append(int(value))
                    except ValueError:
                        conf[field].append(float(value))

        elif self.mode == "scalar":

            for field, value in zip(self.fields, values[1:]):
                try:
                    conf[field] = int(value)
                except ValueError:
                    conf[field] = float(value)

        return conf

    def to_pandas(self):
        """
        Convert into a pandas DataFrame.

        Returns
        -------
        pandas.DataFrame
            If `mode` == 'scalar', returns a pandas DataFrame without index.
            If `mode` == 'vector', returns a MultiIndex pandas DataFrame,
            where the first index is the timestep and the second index
            is the first field.
        """
        if self.mode == "vector":

            df = pd.DataFrame([])

            for conf in self:
                iterables = [[conf["TimeStep"]], conf[self.fields[0]]]
                index = pd.MultiIndex.from_product(
                    iterables, names=["TimeStep", self.fields[0]]
                )
                columns = self.fields[1:]

                df_ = pd.DataFrame(conf, index=index, columns=columns)
                df = pd.concat([df, df_])

        elif self.mode == "scalar":

            columns = ["TimeStep", *self.fields]
            df = pd.DataFrame(list(self), columns=columns)

        return df
