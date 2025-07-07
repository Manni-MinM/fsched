import io
import pytest

from unittest.mock import patch
from apps.predictor.app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_predict_benchmarked_missing_exec_time_list(client):
    payload = {
        "task_id": "t1",
        "input_size": 100,
        "generosity": 0.5,
    }
    response = client.post("/predictor/task/benchmarked", json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"message": "Required keys not specified"}

@patch("apps.predictor.cache_predictor.predict_for_benchmarked_task")
def test_predict_benchmarked_success(mock_predict, client):
    mock_predict.return_value = 3

    payload = {
        "task_id": "t1",
        "input_size": 100,
        "generosity": 0.5,
        "execution_time_list": [0.1, 0.2, 0.3],
    }
    response = client.post("/predictor/task/benchmarked", json=payload)
    assert response.status_code == 200
    assert response.get_json() == {"suitable_cos": 3}
    mock_predict.assert_called_once_with("t1", 100, 0.5, [0.1, 0.2, 0.3])

def test_predict_assisted_missing_generosity(client):
    payload = {
        "task_id": "t1",
        "input_size": 100,
    }
    response = client.post("/predictor/task/assisted", json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"message": "Required keys not specified"}

@patch("apps.predictor.cache_predictor.predict_for_assisted_task")
def test_predict_assisted_success(mock_predict, client):
    mock_predict.return_value = 5

    payload = {
        "task_id": "t1",
        "input_size": 100,
        "generosity": 0.7,
    }
    response = client.post("/predictor/task/assisted", json=payload)
    assert response.status_code == 200
    assert response.get_json() == {"suitable_cos": 5}
    mock_predict.assert_called_once_with("t1", 100, 0.7)
