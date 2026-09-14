import frappe
from frappe.model.document import Document


class GymMember(Document):
	def before_insert(self):
		self.sync_customer()

	def on_update(self):
		if not self.customer:
			self.sync_customer()
			return
		if self.has_value_changed("full_name"):
			frappe.db.set_value("Customer", self.customer, "customer_name", self.full_name)
		if self.has_value_changed("phone"):
			frappe.db.set_value("Customer", self.customer, "mobile_no", self.phone)
		if self.has_value_changed("email"):
			frappe.db.set_value("Customer", self.customer, "email_id", self.email)

	def sync_customer(self):
		if self.customer:
			return
		default_group = frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual"
		cust = frappe.new_doc("Customer")
		cust.customer_name = self.full_name
		cust.customer_type = "Individual"
		cust.customer_group = default_group
		cust.territory = "All Territories"
		cust.mobile_no = self.phone or ""
		cust.email_id = self.email or ""
		cust.insert(ignore_permissions=True)
		self.customer = cust.name
