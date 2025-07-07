import io
import pytest

from unittest.mock import patch, MagicMock
from apps.controller.app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_new_task_no_file(client):
    response = client.post("/controller/task/new")
    assert response.status_code == 400
    assert response.get_json() == {"message": "No file specified"}

@patch("apps.controller.controller.create_task")
def test_new_task_success(mock_create_task, client):
    data = {
        "file": (io.BytesIO(b"dummy content"), "test.txt")
    }

    mock_create_task.return_value = "task123"
    response = client.post("/controller/task/new", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.get_json() == {"task_id": "task123"}
    mock_create_task.assert_called_once()

def test_run_task_missing_input_size(client):
    payload = {
        "command": "run",
        "task_id": "t1",
    }
    response = client.post("/controller/task/run", json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"message": "Required keys not specified"}

@patch("apps.controller.controller.task_state_for_input")
@patch("apps.controller.controller.assign_execution")
def test_run_task_inop_mode(mock_assign_execution, mock_task_state, client):
    mock_task_state.return_value = "INOP"

    payload = {
        "command": "run",
        "task_id": "t1",
        "input_size": 100
    }

    response = client.post("/controller/task/run", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Task is not yet ready for execution. Try benchmarking it with a specific input size"
    }
    mock_task_state.assert_called_once_with("t1", 100)
    mock_assign_execution.assert_not_called()

@patch("apps.controller.controller.task_state_for_input")
@patch("apps.controller.controller.assign_execution")
def test_run_task_executes(mock_assign_execution, mock_task_state, client):
    mock_task_state.return_value = "READY"

    mock_response = MagicMock()
    mock_response.json.return_value = {"foo": "bar"}
    mock_assign_execution.return_value = mock_response

    payload = {
        "command": "run",
        "task_id": "t1",
        "input_size": 100,
    }

    response = client.post("/controller/task/run", json=payload)
    expected_json = {"foo": "bar", "mode": "READY"}

    assert response.status_code == 200
    assert response.get_json() == expected_json
    mock_assign_execution.assert_called_once_with("run", "t1", 100)

def test_benchmark_task_missing_input_size(client):
    payload = {
        "command": "run",
        "task_id": "t1",
    }
    response = client.post("/controller/task/benchmark", json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"message": "Required keys not specified"}

@patch("apps.controller.controller.task_state_for_input")
@patch("apps.controller.controller.assign_benchmark")
def test_benchmark_task_failure(mock_assign_benchmark, mock_task_state, client):
    mock_assign_benchmark.return_value = {"some": "data"}
    mock_task_state.return_value = "INOP"

    payload = {
        "command": "run",
        "task_id": "t1",
        "input_size": 100,
    }

    response = client.post("/controller/task/benchmark", json=payload)
    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Failed to benchmark task with specified command and input size"
    }
    mock_assign_benchmark.assert_called_once_with("run", "t1", 100)
    mock_task_state.assert_called_once_with("t1", 100)

@patch("apps.controller.controller.task_state_for_input")
@patch("apps.controller.controller.assign_benchmark")
def test_benchmark_task_success(mock_assign_benchmark, mock_task_state, client):
    exec_time_map = {"100": 0.123, "200": 0.234}
    mock_assign_benchmark.return_value = exec_time_map
    mock_task_state.return_value = "READY"

    payload = {
        "command": "run",
        "task_id": "t1",
        "input_size": 100
    }

    response = client.post("/controller/task/benchmark", json=payload)
    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Benchmarking was successful and task is ready for execution",
        "exec_time": exec_time_map,
    }
    mock_assign_benchmark.assert_called_once_with("run", "t1", 100)
    mock_task_state.assert_called_once_with("t1", 100)
