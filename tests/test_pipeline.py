from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def test_modules_exist():
    module_paths = [
        ROOT / 'src' / 'preprocessing.py',
        ROOT / 'src' / 'train.py',
        ROOT / 'src' / 'predict.py',
        ROOT / 'src' / 'utils.py',
    ]
    for path in module_paths:
        assert path.exists(), f'{path} is missing'


def test_dataset_root_exists():
    dataset_root = ROOT / 'dataset' / 'classification'
    assert dataset_root.exists(), 'dataset/classification is missing'
