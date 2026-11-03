"""Unit tests for Cantor S3 drive; tiny mock is not a physical S3 sector."""
import hashlib
import tempfile
import unittest
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from cantor_s3_drive import SIGNAL_SHA256, cantor_signal, load_matrix, propagators, replay, run

TOY_MATRIX = '2\n1 4\n0 3\n0 0 4\n0 1 -4\n1 1 4\n'

class CantorS3Tests(unittest.TestCase):
    def test_cantor_source_hash(self):
        b = cantor_signal()
        self.assertEqual(hashlib.sha256(b).hexdigest(), SIGNAL_SHA256)
        self.assertEqual([b.count(i) for i in range(3)], [665, 32, 32])

    def test_weighted_hermitian_and_independent_expm(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'m'
            p.write_text(TOY_MATRIX)
            e, mag, _ = load_matrix(p)
            self.assertAlmostEqual(e[0,1], -2.)
            unitaries = propagators(e, mag, 9, 1/27, 1/27)
            for pulse, u in unitaries.items():
                expected = expm(-1j/27 * (e + np.diag((9+pulse/27)*mag)))
                self.assertLess(np.max(np.abs(expected-u)), 1e-12)
            psi, drift, backward = replay([1,0,-1,1,0]*8, unitaries, 0)
            self.assertLess(drift, 1e-12)
            self.assertLess(backward, 1e-12)
            self.assertAlmostEqual(np.linalg.norm(psi), 1.)

    def test_729_steps_and_reproducible_receipts(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'m'
            p.write_text(TOY_MATRIX)
            hbp, hbi = run(p)
            self.assertIn('VERDICT|result=PASS', hbp)
            self.assertEqual((hbp, hbi), run(p))
            self.assertEqual(len(hbp.splitlines()), len(hbi.splitlines()))
            self.assertIn('control=rotated_one', hbp)

    def test_reject_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'m'
            for content in ['2\n1 0\n0 3\n', TOY_MATRIX+'0 1 2\n', TOY_MATRIX.replace('0 1 -4','1 0 -4')]:
                p.write_text(content)
                with self.assertRaises(ValueError):
                    load_matrix(p)

if __name__ == '__main__':
    unittest.main()
