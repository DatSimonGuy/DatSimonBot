""" Api for DSB """

import threading
from flask import Flask, request, jsonify, abort
import jsonpickle
from werkzeug.serving import make_server
from dsb.types.plan import Plan, Lesson
from dsb.utils.transforms import str_to_day
from dsb.data.database import Database

class DSBApiThread(threading.Thread):
    """ Api server thread"""
    def __init__(self, database: Database, api_port: int) -> None:
        """ Initialize the api """
        threading.Thread.__init__(self)
        self._app = Flask(__name__)
        self.__setup_routes()
        self._database = database
        self.server = make_server('0.0.0.0', api_port, self._app)
        self.ctx = self._app.app_context()
        self.ctx.push()

    def __setup_routes(self):
        self._app.add_url_rule("/where_next", view_func=self.where_next, methods=["GET"])
        self._app.add_url_rule("/add_lesson", view_func=self.add_lesson, methods=["POST"])
        self._app.add_url_rule("/edit_lesson", view_func=self.edit_lesson, methods=["POST"])
        self._app.add_url_rule("/get_plan", view_func=self.get_plan, methods=["GET"])

    def run(self):
        """ Run the api """
        self.server.serve_forever()

    def shutdown(self):
        """ Shutdown the api """
        self.server.shutdown()

    def load_plan(self, chat_id: int, plan_name: str) -> Plan:
        """ Get plan from database """
        chat_data = self._database.get_chat_data(chat_id)
        plan = chat_data.get("plans", {}).get(plan_name, None)
        if plan is None:
            raise ValueError("Plan not found")
        if plan == {}:
            raise ValueError("Chat data is empty")
        return plan

    def where_next(self):
        """ Returns classroom where the user has lessons in next """
        chat_id = int(request.args.get("group_id"))
        if chat_id is None:
            return abort(400, "Group id not specified")
        plan_name = request.args.get("plan_name")
        if plan_name is not None:
            try:
                plan = self.load_plan(chat_id, plan_name)
            except ValueError as e:
                return abort(404, str(e))
        else:
            return abort(400, "Plan name was not specified")
        lesson = plan.next_lesson
        if not lesson:
            return abort(404, "No next lesson")
        return jsonify({"room": lesson.room})

    def add_lesson(self):
        """ Add a lesson to a plan """
        data = request.form.to_dict()
        required = ["group_id", "plan_name", "day", "start",
                    "end", "teacher", "room", "repeat", "subject", "type"]
        for req in required:
            if req not in data:
                return abort(400, f"{req} missing")
        new_lesson = Lesson(data)
        chat_id = int(data["chat_id"])
        try:
            plan = self.load_plan(chat_id, data["plan_name"])
        except ValueError as e:
            return abort(404, str(e))
        plan.add_lesson(str_to_day(data["day"]) - 1, new_lesson)
        return "Lesson added", 200

    def edit_lesson(self):
        """ Edit lesson from a specified plan """
        data = request.form.to_dict()
        required = ["group_id", "day", "plan_name", "idx"]
        for req in required:
            if req not in data:
                return abort(400, f"{req} missing")
        chat_id = int(data["group_id"])
        try:
            plan = self.load_plan(chat_id, data["plan_name"])
        except ValueError as e:
            return abort(404, str(e))
        day = str_to_day(data["day"]) - 1
        idx = int(data["idx"])
        lesson = plan.get_day(day)[idx]
        lesson_data = lesson.to_dict()
        lesson_data.update(data)
        new_lesson = Lesson(lesson_data)
        plan.remove_lesson_by_index(day, idx)
        plan.add_lesson(day, new_lesson)
        return "Lesson changed", 200

    def get_plan(self):
        """ Get a plan from the database """
        data = request.args.to_dict()
        chat_id = int(data.get("group_id"))
        if not chat_id:
            return abort(400, "Group id not specified")
        plan_name = request.args.get("plan_name")
        if not plan_name:
            return abort(400, "Plan name not specified")
        try:
            plan = self.load_plan(chat_id, data["plan_name"])
        except ValueError as e:
            return abort(404, str(e))
        plan_dict = {}
        for i in range(0, 5):
            day = plan.get_day(i)
            plan_dict[i] = [lesson.to_dict() for lesson in day]
        return jsonify(plan_dict)
