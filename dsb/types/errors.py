""" Base error class for dsb """

class DSBError(Exception):
    """ Base error class for dsb """

class InvalidValueError(DSBError):
    """ Raised when invalid parameter is provided """
    def __init__(self, parameter: str, *args) -> None:
        super().__init__(f"Please provide valid {parameter} value", *args)

class PlanNotFoundError(DSBError):
    """ Raised when plan is not found """
    def __init__(self, plan_name: str, *args) -> None:
        super().__init__(f"Plan {plan_name} not found", *args)

class PlanAlreadyExistsError(DSBError):
    """ Raised when plan already exists """
    def __init__(self, plan_name: str, *args) -> None:
        super().__init__(f"Plan {plan_name} already exists", *args)

class PlanOwnershipError(DSBError):
    """ Raised when plan ownership is invalid """
    def __init__(self, *args) -> None:
        super().__init__("This plan does not belong to you", *args)

class PlanTransferError(DSBError):
    """ Raised when plan transfer is invalid """
    def __init__(self, plan_name: str, *args) -> None:
        super().__init__(f"Plan {plan_name} already exists in the new group", *args)

class PlanEmptyError(DSBError):
    """ Raised when plan is empty """
    def __init__(self, *args) -> None:
        super().__init__("Plan is empty", *args)

class InvalidPlanNameError(DSBError):
    """ Raised when the plan name is invalid """
    def __init__(self, plan_name: str, *args):
        super().__init__(f"'{plan_name}' is not a valid plan name", *args)

class DoesNotBelongError(DSBError):
    """ Raised when user does not belong to a plan """
    def __init__(self, *args) -> None:
        super().__init__("You do not belong to a plan, use /join_plan to join one", *args)

class NoPlansFoundError(DSBError):
    """ Raised when no plans are found """
    def __init__(self, *args) -> None:
        super().__init__("No plans found", *args)

class LessonNotFoundError(DSBError):
    """ Raised when lesson is not found """
    def __init__(self, *args) -> None:
        super().__init__("Lesson not found", *args)

class NoLessonsError(DSBError):
    """ Raised when no lessons are found """
    def __init__(self, *args) -> None:
        super().__init__("No lessons found", *args)

class NoStudentsError(DSBError):
    """ Raised when no students are found """
    def __init__(self, *args) -> None:
        super().__init__("No students found", *args)