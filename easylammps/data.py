# -*- coding: iso-8859-1 -*-
"""
Python library to manage LAMMPS Data object.
"""

import logging
import itertools
import networkx as nx


supported_atom_styles = ["full", "pqeq", "molecular"]


def write_comment(f, d):
    """
    Add comment at f if d contains a comment value.

    Parameters
    ----------
    f : file object
        LAMMPS data file object.
    d : dict
        May contain a comment value.
    """
    if "comment" in d and d["comment"] is not None:
        f.write(" # {:s}\n".format(d["comment"]))
    else:
        f.write("\n")


def expand_ids(ids, idmax):
    """
    Expand lists in LAMMPS format.

    Parameters
    ----------
    ids : str
        Index (1) or indices list (3*5).
    idmax : int
        May contain a comment value.

    Returns
    -------
    tuple
        Expanded indices.
    """
    if "*" not in ids:
        return tuple([int(ids)])
    else:
        if ids.startswith("*"):
            istart = 1
        else:
            istart = int(ids.split("*")[0])
        if ids.endswith("*"):
            iend = idmax
        else:
            iend = int(ids.split("*")[1])
        return tuple(range(istart, iend + 1))


class Data(object):
    """
    LAMMPS Data object.

    Parameters
    ----------
    filename : str, optional
        LAMMPS data file.
    atom_style : str, default 'full'
        LAMMPS atom style.

    Examples
    --------
    Load an existing LAMMPS Data from file:

    >>> data = Data("data.spce")

    Box size [(xlo, xhi), (ylo, yhi), (zlo, zhi)] and shape [xy, xz, yz]:

    >>> data.box
    [(0.02645, 35.5328), (0.02645, 35.5328), (0.02641, 35.4736)]
    >>> data.tilt
    [0, 0, 0]

    List of atom, bond, angle, dihedral angle and improper types:

    >>> data.atom_types
    [{'i': 1, 'mass': 15.9994}, {'i': 2, 'mass': 1.00794}]
    >>> data.bond_types
    [{'i': 1, 'coeffs': None, 'style': None}]
    >>> data.angle_types
    [{'i': 1, 'coeffs': None, 'style': None}]

    Lists are empty if no type is defined:

    >>> data.dihedral_types
    []
    >>> data.improper_types
    []

    List of atoms, bonds, angles, dihedral angles and impropers. Nested dict-like structure:

    >>> data.atoms[0]
    {'i': 1, 'mol_i': 1, 'atom_type': {'i': 1, 'mass': 15.9994}, 'x': 12.12456, 'y': 28.09298, 'z': 22.27452, 'charge': -0.8472, 'nx': 0, 'ny': 1, 'nz': 0}
    >>> data.bonds[0]
    {'i': 1, 'bond_type': {'i': 1, 'coeffs': None, 'style': None}, 'atom1': {'i': 1, 'mol_i': 1, 'atom_type': {'i': 1, 'mass': 15.9994}, 'x': 12.12456, 'y': 28.09298, 'z': 22.27452, 'charge': -0.8472, 'nx': 0, 'ny': 1, 'nz': 0}, 'atom2': {'i': 2, 'mol_i': 1, 'atom_type': {'i': 2, 'mass': 1.00794}, 'x': 12.53683, 'y': 28.75606, 'z': 22.89928, 'charge': 0.4236, 'nx': 0, 'ny': 1, 'nz': 0}}
    >>> data.angles[0]
    {'i': 1, 'angle_type': {'i': 1, 'coeffs': None, 'style': None}, 'atom1': {'i': 2, 'mol_i': 1, 'atom_type': {'i': 2, 'mass': 1.00794}, 'x': 12.53683, 'y': 28.75606, 'z': 22.89928, 'charge': 0.4236, 'nx': 0, 'ny': 1, 'nz': 0}, 'atom2': {'i': 1, 'mol_i': 1, 'atom_type': {'i': 1, 'mass': 15.9994}, 'x': 12.12456, 'y': 28.09298, 'z': 22.27452, 'charge': -0.8472, 'nx': 0, 'ny': 1, 'nz': 0}, 'atom3': {'i': 3, 'mol_i': 1, 'atom_type': {'i': 2, 'mass': 1.00794}, 'x': 11.49482, 'y': 28.5639, 'z': 21.65678, 'charge': 0.4236, 'nx': 0, 'ny': 1, 'nz': 0}}

    Lists are empty if no structure is defined:

    >>> data.dihedrals
    []
    >>> data.impropers
    []

    Initialize an empty LAMMPS object:

    >>> data = Data()
    """

    def __init__(self, filename=None, atom_style="full"):

        self.atom_style = atom_style
        if self.atom_style not in supported_atom_styles:
            raise NotImplementedError(
                "Atom style {:s} is not supported yet".format(self.atom_style)
            )

        self.header = None

        self.box = [(None, None), (None, None), (None, None)]
        self.tilt = [0, 0, 0]

        self.atom_types = []
        self.pair_types = []
        self.bond_types = []
        self.angle_types = []
        self.dihedral_types = []
        self.improper_types = []

        self.atoms = []
        self.bonds = []
        self.angles = []
        self.dihedrals = []
        self.impropers = []

        self.filename = filename

        if self.filename:
            self.read_from_file(self.filename)

    def add_atom_type(self, i=None, mass=None, comment=None):
        """
        Add an atom type to the list.

        Parameters
        ----------
        i : int, optional
            Atom type index.
        mass : float, optional
            Atom type mass.
        comment : str, optional
            Atom type comment.
        """
        if i is None:
            i = len(self.atom_types) + 1
        atom_type = {"i": i, "mass": mass}
        if comment is not None:
            atom_type["comment"] = comment

        try:
            self.atom_types[i - 1] = atom_type
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.atom_types.extend([None] * (i - len(self.atom_types)))
            self.atom_types[i - 1] = atom_type

    def add_pair_type(self, atom_type_is, coeffs=None, style=None, comment=None):
        """
        Add a pair type to the list.

        Parameters
        ----------
        atom_type_is : tuple
            The two atom type indices composing the pair.
        coeffs : list, optional
            Pair type coefficients.
        style : str, optional
            Pair type style.
        comment : str, optional
            Pair type comment.
        """
        atom_type_1 = self.atom_types[atom_type_is[0] - 1]
        atom_type_2 = self.atom_types[atom_type_is[1] - 1]

        pair_type = {
            "atom_type_1": atom_type_1,
            "atom_type_2": atom_type_2,
            "coeffs": coeffs,
            "style": style,
        }
        if comment is not None:
            pair_type["comment"] = comment

        self.pair_types.append(pair_type)

    def add_bond_type(self, i=None, coeffs=None, style=None, comment=None):
        """
        Add a bond type to the list.

        Parameters
        ----------
        i : int, optional
            Bond type index.
        coeffs : list, optional
            Bond type coefficients.
        style : str, optional
            Bond type style.
        comment : str, optional
            Bond type comment.
        """
        if i is None:
            i = len(self.bond_types) + 1
        bond_type = {"i": i, "coeffs": coeffs, "style": style}
        if comment is not None:
            bond_type["comment"] = comment

        try:
            self.bond_types[i - 1] = bond_type
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.bond_types.extend([None] * (i - len(self.bond_types)))
            self.bond_types[i - 1] = bond_type

    def add_angle_type(self, i=None, coeffs=None, style=None, comment=None):
        """
        Add an angle type to the list.

        Parameters
        ----------
        i : int, optional
            Angle type index.
        coeffs : list, optional
            Angle type coefficients.
        style : str, optional
            Angle type style.
        comment : str, optional
            Angle type comment.
        """
        if i is None:
            i = len(self.angle_types) + 1
        angle_type = {"i": i, "coeffs": coeffs, "style": style}
        if comment is not None:
            angle_type["comment"] = comment

        try:
            self.angle_types[i - 1] = angle_type
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.angle_types.extend([None] * (i - len(self.angle_types)))
            self.angle_types[i - 1] = angle_type

    def add_dihedral_type(self, i=None, coeffs=None, style=None, comment=None):
        """
        Add a dihedral angle type to the list.

        Parameters
        ----------
        i : int, optional
            Dihedral angle type index.
        coeffs : list, optional
            Dihedral angle type coefficients.
        style : str, optional
            Dihedral angle type style.
        comment : str, optional
            Dihedral angle type comment.
        """
        if i is None:
            i = len(self.dihedral_types) + 1
        dihedral_type = {"i": i, "coeffs": coeffs, "style": style}
        if comment is not None:
            dihedral_type["comment"] = comment

        try:
            self.dihedral_types[i - 1] = dihedral_type
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.dihedral_types.extend([None] * (i - len(self.dihedral_types)))
            self.dihedral_types[i - 1] = dihedral_type

    def add_improper_type(self, i=None, coeffs=None, style=None, comment=None):
        """
        Add a improper type to the list.

        Parameters
        ----------
        i : int, optional
            Improper type index.
        coeffs : list, optional
            Improper type coefficients.
        style : str, optional
            Improper type style.
        comment : str, optional
            Improper type comment.
        """
        if i is None:
            i = len(self.improper_types) + 1
        improper_type = {"i": i, "coeffs": coeffs, "style": style}
        if comment is not None:
            improper_type["comment"] = comment

        try:
            self.improper_types[i - 1] = improper_type
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.improper_types.extend([None] * (i - len(self.improper_types)))
            self.improper_types[i - 1] = improper_type

    def add_atom(
        self,
        i=None,
        mol_i=None,
        atom_type=None,
        charge=None,
        x=None,
        y=None,
        z=None,
        nx=None,
        ny=None,
        nz=None,
        vx=None,
        vy=None,
        vz=None,
        comment=None,
    ):
        """
        Add an atom to the list.

        Parameters
        ----------
        i : int, optional
            Atom index.
        mol_i : int, optional
            Molecule index.
        atom_type : dict, optional
            Atom type.
        charge : float, optional
            Atom charge.
        x : float, optional
            Atom x coordinate.
        y : float, optional
            Atom y coordinate.
        z : float, optional
            Atom z coordinate.
        nx : float, optional
            Atom periodic image x index.
        ny : float, optional
            Atom periodic image y index.
        nz : float, optional
            Atom periodic image z index.
        vx : float, optional
            Atom velocity x coordinate.
        vy : float, optional
            Atom velocity y coordinate.
        vz : float, optional
            Atom velocity z coordinate.
        comment : str, optional
            Atom comment.
        """
        if i is None:
            i = len(self.atoms) + 1
        atom = {"i": i, "mol_i": mol_i, "atom_type": atom_type, "x": x, "y": y, "z": z}
        if charge is not None:
            atom["charge"] = charge
        if nx is not None:
            atom["nx"] = nx
        if ny is not None:
            atom["ny"] = ny
        if nz is not None:
            atom["nz"] = nz
        if vx is not None:
            atom["vx"] = vx
        if vy is not None:
            atom["vy"] = vy
        if vz is not None:
            atom["vz"] = vz
        if comment is not None:
            atom["comment"] = comment

        try:
            self.atoms[i - 1] = atom
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.atoms.extend([None] * (i - len(self.atoms)))
            self.atoms[i - 1] = atom

    def add_bond(self, atom_is, i=None, bond_type=None, comment=None):
        """
        Add a bond to the list.

        Parameters
        ----------
        atom_is : tuple
            The two atom indices composing the bond.
        i : int, optional
            Bond index.
        bond_type : dict, optional
            Bond type.
        comment : str, optional
            Bond comment.
        """
        atom1 = self.atoms[atom_is[0] - 1]
        atom2 = self.atoms[atom_is[1] - 1]

        if i is None:
            i = len(self.bonds) + 1
        bond = {"i": i, "bond_type": bond_type, "atom1": atom1, "atom2": atom2}
        if comment is not None:
            bond["comment"] = comment

        try:
            self.bonds[i - 1] = bond
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.bonds.extend([None] * (i - len(self.bonds)))
            self.bonds[i - 1] = bond

    def add_angle(self, atom_is, i=None, angle_type=None, comment=None):
        """
        Add an angle to the list.

        Parameters
        ----------
        atom_is : tuple
            The three atom indices composing the angle.
        i : int, optional
            Angle index.
        angle_type : dict, optional
            Angle type.
        comment : str, optional
            Angle comment.
        """
        atom1 = self.atoms[atom_is[0] - 1]
        atom2 = self.atoms[atom_is[1] - 1]
        atom3 = self.atoms[atom_is[2] - 1]

        if i is None:
            i = len(self.angles) + 1
        angle = {
            "i": i,
            "angle_type": angle_type,
            "atom1": atom1,
            "atom2": atom2,
            "atom3": atom3,
        }
        if comment is not None:
            angle["comment"] = comment

        try:
            self.angles[i - 1] = angle
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.angles.extend([None] * (i - len(self.angles)))
            self.angles[i - 1] = angle

    def add_dihedral(self, atom_is, i=None, dihedral_type=None, comment=None):
        """
        Add a dihedral angle to the list.

        Parameters
        ----------
        atom_is : tuple
            The four atom indices composing the dihedral angle.
        i : int, optional
            Dihedral angle index.
        dihedral_type : dict, optional
            Dihedral angle type.
        comment : str, optional
            Dihedral angle comment.
        """
        atom1 = self.atoms[atom_is[0] - 1]
        atom2 = self.atoms[atom_is[1] - 1]
        atom3 = self.atoms[atom_is[2] - 1]
        atom4 = self.atoms[atom_is[3] - 1]

        if i is None:
            i = len(self.dihedrals) + 1
        dihedral = {
            "i": i,
            "dihedral_type": dihedral_type,
            "atom1": atom1,
            "atom2": atom2,
            "atom3": atom3,
            "atom4": atom4,
        }
        if comment is not None:
            dihedral["comment"] = comment

        try:
            self.dihedrals[i - 1] = dihedral
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.dihedrals.extend([None] * (i - len(self.dihedrals)))
            self.dihedrals[i - 1] = dihedral

    def add_improper(self, atom_is, i=None, improper_type=None, comment=None):
        """
        Add an improper to the list.

        Parameters
        ----------
        atom_is : tuple
            The four atom indices composing the improper.
        i : int, optional
            Improper index.
        improper_type : dict, optional
            Improper type.
        comment : str, optional
            Improper comment.
        """
        atom1 = self.atoms[atom_is[0] - 1]
        atom2 = self.atoms[atom_is[1] - 1]
        atom3 = self.atoms[atom_is[2] - 1]
        atom4 = self.atoms[atom_is[3] - 1]

        if i is None:
            i = len(self.impropers) + 1
        improper = {
            "i": i,
            "improper_type": improper_type,
            "atom1": atom1,
            "atom2": atom2,
            "atom3": atom3,
            "atom4": atom4,
        }
        if comment is not None:
            improper["comment"] = comment

        try:
            self.impropers[i - 1] = improper
        except IndexError:
            # There are holes in the list, grow list (holes will be None and will be removed after)
            self.impropers.extend([None] * (i - len(self.impropers)))
            self.impropers[i - 1] = improper

    def remove_holes(self):
        """
        Remove holes (None).
        """
        if None in self.atom_types:
            self.atom_types = [
                atom_type for atom_type in self.atom_types if atom_type is not None
            ]
        if None in self.bond_types:
            self.bond_types = [
                bond_type for bond_type in self.bond_types if bond_type is not None
            ]
        if None in self.angle_types:
            self.angle_types = [
                angle_type for angle_type in self.angle_types if angle_type is not None
            ]
        if None in self.dihedral_types:
            self.dihedral_types = [
                dihedral_type
                for dihedral_type in self.dihedral_types
                if dihedral_type is not None
            ]
        if None in self.improper_types:
            self.improper_types = [
                improper_type
                for improper_type in self.improper_types
                if improper_type is not None
            ]
        if None in self.atoms:
            self.atoms = [atom for atom in self.atoms if atom is not None]
        if None in self.bonds:
            self.bonds = [bond for bond in self.bonds if bond is not None]
        if None in self.angles:
            self.angles = [angle for angle in self.angles if angle is not None]
        if None in self.dihedrals:
            self.dihedrals = [
                dihedral for dihedral in self.dihedrals if dihedral is not None
            ]
        if None in self.impropers:
            self.impropers = [
                improper for improper in self.impropers if improper is not None
            ]

    def read_from_file(self, filename="lammps.data"):
        """
        Constructor from LAMMPS data file.

        Parameters
        ----------
        filename : str, default 'lammps.data'
            LAMMPS data file.
        """
        nb_atoms = 0
        nb_bonds = 0
        nb_angles = 0
        nb_dihedrals = 0
        nb_impropers = 0

        nb_atom_types = 0
        nb_bond_types = 0
        nb_angle_types = 0
        nb_dihedral_types = 0
        nb_improper_types = 0

        f = open(filename, "r")

        section = "Header"
        self.header = f.readline().strip()

        for line in f:
            line = line.strip()

            if line == "":
                continue

            keyword = line.split("#")[0].strip()

            # Section change
            if (
                keyword == "Masses"
                or keyword == "Pair Coeffs"
                or keyword == "PairIJ Coeffs"
                or keyword == "Bond Coeffs"
                or keyword == "Angle Coeffs"
                or keyword == "Dihedral Coeffs"
                or keyword == "Improper Coeffs"
                or keyword == "Atoms"
                or keyword == "Velocities"
                or keyword == "Bonds"
                or keyword == "Angles"
                or keyword == "Dihedrals"
                or keyword == "Impropers"
            ):
                section = keyword
                continue

            # Header
            if section == "Header":
                if "atoms" in line:
                    nb_atoms = int(line.split()[0])
                    self.atoms = [None] * nb_atoms
                    continue
                if "bonds" in line:
                    nb_bonds = int(line.split()[0])
                    self.bonds = [None] * nb_bonds
                    continue
                if "angles" in line:
                    nb_angles = int(line.split()[0])
                    self.angles = [None] * nb_angles
                    continue
                if "dihedrals" in line:
                    nb_dihedrals = int(line.split()[0])
                    self.dihedrals = [None] * nb_dihedrals
                    continue
                if "impropers" in line:
                    nb_impropers = int(line.split()[0])
                    self.impropers = [None] * nb_impropers
                    continue

                if "atom types" in line:
                    nb_atom_types = int(line.split()[0])
                    continue
                if "bond types" in line:
                    nb_bond_types = int(line.split()[0])
                    continue
                if "angle types" in line:
                    nb_angle_types = int(line.split()[0])
                    continue
                if "dihedral types" in line:
                    nb_dihedral_types = int(line.split()[0])
                    continue
                if "improper types" in line:
                    nb_improper_types = int(line.split()[0])
                    continue

                if "xlo xhi" in line:
                    self.box[0] = (float(line.split()[0]), float(line.split()[1]))
                    continue
                if "ylo yhi" in line:
                    self.box[1] = (float(line.split()[0]), float(line.split()[1]))
                    continue
                if "zlo zhi" in line:
                    self.box[2] = (float(line.split()[0]), float(line.split()[1]))
                    continue
                if "xy xz yz" in line:
                    self.tilt = [
                        float(line.split()[0]),
                        float(line.split()[1]),
                        float(line.split()[2]),
                    ]
                    continue

            # Comment
            comment = None
            if "#" in line:
                comment = line.split("#")[1].strip()

            # Masses
            if section == "Masses":
                i = int(line.split()[0])
                mass = float(line.split()[1])

                self.add_atom_type(i=i, mass=mass, comment=comment)

            # Pair Coeffs
            if section == "Pair Coeffs":
                i = int(line.split()[0])
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[1:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c

                self.add_pair_type((i, i), coeffs=coeffs, style=style, comment=comment)

            # PairIJ Coeffs
            if section == "PairIJ Coeffs":
                i = int(line.split()[0])
                j = int(line.split()[1])
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[2:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c

                self.add_pair_type((i, j), coeffs=coeffs, style=style, comment=comment)

            # Bond Coeffs
            if section == "Bond Coeffs":
                i = int(line.split()[0])
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[1:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c

                self.add_bond_type(i=i, coeffs=coeffs, style=style, comment=comment)

            # Angle Coeffs
            if section == "Angle Coeffs":
                i = int(line.split()[0])
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[1:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c

                self.add_angle_type(i=i, coeffs=coeffs, style=style, comment=comment)

            # Dihedral Coeffs
            if section == "Dihedral Coeffs":
                i = int(line.split()[0])
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[1:]:
                    if c == "?":
                        continue
                    # Some dihedral coeffs should be keep as int
                    try:
                        coeff = int(c)
                        coeffs.append(coeff)
                    except ValueError:
                        try:
                            coeff = float(c)
                            coeffs.append(coeff)
                        except ValueError:
                            style = c

                self.add_dihedral_type(i=i, coeffs=coeffs, style=style, comment=comment)

            # Improper Coeffs
            if section == "Improper Coeffs":
                i = int(line.split()[0])
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[1:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c

                self.add_improper_type(i=i, coeffs=coeffs, style=style, comment=comment)

            # Atoms
            if section == "Atoms":
                i = int(line.split()[0])
                mol_i = int(line.split()[1])
                atom_type_i = int(line.split()[2])
                if self.atom_style == "full" or self.atom_style == "pqeq":
                    charge = float(line.split()[3])
                x = float(line.split()[4])
                y = float(line.split()[5])
                z = float(line.split()[6])
                try:
                    nx = int(line.split()[7])
                    ny = int(line.split()[8])
                    nz = int(line.split()[9])
                except (IndexError, ValueError):
                    nx = None
                    ny = None
                    nz = None

                try:
                    atom_type = self.atom_types[atom_type_i - 1]
                except IndexError:
                    # Masses not available, create empty type
                    # Atom type comment taken from atom
                    self.add_atom_type(i=atom_type_i, comment=comment)
                    atom_type = self.atom_types[atom_type_i - 1]

                self.add_atom(
                    i=i,
                    mol_i=mol_i,
                    atom_type=atom_type,
                    charge=charge,
                    x=x,
                    y=y,
                    z=z,
                    nx=nx,
                    ny=ny,
                    nz=nz,
                    comment=comment,
                )

            # Velocities
            if section == "Velocities":
                i = int(line.split()[0])
                vx = float(line.split()[1])
                vy = float(line.split()[2])
                vz = float(line.split()[3])
                self.atoms[i - 1]["vx"] = vx
                self.atoms[i - 1]["vy"] = vy
                self.atoms[i - 1]["vz"] = vz

            # Bonds
            if section == "Bonds":
                i = int(line.split()[0])
                bond_type_i = int(line.split()[1])
                atom1_i = int(line.split()[2])
                atom2_i = int(line.split()[3])

                try:
                    bond_type = self.bond_types[bond_type_i - 1]
                except IndexError:
                    # Coeffs not available, create empty type
                    # Bond type comment taken from bond
                    self.add_bond_type(i=bond_type_i, comment=comment)
                    bond_type = self.bond_types[bond_type_i - 1]

                self.add_bond(
                    (atom1_i, atom2_i), i=i, bond_type=bond_type, comment=comment
                )

            # Angles
            if section == "Angles":
                i = int(line.split()[0])
                angle_type_i = int(line.split()[1])
                atom1_i = int(line.split()[2])
                atom2_i = int(line.split()[3])
                atom3_i = int(line.split()[4])

                try:
                    angle_type = self.angle_types[angle_type_i - 1]
                except IndexError:
                    # Coeffs not available, create empty type
                    # Angle type comment taken from angle
                    self.add_angle_type(i=angle_type_i, comment=comment)
                    angle_type = self.angle_types[angle_type_i - 1]

                self.add_angle(
                    (atom1_i, atom2_i, atom3_i),
                    i=i,
                    angle_type=angle_type,
                    comment=comment,
                )

            # Dihedrals
            if section == "Dihedrals":
                i = int(line.split()[0])
                dihedral_type_i = int(line.split()[1])
                atom1_i = int(line.split()[2])
                atom2_i = int(line.split()[3])
                atom3_i = int(line.split()[4])
                atom4_i = int(line.split()[5])

                try:
                    dihedral_type = self.dihedral_types[dihedral_type_i - 1]
                except IndexError:
                    # Coeffs not available, create empty type
                    # Dihedral type comment taken from dihedral
                    self.add_dihedral_type(i=dihedral_type_i, comment=comment)
                    dihedral_type = self.dihedral_types[dihedral_type_i - 1]

                self.add_dihedral(
                    (atom1_i, atom2_i, atom3_i, atom4_i),
                    i=i,
                    dihedral_type=dihedral_type,
                    comment=comment,
                )

            # Impropers
            if section == "Impropers":
                i = int(line.split()[0])
                improper_type_i = int(line.split()[1])
                atom1_i = int(line.split()[2])
                atom2_i = int(line.split()[3])
                atom3_i = int(line.split()[4])
                atom4_i = int(line.split()[5])

                try:
                    improper_type = self.improper_types[improper_type_i - 1]
                except IndexError:
                    # Coeffs not available, create empty type
                    # Improper type comment taken from improper
                    self.add_improper_type(i=improper_type_i, comment=comment)
                    improper_type = self.improper_types[improper_type_i - 1]

                self.add_improper(
                    (atom1_i, atom2_i, atom3_i, atom4_i),
                    i=i,
                    improper_type=improper_type,
                    comment=comment,
                )

        f.close()

        # Remove holes (None)
        self.remove_holes()

        # Sort pair types by first atom type then by second atom type
        self.pair_types.sort(
            key=lambda pair_type: (
                pair_type["atom_type_1"]["i"],
                pair_type["atom_type_2"]["i"],
            )
        )

        # Validate numbers
        if len(self.atoms) != nb_atoms:
            raise ValueError("Number of atoms is not coherent")
        if len(self.bonds) != nb_bonds:
            raise ValueError("Number of bonds is not coherent")
        if len(self.angles) != nb_angles:
            raise ValueError("Number of angles is not coherent")
        if len(self.dihedrals) != nb_dihedrals:
            raise ValueError("Number of dihedrals is not coherent")
        if len(self.impropers) != nb_impropers:
            raise ValueError("Number of impropers is not coherent")
        if len(self.atom_types) != nb_atom_types:
            raise ValueError("Number of atom types is not coherent")
        if len(self.bond_types) != nb_bond_types:
            raise ValueError("Number of bond types is not coherent")
        if len(self.angle_types) != nb_angle_types:
            raise ValueError("Number of angle types is not coherent")
        if len(self.dihedral_types) != nb_dihedral_types:
            raise ValueError("Number of dihedral types is not coherent")
        if len(self.improper_types) != nb_improper_types:
            raise ValueError("Number of improper types is not coherent")

    def read_pair_coeffs_from_file(self, filename="pair.coeffs"):
        """
        Read pair coefficients from a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'pair.coeffs'
            LAMMPS input file.
        """
        nb_atom_types = len(self.atom_types)
        self.pair_types = []

        f = open(filename, "r")

        for line in f:
            if not line.startswith("pair_coeff"):
                continue
            # Expand indices, if using wild-cards
            ids_i = expand_ids(line.split()[1], nb_atom_types)
            ids_j = expand_ids(line.split()[2], nb_atom_types)
            for i, j in itertools.product(ids_i, ids_j):
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[3:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c
                # Comment
                comment = None
                if "#" in line:
                    comment = line.split("#")[1].strip()

                # Order atom types
                if i <= j:
                    self.add_pair_type(
                        (i, j), coeffs=coeffs, style=style, comment=comment
                    )
                else:
                    self.add_pair_type(
                        (j, i), coeffs=coeffs, style=style, comment=comment
                    )

        f.close()

        # Remove duplicates
        self.pair_types = [
            pair_type
            for n, pair_type in enumerate(self.pair_types)
            if pair_type not in self.pair_types[n + 1 :]
        ]

        # Sort pair types by first atom type then by second atom type
        self.pair_types.sort(
            key=lambda pair_type: (
                pair_type["atom_type_1"]["i"],
                pair_type["atom_type_2"]["i"],
            )
        )

    def read_bond_coeffs_from_file(self, filename="bond.coeffs"):
        """
        Read bond coefficients from a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'bond.coeffs'
            LAMMPS input file.
        """
        nb_bond_types = len(self.bond_types)
        self.bond_types = []

        f = open(filename, "r")

        for line in f:
            if not line.startswith("bond_coeff"):
                continue
            # Expand indices, if using wild-cards
            ids = expand_ids(line.split()[1], nb_bond_types)
            for i in ids:
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[2:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c
                # Comment
                comment = None
                if "#" in line:
                    comment = line.split("#")[1].strip()

                self.add_bond_type(i=i, coeffs=coeffs, style=style, comment=comment)

        f.close()

        # Do not forget to update bonds
        for bond in self.bonds:
            bond_type_i = bond["bond_type"]["i"]
            bond["bond_type"] = self.bond_types[bond_type_i - 1]

        # Remove holes (None)
        if None in self.bond_types:
            self.bond_types = [
                bond_type for bond_type in self.bond_types if bond_type is not None
            ]

    def read_angle_coeffs_from_file(self, filename="angle.coeffs"):
        """
        Read angle coefficients from a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'angle.coeffs'
            LAMMPS input file.
        """
        nb_angle_types = len(self.angle_types)
        self.angle_types = []

        f = open(filename, "r")

        for line in f:
            if not line.startswith("angle_coeff"):
                continue
            # Expand indices, if using wild-cards
            ids = expand_ids(line.split()[1], nb_angle_types)
            for i in ids:
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[2:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c
                # Comment
                comment = None
                if "#" in line:
                    comment = line.split("#")[1].strip()

                self.add_angle_type(i=i, coeffs=coeffs, style=style, comment=comment)

        f.close()

        # Do not forget to update angles
        for angle in self.angles:
            angle_type_i = angle["angle_type"]["i"]
            angle["angle_type"] = self.angle_types[angle_type_i - 1]

        # Remove holes (None)
        if None in self.angle_types:
            self.angle_types = [
                angle_type for angle_type in self.angle_types if angle_type is not None
            ]

    def read_dihedral_coeffs_from_file(self, filename="dihedral.coeffs"):
        """
        Read dihedral coefficients from a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'dihedral.coeffs'
            LAMMPS input file.
        """
        nb_dihedral_types = len(self.dihedral_types)
        self.dihedral_types = []

        f = open(filename, "r")

        for line in f:
            if not line.startswith("dihedral_coeff"):
                continue
            # Expand indices, if using wild-cards
            ids = expand_ids(line.split()[1], nb_dihedral_types)
            for i in ids:
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[2:]:
                    if c == "?":
                        continue
                    # Some dihedral coeffs should be keep as int
                    try:
                        coeff = int(c)
                        coeffs.append(coeff)
                    except ValueError:
                        try:
                            coeff = float(c)
                            coeffs.append(coeff)
                        except ValueError:
                            style = c
                # Comment
                comment = None
                if "#" in line:
                    comment = line.split("#")[1].strip()

                self.add_dihedral_type(i=i, coeffs=coeffs, style=style, comment=comment)

        f.close()

        # Do not forget to update dihedrals
        for dihedral in self.dihedrals:
            dihedral_type_i = dihedral["dihedral_type"]["i"]
            dihedral["dihedral_type"] = self.dihedral_types[dihedral_type_i - 1]

        # Remove holes (None)
        if None in self.dihedral_types:
            self.dihedral_types = [
                dihedral_type
                for dihedral_type in self.dihedral_types
                if dihedral_type is not None
            ]

    def read_improper_coeffs_from_file(self, filename="improper.coeffs"):
        """
        Read improper coefficients from a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'improper.coeffs'
            LAMMPS input file.
        """
        nb_improper_types = len(self.improper_types)
        self.improper_types = []

        f = open(filename, "r")

        for line in f:
            if not line.startswith("improper_coeff"):
                continue
            # Expand indices, if using wild-cards
            ids = expand_ids(line.split()[1], nb_improper_types)
            for i in ids:
                # Get all float coeffs
                coeffs = []
                # Style can be a string at the first place
                style = None
                for c in line.split("#")[0].split()[2:]:
                    if c == "?":
                        continue
                    try:
                        coeff = float(c)
                        coeffs.append(coeff)
                    except ValueError:
                        style = c
                # Comment
                comment = None
                if "#" in line:
                    comment = line.split("#")[1].strip()

                self.add_improper_type(i=i, coeffs=coeffs, style=style, comment=comment)

        f.close()

        # Do not forget to update impropers
        for improper in self.impropers:
            improper_type_i = improper["improper_type"]["i"]
            improper["improper_type"] = self.improper_types[improper_type_i - 1]

        # Remove holes (None)
        if None in self.improper_types:
            self.improper_types = [
                improper_type
                for improper_type in self.improper_types
                if improper_type is not None
            ]

    def write_to_file(self, filename="lammps.data", is_coeffs=False):
        """
        Write Data to a LAMMPS data file.

        Parameters
        ----------
        filename : str, default 'lammps.data'
            LAMMPS data file.
        is_coeffs : bool, default 'False'
            Include force field information ?
        """
        f = open(filename, "w")

        # Header
        f.write("{:s}\n\n".format(self.header))
        f.write("{:d} atoms\n".format(len(self.atoms)))
        if len(self.bonds) > 0:
            f.write("{:d} bonds\n".format(len(self.bonds)))
        if len(self.angles) > 0:
            f.write("{:d} angles\n".format(len(self.angles)))
        if len(self.dihedrals) > 0:
            f.write("{:d} dihedrals\n".format(len(self.dihedrals)))
        if len(self.impropers) > 0:
            f.write("{:d} impropers\n".format(len(self.impropers)))
        f.write("\n")

        f.write("{:d} atom types\n".format(len(self.atom_types)))
        if len(self.bond_types) > 0:
            f.write("{:d} bond types\n".format(len(self.bond_types)))
        if len(self.angle_types) > 0:
            f.write("{:d} angle types\n".format(len(self.angle_types)))
        if len(self.dihedral_types) > 0:
            f.write("{:d} dihedral types\n".format(len(self.dihedral_types)))
        if len(self.improper_types) > 0:
            f.write("{:d} improper types\n".format(len(self.improper_types)))
        f.write("\n")

        f.write("{:f} {:f} xlo xhi\n".format(*self.box[0]))
        f.write("{:f} {:f} ylo yhi\n".format(*self.box[1]))
        f.write("{:f} {:f} zlo zhi\n".format(*self.box[2]))
        if self.tilt != [0.0, 0.0, 0.0]:
            f.write("{:f} {:f} {:f} xy xz yz\n".format(*self.tilt))
        f.write("\n")

        # Masses
        if self.atom_types != []:
            f.write("Masses\n\n")
            for atom_type in self.atom_types:
                f.write("{:4d} {:9.6f}".format(atom_type["i"], atom_type["mass"]))
                write_comment(f, atom_type)
            f.write("\n")

        # Coeffs
        if is_coeffs:

            # Pair Coeffs
            if [
                pair_type
                for pair_type in self.pair_types
                if pair_type["atom_type_1"]["i"] == pair_type["atom_type_2"]["i"]
            ] != []:
                f.write("Pair Coeffs")
                nb_styles = len(set([d["style"] for d in self.pair_types]))
                if nb_styles == 1:
                    style = self.pair_types[0]["style"]
                    if style is not None:
                        f.write(" # {:s}".format(style))
                f.write("\n\n")

                for pair_type in self.pair_types:
                    if pair_type["atom_type_1"]["i"] != pair_type["atom_type_2"]["i"]:
                        continue
                    f.write("{:4d}".format(pair_type["atom_type_1"]["i"]))
                    if nb_styles > 1:
                        f.write(" {:7s}".format(pair_type["style"]))
                    if pair_type["coeffs"] is not None:
                        for coeff in pair_type["coeffs"]:
                            f.write(" {:9.4f}".format(coeff))
                    write_comment(f, pair_type)
                f.write("\n")

            # PairIJ Coeffs
            if [
                pair_type
                for pair_type in self.pair_types
                if pair_type["atom_type_1"]["i"] != pair_type["atom_type_2"]["i"]
            ] != []:
                f.write("PairIJ Coeffs")
                nb_styles = len(set([d["style"] for d in self.pair_types]))
                if nb_styles == 1:
                    style = self.pair_types[0]["style"]
                    if style is not None:
                        f.write(" # {:s}".format(style))
                f.write("\n\n")

                for pair_type in self.pair_types:
                    if pair_type["atom_type_1"]["i"] == pair_type["atom_type_2"]["i"]:
                        continue
                    f.write(
                        "{:4d} {:4d}".format(
                            pair_type["atom_type_1"]["i"], pair_type["atom_type_2"]["i"]
                        )
                    )
                    if nb_styles > 1:
                        f.write(" {:7s}".format(pair_type["style"]))
                    if pair_type["coeffs"] is not None:
                        for coeff in pair_type["coeffs"]:
                            f.write(" {:9.4f}".format(coeff))
                    write_comment(f, pair_type)
                f.write("\n")

            # Bond Coeffs
            if self.bond_types != []:
                f.write("Bond Coeffs")
                nb_styles = len(set([d["style"] for d in self.bond_types]))
                if nb_styles == 1:
                    style = self.bond_types[0]["style"]
                    if style is not None:
                        f.write(" # {:s}".format(style))
                f.write("\n\n")

                for bond_type in self.bond_types:
                    f.write("{:4d}".format(bond_type["i"]))
                    if nb_styles > 1:
                        f.write(" {:7s}".format(bond_type["style"]))
                    if bond_type["coeffs"] is not None:
                        for coeff in bond_type["coeffs"]:
                            f.write(" {:9.4f}".format(coeff))
                    write_comment(f, bond_type)
                f.write("\n")

            # Angle Coeffs
            if self.angle_types != []:
                f.write("Angle Coeffs")
                nb_styles = len(set([d["style"] for d in self.angle_types]))
                if nb_styles == 1:
                    style = self.angle_types[0]["style"]
                    if style is not None:
                        f.write(" # {:s}".format(style))
                f.write("\n\n")

                for angle_type in self.angle_types:
                    f.write("{:4d}".format(angle_type["i"]))
                    if nb_styles > 1:
                        f.write(" {:7s}".format(angle_type["style"]))
                    if angle_type["coeffs"] is not None:
                        for coeff in angle_type["coeffs"]:
                            f.write(" {:9.4f}".format(coeff))
                    write_comment(f, angle_type)
                f.write("\n")

            # Dihedral Coeffs
            if self.dihedral_types != []:
                f.write("Dihedral Coeffs")
                nb_styles = len(set([d["style"] for d in self.dihedral_types]))
                if nb_styles == 1:
                    style = self.dihedral_types[0]["style"]
                    if style is not None:
                        f.write(" # {:s}".format(style))
                f.write("\n\n")

                for dihedral_type in self.dihedral_types:
                    f.write("{:4d}".format(dihedral_type["i"]))
                    if nb_styles > 1:
                        f.write(" {:7s}".format(dihedral_type["style"]))
                    if dihedral_type["coeffs"] is not None:
                        for coeff in dihedral_type["coeffs"]:
                            f.write(" {:9.4f}".format(coeff))
                    write_comment(f, dihedral_type)
                f.write("\n")

            # Improper Coeffs
            if self.improper_types != []:
                f.write("Improper Coeffs")
                nb_styles = len(set([d["style"] for d in self.improper_types]))
                if nb_styles == 1:
                    style = self.improper_types[0]["style"]
                    if style is not None:
                        f.write(" # {:s}".format(style))
                f.write("\n\n")

                for improper_type in self.improper_types:
                    f.write("{:4d}".format(improper_type["i"]))
                    if nb_styles > 1:
                        f.write(" {:7s}".format(improper_type["style"]))
                    if improper_type["coeffs"] is not None:
                        for coeff in improper_type["coeffs"]:
                            f.write(" {:9.4f}".format(coeff))
                    write_comment(f, improper_type)
                f.write("\n")

        # Atoms
        if self.atoms != []:
            f.write("Atoms # {:s}\n\n".format(self.atom_style))
            for atom in self.atoms:
                f.write(
                    "{:7d} {:7d} {:7d}".format(
                        atom["i"], atom["mol_i"], atom["atom_type"]["i"]
                    )
                )
                if self.atom_style == "full" or self.atom_style == "pqeq":
                    f.write(" {:9.6f}".format(atom["charge"]))
                f.write(
                    " {:13.6e} {:13.6e} {:13.6e}".format(
                        atom["x"], atom["y"], atom["z"]
                    )
                )
                if "nx" in atom and "ny" in atom and "nz" in atom:
                    f.write(
                        " {:d} {:d} {:d}".format(atom["nx"], atom["ny"], atom["nz"])
                    )
                write_comment(f, atom)
            f.write("\n")

        # Velocities
        if self.atoms != [] and (
            "vx" in self.atoms[0] and "vy" in self.atoms[0] and "vz" in self.atoms[0]
        ):
            f.write("Velocities\n\n")
            for atom in self.atoms:
                f.write(
                    "{:7d} {:13.6e} {:13.6e} {:13.6e}".format(
                        atom["i"], atom["vx"], atom["vy"], atom["vz"]
                    )
                )
                write_comment(f, atom)
            f.write("\n")

        # Bonds
        if self.bonds != []:
            f.write("Bonds\n\n")
            for bond in self.bonds:
                f.write(
                    "{:7d} {:7d} {:7d} {:7d}".format(
                        bond["i"],
                        bond["bond_type"]["i"],
                        bond["atom1"]["i"],
                        bond["atom2"]["i"],
                    )
                )
                write_comment(f, bond)
            f.write("\n")

        # Angles
        if self.angles != []:
            f.write("Angles\n\n")
            for angle in self.angles:
                f.write(
                    "{:7d} {:7d} {:7d} {:7d} {:7d}".format(
                        angle["i"],
                        angle["angle_type"]["i"],
                        angle["atom1"]["i"],
                        angle["atom2"]["i"],
                        angle["atom3"]["i"],
                    )
                )
                write_comment(f, angle)
            f.write("\n")

        # Dihedrals
        if self.dihedrals != []:
            f.write("Dihedrals\n\n")
            for dihedral in self.dihedrals:
                f.write(
                    "{:7d} {:7d} {:7d} {:7d} {:7d} {:7d}".format(
                        dihedral["i"],
                        dihedral["dihedral_type"]["i"],
                        dihedral["atom1"]["i"],
                        dihedral["atom2"]["i"],
                        dihedral["atom3"]["i"],
                        dihedral["atom4"]["i"],
                    )
                )
                write_comment(f, dihedral)
            f.write("\n")

        # Impropers
        if self.impropers != []:
            f.write("Impropers\n\n")
            for improper in self.impropers:
                f.write(
                    "{:7d} {:7d} {:7d} {:7d} {:7d} {:7d}".format(
                        improper["i"],
                        improper["improper_type"]["i"],
                        improper["atom1"]["i"],
                        improper["atom2"]["i"],
                        improper["atom3"]["i"],
                        improper["atom4"]["i"],
                    )
                )
                write_comment(f, improper)
            f.write("\n")

        f.close()

    def write_pair_coeffs_to_file(self, filename="pair.coeffs"):
        """
        Write pair coefficients to a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'pair.coeffs'
            LAMMPS input file.
        """
        if self.pair_types == []:
            return logging.info(
                "No pair type, no need to write {:s} file.".format(filename)
            )

        f = open(filename, "w")

        nb_styles = len(set([d["style"] for d in self.pair_types]))
        for pair_type in self.pair_types:
            f.write(
                "pair_coeff {:4d} {:4d}".format(
                    pair_type["atom_type_1"]["i"], pair_type["atom_type_2"]["i"]
                )
            )
            if nb_styles > 1:
                f.write(" {:7s}".format(pair_type["style"]))
            if pair_type["coeffs"] is not None:
                for coeff in pair_type["coeffs"]:
                    f.write(" {:9.4f}".format(coeff))
            else:
                f.write(" ?")
            write_comment(f, pair_type)

        f.close()

    def write_bond_coeffs_to_file(self, filename="bond.coeffs"):
        """
        Write bond coefficients to a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'bond.coeffs'
            LAMMPS input file.
        """
        if self.bond_types == []:
            return logging.info(
                "No bond type, no need to write {:s} file.".format(filename)
            )

        f = open(filename, "w")

        nb_styles = len(set([d["style"] for d in self.bond_types]))
        for bond_type in self.bond_types:
            f.write("bond_coeff {:4d}".format(bond_type["i"]))
            if nb_styles > 1:
                f.write(" {:7s}".format(bond_type["style"]))
            if bond_type["coeffs"] is not None:
                for coeff in bond_type["coeffs"]:
                    f.write(" {:9.4f}".format(coeff))
            else:
                f.write(" ?")
            write_comment(f, bond_type)

        f.close()

    def write_angle_coeffs_to_file(self, filename="angle.coeffs"):
        """
        Write angle coefficients to a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'angle.coeffs'
            LAMMPS input file.
        """
        if self.angle_types == []:
            return logging.info(
                "No angle type, no need to write {:s} file.".format(filename)
            )

        f = open(filename, "w")

        nb_styles = len(set([d["style"] for d in self.angle_types]))
        for angle_type in self.angle_types:
            f.write("angle_coeff {:4d}".format(angle_type["i"]))
            if nb_styles > 1:
                f.write(" {:7s}".format(angle_type["style"]))
            if angle_type["coeffs"] is not None:
                for coeff in angle_type["coeffs"]:
                    f.write(" {:9.4f}".format(coeff))
            else:
                f.write(" ?")
            write_comment(f, angle_type)

        f.close()

    def write_dihedral_coeffs_to_file(self, filename="dihedral.coeffs"):
        """
        Write dihedral coefficients to a LAMMPS input file.
        
        Parameters
        ----------
        filename : str, default 'dihedral.coeffs'
            LAMMPS input file.
        """
        if self.dihedral_types == []:
            return logging.info(
                "No dihedral type, no need to write {:s} file.".format(filename)
            )

        f = open(filename, "w")

        nb_styles = len(set([d["style"] for d in self.dihedral_types]))
        for dihedral_type in self.dihedral_types:
            f.write("dihedral_coeff {:4d}".format(dihedral_type["i"]))
            if nb_styles > 1:
                f.write(" {:7s}".format(dihedral_type["style"]))
            if dihedral_type["coeffs"] is not None:
                for coeff in dihedral_type["coeffs"]:
                    f.write(" {:9.4f}".format(coeff))
            else:
                f.write(" ?")
            write_comment(f, dihedral_type)

        f.close()

    def write_improper_coeffs_to_file(self, filename="improper.coeffs"):
        """
        Write improper coefficients to a LAMMPS input file.

        Parameters
        ----------
        filename : str, default 'improper.coeffs'
            LAMMPS input file.
        """
        if self.improper_types == []:
            return logging.info(
                "No improper type, no need to write {:s} file.".format(filename)
            )

        f = open(filename, "w")

        nb_styles = len(set([d["style"] for d in self.improper_types]))
        for improper_type in self.improper_types:
            f.write("improper_coeff {:4d}".format(improper_type["i"]))
            if nb_styles > 1:
                f.write(" {:7s}".format(improper_type["style"]))
            if improper_type["coeffs"] is not None:
                for coeff in improper_type["coeffs"]:
                    f.write(" {:9.4f}".format(coeff))
            else:
                f.write(" ?")
            write_comment(f, improper_type)

        f.close()

    def auto_comment_from_atom_types(self, sep="-"):
        """
        Automatic comment by joining atom types comments.

        Parameters
        ----------
        sep : str, default '-'
            Separator used by `join()` method.
        """
        for pair_type in self.pair_types:
            pair_type["comment"] = sep.join(
                (
                    pair_type["atom_type_1"]["comment"],
                    pair_type["atom_type_2"]["comment"],
                )
            )
        for atom in self.atoms:
            atom["comment"] = atom["atom_type"]["comment"]
        for bond in self.bonds:
            atom1 = bond["atom1"]
            atom2 = bond["atom2"]
            bond["comment"] = sep.join(
                (atom1["atom_type"]["comment"], atom2["atom_type"]["comment"])
            )
            bond["bond_type"]["comment"] = bond["comment"]
        for angle in self.angles:
            atom1 = angle["atom1"]
            atom2 = angle["atom2"]
            atom3 = angle["atom3"]
            angle["comment"] = sep.join(
                (
                    atom1["atom_type"]["comment"],
                    atom2["atom_type"]["comment"],
                    atom3["atom_type"]["comment"],
                )
            )
            angle["angle_type"]["comment"] = angle["comment"]
        for dihedral in self.dihedrals:
            atom1 = dihedral["atom1"]
            atom2 = dihedral["atom2"]
            atom3 = dihedral["atom3"]
            atom4 = dihedral["atom4"]
            dihedral["comment"] = sep.join(
                (
                    atom1["atom_type"]["comment"],
                    atom2["atom_type"]["comment"],
                    atom3["atom_type"]["comment"],
                    atom4["atom_type"]["comment"],
                )
            )
            dihedral["dihedral_type"]["comment"] = dihedral["comment"]
        for improper in self.impropers:
            atom1 = improper["atom1"]
            atom2 = improper["atom2"]
            atom3 = improper["atom3"]
            atom4 = improper["atom4"]
            improper["comment"] = sep.join(
                (
                    atom1["atom_type"]["comment"],
                    atom2["atom_type"]["comment"],
                    atom3["atom_type"]["comment"],
                    atom4["atom_type"]["comment"],
                )
            )
            improper["improper_type"]["comment"] = improper["comment"]

    def to_networkx(self):
        """
        Convert Data into a NetworkX Graph.

        Returns
        -------
        networkx.Graph
            Atoms are assigned as nodes. Bonds are assigned as edges.
        """
        G = nx.Graph()
        G.add_nodes_from([(atom["i"], atom) for atom in self.atoms])
        G.add_edges_from(
            [
                (
                    bond["atom1"]["i"],
                    bond["atom2"]["i"],
                    {
                        key: value
                        for key, value in bond.items()
                        if key != "atom1" and key != "atom2"
                    },
                )
                for bond in self.bonds
            ]
        )
        return G

    def reset_mol_i(self):
        """
        Reset all molecule indices in atoms list by checking bond topology.
        """
        for atom in self.atoms:
            atom["mol_i"] = None

        G = self.to_networkx()

        mol_i = 0
        for node in G.nodes:
            if G.nodes[node]["mol_i"] is None:
                mol_i += 1
                G.nodes[node]["mol_i"] = mol_i
                self.atoms[node - 1]["mol_i"] = mol_i
                for descendant in nx.descendants(G, node):
                    G.nodes[descendant]["mol_i"] = mol_i
                    self.atoms[descendant - 1]["mol_i"] = mol_i

    def reset_atom_types(self):
        """
        Reset all atom types.

        Matches `mass` and `comment` (if available) of atom types.
        If not empty, pair types are updated accordingly.
        """
        self.atom_types = []

        for atom in self.atoms:
            mass = atom["atom_type"]["mass"]
            if "comment" in atom["atom_type"]:
                comment = atom["atom_type"]["comment"]
            else:
                comment = None

            # Try to find atom type in the list
            not_new = False
            for atom_type in self.atom_types:
                if atom_type["mass"] == mass:
                    if (
                        "comment" in atom_type and atom_type["comment"] == comment
                    ) or comment is None:
                        not_new = True
                        # Old atom type knows its new atom type to help reset pair types
                        atom["atom_type"]["atom_type"] = atom_type
                        # Do not forget to update atom type (i may have changed)
                        atom["atom_type"] = atom_type
                        break
            if not_new:
                continue

            # Add a new atom type to the list
            self.add_atom_type(i=None, mass=mass, comment=comment)
            atom["atom_type"] = self.atom_types[-1]

        # Information is only available in the list, need to copy before reset
        old_pair_types = self.pair_types
        self.pair_types = []

        for pair_type in old_pair_types:
            # Get new atom types
            i = pair_type["atom_type_1"]["atom_type"]["i"]
            j = pair_type["atom_type_2"]["atom_type"]["i"]
            coeffs = pair_type["coeffs"]
            style = pair_type["style"]
            if "comment" in pair_type:
                comment = pair_type["comment"]
            else:
                comment = None

            # Order atom types
            if i <= j:
                self.add_pair_type((i, j), coeffs=coeffs, style=style, comment=comment)
            else:
                self.add_pair_type((j, i), coeffs=coeffs, style=style, comment=comment)

        # Remove duplicates (if number of atom types has been reduced)
        self.pair_types = [
            pair_type
            for n, pair_type in enumerate(self.pair_types)
            if pair_type not in self.pair_types[n + 1 :]
        ]

        # Sort pair types by first atom type then by second atom type
        self.pair_types.sort(
            key=lambda pair_type: (
                pair_type["atom_type_1"]["i"],
                pair_type["atom_type_2"]["i"],
            )
        )

    def reset_bond_types(self, match_atypes=True):
        """
        Reset all bond types.

        Matches `coeffs`, `style` and `comment` (if available) of bond types.

        Parameters
        ----------
        match_atypes : bool, default 'True'
            Match atom types of the two atoms composing the bond ?
        """
        self.bond_types = []

        for bond in self.bonds:
            # Extra information to check first
            atom_types = (bond["atom1"]["atom_type"], bond["atom2"]["atom_type"])
            atom_types_rev = list(atom_types)
            atom_types_rev.reverse()
            atom_types_rev = tuple(atom_types_rev)

            coeffs = bond["bond_type"]["coeffs"]
            style = bond["bond_type"]["style"]
            if "comment" in bond["bond_type"]:
                comment = bond["bond_type"]["comment"]
            else:
                comment = None

            # Try to find bond type in the list
            not_new = False
            for bond_type in self.bond_types:
                if (
                    (
                        not match_atypes
                        or (
                            match_atypes
                            and bond_type["atom_types"] == atom_types
                            or bond_type["atom_types"] == atom_types_rev
                        )
                    )
                    and bond_type["coeffs"] == coeffs
                    and bond_type["style"] == style
                ):
                    if (
                        "comment" in bond_type and bond_type["comment"] == comment
                    ) or comment is None:
                        not_new = True
                        # Do not forget to update bond type (i may have changed)
                        bond["bond_type"] = bond_type
                        break
            if not_new:
                continue

            # Add a new bond type to the list
            self.add_bond_type(i=None, coeffs=coeffs, style=style, comment=comment)
            bond["bond_type"] = self.bond_types[-1]

            # Add extra information
            bond["bond_type"]["atom_types"] = atom_types

        # Delete extra information
        for bond_type in self.bond_types:
            del bond_type["atom_types"]

    def reset_angle_types(self, match_atypes=True):
        """
        Reset all angle types.

        Matches `coeffs`, `style` and `comment` (if available) of angle types.

        Parameters
        ----------
        match_atypes : bool, default 'True'
            Match atom types of the three atoms composing the angle ?
        """
        self.angle_types = []

        for angle in self.angles:
            # Extra information to check first
            atom_types = (
                angle["atom1"]["atom_type"],
                angle["atom2"]["atom_type"],
                angle["atom3"]["atom_type"],
            )
            atom_types_rev = list(atom_types)
            atom_types_rev.reverse()
            atom_types_rev = tuple(atom_types_rev)

            coeffs = angle["angle_type"]["coeffs"]
            style = angle["angle_type"]["style"]
            if "comment" in angle["angle_type"]:
                comment = angle["angle_type"]["comment"]
            else:
                comment = None

            # Try to find angle type in the list
            not_new = False
            for angle_type in self.angle_types:
                if (
                    (
                        not match_atypes
                        or (
                            match_atypes
                            and angle_type["atom_types"] == atom_types
                            or angle_type["atom_types"] == atom_types_rev
                        )
                    )
                    and angle_type["coeffs"] == coeffs
                    and angle_type["style"] == style
                ):
                    if (
                        "comment" in angle_type and angle_type["comment"] == comment
                    ) or comment is None:
                        not_new = True
                        # Do not forget to update angle type (i may have changed)
                        angle["angle_type"] = angle_type
                        break
            if not_new:
                continue

            # Add a new angle type to the list
            self.add_angle_type(i=None, coeffs=coeffs, style=style, comment=comment)
            angle["angle_type"] = self.angle_types[-1]

            # Add extra information
            angle["angle_type"]["atom_types"] = atom_types

        # Delete extra information
        for angle_type in self.angle_types:
            del angle_type["atom_types"]

    def reset_dihedral_types(self, match_atypes=True):
        """
        Reset all dihedral angle types.

        Matches `coeffs`, `style` and `comment` (if available) of dihedral angle types.

        Parameters
        ----------
        match_atypes : bool, default 'True'
            Match atom types of the four atoms composing the dihedral angle ?
        """
        self.dihedral_types = []

        for dihedral in self.dihedrals:
            # Extra information to check first
            atom_types = (
                dihedral["atom1"]["atom_type"],
                dihedral["atom2"]["atom_type"],
                dihedral["atom3"]["atom_type"],
                dihedral["atom4"]["atom_type"],
            )
            atom_types_rev = list(atom_types)
            atom_types_rev.reverse()
            atom_types_rev = tuple(atom_types_rev)

            coeffs = dihedral["dihedral_type"]["coeffs"]
            style = dihedral["dihedral_type"]["style"]
            if "comment" in dihedral["dihedral_type"]:
                comment = dihedral["dihedral_type"]["comment"]
            else:
                comment = None

            # Try to find dihedral type in the list
            not_new = False
            for dihedral_type in self.dihedral_types:
                if (
                    (
                        not match_atypes
                        or (
                            match_atypes
                            and dihedral_type["atom_types"] == atom_types
                            or dihedral_type["atom_types"] == atom_types_rev
                        )
                    )
                    and dihedral_type["coeffs"] == coeffs
                    and dihedral_type["style"] == style
                ):
                    if (
                        "comment" in dihedral_type
                        and dihedral_type["comment"] == comment
                    ) or comment is None:
                        not_new = True
                        # Do not forget to update dihedral type (i may have changed)
                        dihedral["dihedral_type"] = dihedral_type
                        break
            if not_new:
                continue

            # Add a new dihedral type to the list
            self.add_dihedral_type(i=None, coeffs=coeffs, style=style, comment=comment)
            dihedral["dihedral_type"] = self.dihedral_types[-1]

            # Add extra information
            dihedral["dihedral_type"]["atom_types"] = atom_types

        # Delete extra information
        for dihedral_type in self.dihedral_types:
            del dihedral_type["atom_types"]

    def reset_improper_types(self):
        """
        Reset all improper types.

        Matches atom types of the four atoms composing the improper. Matches `coeffs`,
        `style` and `comment` (if available) of improper types. Atoms in improper are
        reordered accordingly, but not the optionnal improper `comment` (if available).
        """
        for improper_type in self.improper_types:
            if (
                improper_type["style"] == "distharm"
                or improper_type["style"] == "ring"
                or improper_type["style"] == "class2"
            ):
                raise NotImplementedError(
                    "Found {:s} improper type style, first atom is not the center atom".format(
                        improper_type["style"]
                    )
                )

        self.improper_types = []

        for improper in self.impropers:
            # Extra information to check first
            atom_typesA = (
                improper["atom1"]["atom_type"],
                improper["atom2"]["atom_type"],
                improper["atom3"]["atom_type"],
                improper["atom4"]["atom_type"],
            )
            atom_typesB = (
                improper["atom1"]["atom_type"],
                improper["atom2"]["atom_type"],
                improper["atom4"]["atom_type"],
                improper["atom3"]["atom_type"],
            )
            atom_typesC = (
                improper["atom1"]["atom_type"],
                improper["atom3"]["atom_type"],
                improper["atom2"]["atom_type"],
                improper["atom4"]["atom_type"],
            )
            atom_typesD = (
                improper["atom1"]["atom_type"],
                improper["atom3"]["atom_type"],
                improper["atom4"]["atom_type"],
                improper["atom2"]["atom_type"],
            )
            atom_typesE = (
                improper["atom1"]["atom_type"],
                improper["atom4"]["atom_type"],
                improper["atom2"]["atom_type"],
                improper["atom3"]["atom_type"],
            )
            atom_typesF = (
                improper["atom1"]["atom_type"],
                improper["atom4"]["atom_type"],
                improper["atom3"]["atom_type"],
                improper["atom2"]["atom_type"],
            )

            coeffs = improper["improper_type"]["coeffs"]
            style = improper["improper_type"]["style"]
            if "comment" in improper["improper_type"]:
                comment = improper["improper_type"]["comment"]
            else:
                comment = None

            # Try to find improper type in the list
            not_new = False
            for improper_type in self.improper_types:
                if (
                    (
                        improper_type["atom_types"] == atom_typesA
                        or improper_type["atom_types"] == atom_typesB
                        or improper_type["atom_types"] == atom_typesC
                        or improper_type["atom_types"] == atom_typesD
                        or improper_type["atom_types"] == atom_typesE
                        or improper_type["atom_types"] == atom_typesF
                    )
                    and improper_type["coeffs"] == coeffs
                    and improper_type["style"] == style
                ):
                    if (
                        "comment" in improper_type
                        and improper_type["comment"] == comment
                    ) or comment is None:
                        not_new = True
                        # Reput the atoms in the same order as the improper type
                        # because the force field parameters are not symetrical
                        if improper_type["atom_types"] == atom_typesB:
                            atom3 = improper["atom3"]
                            improper["atom3"] = improper["atom4"]
                            improper["atom4"] = atom3
                        elif improper_type["atom_types"] == atom_typesC:
                            atom2 = improper["atom2"]
                            improper["atom2"] = improper["atom3"]
                            improper["atom3"] = atom2
                        elif improper_type["atom_types"] == atom_typesD:
                            atom2 = improper["atom2"]
                            improper["atom2"] = improper["atom3"]
                            improper["atom3"] = improper["atom4"]
                            improper["atom4"] = atom2
                        elif improper_type["atom_types"] == atom_typesE:
                            atom2 = improper["atom2"]
                            improper["atom2"] = improper["atom4"]
                            atom3 = improper["atom3"]
                            improper["atom3"] = atom2
                            improper["atom4"] = atom3
                        elif improper_type["atom_types"] == atom_typesF:
                            atom2 = improper["atom2"]
                            improper["atom2"] = improper["atom4"]
                            improper["atom4"] = atom2
                        # Be careful, the comment (may correspond to improper name) is not switched
                        # Do not forget to update improper type (i may have changed)
                        improper["improper_type"] = improper_type
                        break
            if not_new:
                continue

            # Add a new improper type to the list
            self.add_improper_type(i=None, coeffs=coeffs, style=style, comment=comment)
            improper["improper_type"] = self.improper_types[-1]

            # Add extra information
            improper["improper_type"]["atom_types"] = atom_typesA

        # Delete extra information
        for improper_type in self.improper_types:
            del improper_type["atom_types"]

    def reset_all_types(self, match_atypes=True):
        """
        Reset all types.

        Parameters
        ----------
        match_atypes : bool, default 'True'
            Match atom types ?
        """
        self.reset_atom_types()
        self.reset_bond_types(match_atypes=match_atypes)
        self.reset_angle_types(match_atypes=match_atypes)
        self.reset_dihedral_types(match_atypes=match_atypes)
        # Should we add match_atypes option ?
        self.reset_improper_types()
