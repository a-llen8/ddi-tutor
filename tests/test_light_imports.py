"""The look-alike code must import without xgboost or scikit-learn."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_lookalike_imports_without_xgboost_or_sklearn():
    code = ("import sys; sys.modules['xgboost'] = None; sys.modules['sklearn'] = None; "
            "import ml.lookalike")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_old_import_paths_still_work():
    from ml.evaluate import tanimoto as a
    from ml.similarity import tanimoto as b
    assert a is b
