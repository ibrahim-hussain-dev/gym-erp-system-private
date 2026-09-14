import frappe
from frappe.utils import flt
from frappe.model.document import Document

class GymPackage(Document):
    def validate(self):
        if self.pricing_mode != "Manual Per-Service Price" and not self.overall_price:
            frappe.throw("Overall Package Price is required for this Pricing Mode.")
        if self.pricing_mode == "Manual Per-Service Price":
            for row in self.items:
                if not row.price:
                    frappe.throw("Row {0}: Price is required in Manual Per-Service Price mode.".format(row.idx))
            self.overall_price = sum(flt(row.price) for row in self.items)
