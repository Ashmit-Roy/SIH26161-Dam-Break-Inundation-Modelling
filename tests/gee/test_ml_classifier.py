import os

import numpy as np
import pandas as pd
import pytest
from src.gee.ml_classifier import WaterClassifier


@pytest.fixture
def sample_training_data():
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame({
        "VV": np.random.uniform(-25, -5, n_samples),
        "VH": np.random.uniform(-30, -10, n_samples),
        "VV_minus_VH": np.random.uniform(2, 10, n_samples),
        "VV_plus_VH": np.random.uniform(-50, -15, n_samples),
        "SAR_Ratio": np.random.uniform(0.5, 2.5, n_samples),
        "NDPI": np.random.uniform(-0.5, 0.5, n_samples),
        "MNDWI": np.random.uniform(-1, 1, n_samples),
        "NDWI": np.random.uniform(-1, 1, n_samples),
        "NDVI": np.random.uniform(-1, 1, n_samples),
        "label": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    })
    return df


def test_train_and_predict(sample_training_data):
    classifier = WaterClassifier(model_type="rf", n_estimators=10, random_state=42)
    metrics = classifier.train(sample_training_data, target_column="label")

    assert "accuracy" in metrics
    assert "f1" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert classifier.is_trained

    predictions = classifier.predict(sample_training_data)
    assert len(predictions) == len(sample_training_data)
    assert set(np.unique(predictions)).issubset({0, 1})

    # Test predicting with a single dictionary
    single_dict = {"VV": -19.0, "VH": -25.0}
    dict_pred = classifier.predict(single_dict)
    assert len(dict_pred) == 1

    # Test predicting with numpy array
    np_arr = np.array([[-19.0, -25.0, 6.0, -44.0, 0.76, 0.1, 0.5, 0.4, -0.2]])
    np_pred = classifier.predict(np_arr)
    assert len(np_pred) == 1

    # Test predict_proba
    probs = classifier.predict_proba(sample_training_data)
    assert probs.shape[0] == len(sample_training_data)


def test_save_and_load(sample_training_data, tmp_path):
    classifier = WaterClassifier(model_type="rf", n_estimators=10, random_state=42)
    classifier.train(sample_training_data)

    save_file = str(tmp_path / "subdir" / "water_model.joblib")
    classifier.save(save_file)
    assert os.path.exists(save_file)

    loaded_classifier = WaterClassifier.load(save_file)
    assert loaded_classifier.is_trained

    pred_orig = classifier.predict(sample_training_data)
    pred_loaded = loaded_classifier.predict(sample_training_data)
    np.testing.assert_array_equal(pred_orig, pred_loaded)


def test_error_handling(sample_training_data):
    untrained = WaterClassifier()
    with pytest.raises(RuntimeError):
        untrained.predict(sample_training_data)

    with pytest.raises(FileNotFoundError):
        WaterClassifier.load("non_existent_path.joblib")

    with pytest.raises(ValueError):
        WaterClassifier(model_type="unsupported")
