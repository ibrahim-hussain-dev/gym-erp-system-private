import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GymFitnessLog(Document):
    def after_insert(self):
        self.sync_latest_to_member()

    def on_update(self):
        self.sync_latest_to_member()

    def sync_latest_to_member(self):
        latest = frappe.db.get_value(
            "Gym Fitness Log",
            {"member": self.member},
            ["name"],
            order_by="log_date desc, creation desc",
        )
        if latest != self.name:
            return
        updates = {}
        if self.weight_kg:
            updates["weight_kg"] = self.weight_kg
        if self.height_cm:
            updates["height_feet"] = flt(self.height_cm) / 30.48
        if updates:
            frappe.db.set_value("Gym Member", self.member, updates)
