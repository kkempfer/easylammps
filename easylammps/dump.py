"""Python library to manage LAMMPS Dump file."""

import io
import gzip
import itertools
import pandas as pd


class Dump(object):
    """
    LAMMPS Dump file reader.

    Iterator over each configuration written in LAMMPS Dump file.

    Parameters
    ----------
    filename : str, default 'dump.lammpstrj'
        LAMMPS Dump file.
    raw : bool, default 'True'
        Keep raw information to transform later (for parallelisability).
    pandas : bool, default 'True'
        Return atoms as a pandas DataFrame.
    sort : bool, default 'True'
        Sort atoms by their index.
    data : Data object, optional
        Add LAMMPS Data information.

    See Also
    --------
    DumpLocal : LAMMPS DumpLocal file reader.

    Examples
    --------
    """

    def __init__(
        self,
        filename="dump.lammpstrj",
        raw=True,
        pandas=True,
        sort=True,
        data=None,
    ):

        self.filename = filename

        # Try first gzip and fall back to normal if failed
        try:
            self.f = gzip.open(filename, "rt")
            # Test the read
            line = self.f.readline().strip()
            if line != "ITEM: TIMESTEP":
                raise ValueError(
                    "File {:s} does not seem to be a valid LAMMPS Dump file".format(
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
                    "File {:s} does not seem to be a valid LAMMPS Dump file".format(
                        self.filename
                    )
                )
            self.f.close()
            # If OK, reopen it
            self.f = open(filename, "r")

        self.raw = raw
        self.pandas = pandas
        self.sort = sort
        self.data = data

        if self.data is not None:
            raise NotImplementedError(
                "LAMMPS Data information not added to LAMMPS Dump"
            )

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
                "File {:s} does not seem to be a valid LAMMPS Dump file".format(
                    self.filename
                )
            )
        conf["timestep"] = int(next(self.f))

        # Number of atoms
        line = next(self.f).strip()
        if line != "ITEM: NUMBER OF ATOMS":
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS Dump file".format(
                    self.filename
                )
            )
        conf["nb_atoms"] = int(next(self.f))

        # Box
        line = next(self.f).strip()
        if not line.startswith("ITEM: BOX BOUNDS"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS Dump file".format(
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

        # Atoms
        line = next(self.f).strip()
        if not line.startswith("ITEM: ATOMS"):
            raise ValueError(
                "File {:s} does not seem to be a valid LAMMPS Dump file".format(
                    self.filename
                )
            )
        conf["fields"] = line.split()[2:]

        # Keep raw information to transform later (for parallelisability)
        lines = itertools.islice(self.f, conf["nb_atoms"])
        lines = list(lines)
        if self.raw:
            conf["raw"] = (conf["fields"], lines, self.pandas, self.sort)
            conf["atoms"] = None
        else:
            conf["atoms"] = Dump.raw2atoms(
                conf["fields"], lines, self.pandas, self.sort
            )

        return conf

    @staticmethod
    def raw2atoms(fields, lines, pandas, sort):
        """
        Transform raw information into atoms.

        Parameters
        ----------
        fields : list of str
            List of atom attributes.
        lines : list of str
            Information to transform.
        pandas : bool
            Return atoms as a pandas DataFrame.
        sort : bool
            Sort atoms by their index.

        Returns
        -------
        pandas.DataFrame or list of dict
            Atoms.
        """
        # Atoms is a pandas DataFrame
        if pandas:
            atoms = pd.read_csv(
                io.StringIO("".join(lines)),
                " ",
                header=None,
                names=fields,
                index_col=False,
            )
            if sort:
                if "id" not in fields:
                    raise KeyError("Cannot sort atoms, id field not found in fields")
                atoms.sort_values("id", inplace=True)

        # Atoms is a list of dictionnaries
        else:
            atoms = []
            for line in lines:
                atom = {}
                values = line.split()
                for (field, value) in zip(fields, values):
                    try:
                        # Try for int or float
                        try:
                            atom[field] = int(value)
                        except ValueError:
                            atom[field] = float(value)
                    except ValueError:
                        atom[field] = value
                atoms.append(atom)
            if sort:
                if "id" not in fields:
                    raise KeyError("Cannot sort atoms, id field not found in fields")
                atoms.sort(key=lambda atom: atom["id"])

        return atoms
