""" Api for DSB """

import threading
import dotenv
from flask import Flask, request, jsonify, abort
import jsonpickle
from werkzeug.serving import make_server
from dsb.types.plan import Plan, Lesson
from dsb.utils.transforms import str_to_day

app = Flask(__name__)

def load_plan(group_id: int, plan_name: str) -> Plan:
    """ Get plan from database """
    with open(f"dsb/database/chat_data/{group_id}.json", encoding="utf-8") as f:
        data = jsonpickle.decode(f.read(), keys=True)
    plan: Plan = data["plans"][plan_name]
    return plan

@app.route("/where_next", methods=["GET"])
def where_next():
    """ Returns classroom where the user has lessons in next """
    group_id = int(request.args.get("group_id"))
    if group_id is None:
        return abort(400, "Group id not specified")
    plan_name = request.args.get("plan_name")
    if plan_name is not None:
        try:
            plan = load_plan(group_id, plan_name)
        except FileNotFoundError:
            return abort(404, "Group with this id does not exist")
        except KeyError:
            return abort(404, "Plan with this name not found")
    else:
        return abort(400, "Plan name was not specified")
    lesson = plan.next_lesson
    if not lesson:
        return abort(404, "No next lesson")
    return jsonify({"room": lesson.room})

@app.route("/add_lesson", methods=["POST"])
def add_lesson():
    """ Add a lesson to a plan """
    data = request.form.to_dict()
    required = ["group_id", "plan_name", "day", "start",
                "end", "teacher", "room", "repeat", "subject", "type"]
    for req in required:
        if req not in data:
            return abort(400, f"{req} missing")
    new_lesson = Lesson(data)
    group_id = int(data["group_id"])
    try:
        plan = load_plan(group_id, data["plan_name"])
    except FileNotFoundError:
        return abort(404, "Group with this id does not exist")
    except KeyError:
        return abort(404, "Plan with this name not found")
    plan.add_lesson(str_to_day(data["day"]) - 1, new_lesson)
    return "Lesson added", 200

@app.route("/add_lesson", methods=["POST"])
def edit_lesson():
    """ Edit lesson from a specified plan """
    data = request.form.to_dict()
    required = ["group_id", "day", "plan_name", "idx"]
    for req in required:
        if req not in data:
            return abort(400, f"{req} missing")
    group_id = int(data["group_id"])
    try:
        plan = load_plan(group_id, data["plan_name"])
    except FileNotFoundError:
        return abort(404, "Group with this id does not exist")
    except KeyError:
        return abort(404, "Plan with this name not found")
    day = str_to_day(data["day"]) - 1
    idx = int(data["idx"])
    lesson = plan.get_day(day)[idx]
    lesson_data = lesson.to_dict()
    lesson_data.update(data)
    new_lesson = Lesson(lesson_data)
    plan.remove_lesson_by_index(day, idx)
    plan.add_lesson(day, new_lesson)
    return "Lesson changed", 200

@app.route("/get_plan", methods=["GET"])
def get_plan():
    """ Get a plan from the database """
    group_id = int(request.args.get("group_id"))
    if not group_id:
        return abort(400, "Group id not specified")
    plan_name = request.args.get("plan_name")
    if not plan_name:
        return abort(400, "Plan name not specified")
    try:
        plan = load_plan(group_id, plan_name)
    except FileNotFoundError:
        return abort(404, "Group with this id does not exist")
    except KeyError:
        return abort(404, "Plan with this name not found")
    plan_dict = {}
    for i in range(0, 5):
        day = plan.get_day(i)
        plan_dict[i] = [lesson.to_dict() for lesson in day]
    return jsonify(plan_dict)

class DSBApiThread(threading.Thread):
    """ Api server thread"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = make_server('0.0.0.0', dotenv.get_key(".env", "api_port"), app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        """ Run the api """
        self.server.serve_forever()

    def shutdown(self):
        """ Shutdown the api """
        self.server.shutdown()
