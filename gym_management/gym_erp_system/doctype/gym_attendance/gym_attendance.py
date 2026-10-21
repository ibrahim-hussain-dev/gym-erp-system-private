import frappe
from frappe.model.document import Document
from frappe.utils import get_time, getdate, nowtime
from gym_management.gym_erp_system.gym_slot import apply_session_deduction_from_attendance


def _day_in_range(day, day_from, day_to):
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if not day_from or not day_to:
        return True
    start, end, cur = weekdays.index(day_from), weekdays.index(day_to), weekdays.index(day)
    if start <= end:
        return start <= cur <= end
    return cur >= start or cur <= end


def _slot_is_active(slot, check_date, check_time):
    day = check_date.strftime("%A")
    if not _day_in_range(day, slot.day_from, slot.day_to):
        return False
    return get_time(slot.start_time) <= check_time <= get_time(slot.end_time)


class GymAttendance(Document):
    def validate(self):
        self.check_timeslot_rules()

    def check_timeslot_rules(self):
        if not self.member:
            return

        member = frappe.db.get_value(
            "Gym Member", self.member,
            ["gender", "preferred_workout_time", "alternative_workout_time", "full_name"],
            as_dict=True,
        )
        if not member:
            return

        check_date = getdate(self.date) if self.date else getdate()
        check_time = get_time(self.check_in_time) if self.check_in_time else get_time(nowtime())

        # Rule 1: Female-only hours ke waqt Male ki attendance kabhi na lage
        female_slots = frappe.get_all(
            "Gym Timing Slot",
            filters={"gender": "Female", "disabled": 0},
            fields=["slot_name", "day_from", "day_to", "start_time", "end_time"],
        )
        for slot in female_slots:
            if _slot_is_active(slot, check_date, check_time) and member.gender == "Male":
                frappe.throw(
                    f"Female-only hours are currently active ({slot.slot_name}, "
                    f"{slot.start_time} - {slot.end_time}). Male members cannot check in during this time."
                )

        # Rule 2: Attendance sirf member ke apne (primary YA alternative) slot ke andar lage
        assigned = [s for s in [member.preferred_workout_time, member.alternative_workout_time] if s]
        if assigned:
            slot_docs = frappe.get_all(
                "Gym Timing Slot",
                filters={"name": ["in", assigned]},
                fields=["name", "slot_name", "day_from", "day_to", "start_time", "end_time"],
            )
            if not any(_slot_is_active(s, check_date, check_time) for s in slot_docs):
                names = ", ".join(f"{s.slot_name} ({s.start_time}-{s.end_time})" for s in slot_docs)
                frappe.throw(
                    f"This check-in is outside {member.full_name}'s assigned training hours ({names})."
                )

    def after_insert(self):
        apply_session_deduction_from_attendance(self)
