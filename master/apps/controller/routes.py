from apps.controller import controller

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)


# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/controller/task/new", methods=["POST"])
def new_task():
    if "file" not in request.files:
        return jsonify({"message": "No file specified"}), 400

    file = request.files["file"]

    task_id = controller.create_task(file)

    return jsonify({"task_id": f"{task_id}"}), 200

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/controller/task/run", methods=["POST"])
def run_task():
    json_data = request.get_json()

    required_keys = ["command", "task_id", "input_size"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    command = json_data["command"]
    task_id = json_data["task_id"]
    input_size = json_data["input_size"]

    if controller.task_state_for_input(task_id, input_size) == "INOP":
        return jsonify({"message": "Task is not yet ready for execution. Try benchmarking it with a specific input size"}), 200

    resp = controller.assign_execution(command, task_id, input_size)

    json_data = resp.json()
    json_data["mode"] = controller.task_state_for_input(task_id, input_size)

    return json_data, 200

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/controller/task/benchmark", methods=["POST"])
def benchmark_task():
    json_data = request.get_json()

    required_keys = ["command", "task_id", "input_size"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    command = json_data["command"]
    task_id = json_data["task_id"]
    input_size = json_data["input_size"]

    exec_time_map = controller.assign_benchmark(command, task_id, input_size)

    if controller.task_state_for_input(task_id, input_size) == "INOP":
        return jsonify({
            "message": "Failed to benchmark task with specified command and input size",
        }), 200

    return jsonify({
        "message": "Benchmarking was successful and task is ready for execution",
        "exec_time": exec_time_map,
    }), 200
