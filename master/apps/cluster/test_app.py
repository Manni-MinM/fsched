import json
import pytest

from unittest.mock import patch
from apps.cluster.app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("apps.cluster.cluster_manager.add_worker")
def test_add_worker_success(mock_add_worker, client):
    response = client.post("/cluster/worker/add", json={"host": "worker1"})
    assert response.status_code == 200
    assert response.get_json() == {"message": "worker node successfully added"}
    mock_add_worker.assert_called_once_with("worker1")

def test_add_worker_missing_host(client):
    response = client.post("/cluster/worker/add", json={})
    assert response.status_code == 400
    assert response.get_json() == {"message": "no worker host specified"}

def test_list_workers(client):
    response = client.get("/cluster/worker/list")
    assert response.status_code == 200
    assert response.get_json() == {}

@patch("apps.cluster.cluster_manager.assign_task_execution")
def test_assign_task_success(mock_assign, client):
    payload = {
        "cos": 1,
        "command": "run",
        "task_id": "t1",
        "input_size": 123,
        "worker_id": "w1"
    }

    mock_assign.return_value = "task_assigned"
    response = client.post("/cluster/task/assign", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"result": "task_assigned"}
    mock_assign.assert_called_once_with("w1", "run", "t1", 123, 1)

def test_assign_task_missing_input_size(client):
    payload = {
        "cos": 1,
        "command": "run",
        "task_id": "t1",
        "worker_id": "w1"
    }

    response = client.post("/cluster/task/assign", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"message": "Required keys not specified"}
