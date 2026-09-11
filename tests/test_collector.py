import unittest
import numpy as np
from forge.collector.sqlite_collector import SQLiteCollector

class TestSQLiteCollector(unittest.TestCase):
    def test_fallback_ambient_shape(self):
        collector = SQLiteCollector(db_path="/tmp/non_existent_db.sqlite", input_dim=32)
        data = collector.collect_unlabeled_features(min_samples=50)
        self.assertEqual(data.shape, (50, 32))
        self.assertTrue(np.all(data >= 0.0) and np.all(data <= 1.0))

if __name__ == '__main__':
    unittest.main()