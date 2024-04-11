import unittest
from pathlib import Path

from analyzer import save_spectrogram_json


class dotdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, "keys"):
                value = dotdict(value)
            self[key] = value


class TestAnalyzer(unittest.TestCase):
    def test_save_spectrogram_json(self):
        recording = dotdict({"path": "./test.mp3"})
        json_path = save_spectrogram_json(recording)
        self.assertEqual(json_path, Path("/recorder/test.mp3.json.xz"))


if __name__ == "__main__":
    unittest.main()
