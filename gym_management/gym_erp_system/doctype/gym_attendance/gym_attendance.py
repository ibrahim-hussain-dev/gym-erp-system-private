import frappe
from frappe.model.document import Document
from gym_management.gym_erp_system.gym_slot import apply_session_deduction_from_attendance


class GymAttendance(Document):
    def after_insert(self):
        apply_session_deduction_from_attendance(self)
