"""Python library to test LAMMPS Data object."""

import unittest
import tempfile
from pathlib import Path
from easylammps import Data


class DataTest(unittest.TestCase):
    """Test LAMMPS Data object."""

    def test_read_and_write_to_file(self):
        """Read and rewrite a LAMMPS data file."""
        filepath = Path(__file__).parent.joinpath("data", "butane.data")
        data = Data(filepath)
        # Create a directory to securely open a unique temporary file inside
        with tempfile.TemporaryDirectory() as testdir:
            tempfilepath = Path(testdir).joinpath("test-butane.data")
            data.write_to_file(tempfilepath, write_coeffs=True)
            content = tempfilepath.read_text()
        expected = filepath.read_text()
        self.assertMultiLineEqual(content, expected)


if __name__ == "__main__":
    unittest.main()
