frappe.provide('gym_management');

gym_management.NAV_ITEMS = {
	"Gym Front Desk": [
		{label: "Dashboard", route: "/app/gym-operations"},
		{label: "Sell Membership", route: "/app/sell-membership"},
		{label: "Gym Members", route: "/app/gym-member"},
		{label: "Book PT Session", route: "/app/book-pt-session"},
		{label: "Mark Attendance", route: "/app/mark-attendance"},
		{label: "Attendance Log", route: "/app/gym-attendance"},
		{label: "Invoices & Billing", route: "/app/sales-invoice"},
		{label: "Gym Plans", route: "/app/gym-plan"},
		{label: "Gym Packages", route: "/app/gym-package"},
		{label: "Promo Codes", route: "/app/gym-promo-code"},
		{label: "Trainers", route: "/app/gym-trainer"},
		{label: "Time Slots", route: "/app/gym-timing-slot"}
	],
	"Gym Trainer": [
		{label: "Dashboard", route: "/app/gym-operations"},
		{label: "My Sessions", route: "/app/gym-slot"},
		{label: "Attendance Log", route: "/app/gym-attendance"}
	],
	"Gym Manager": [
		{label: "Dashboard", route: "/app/gym-operations"},
		{label: "Sell Membership", route: "/app/sell-membership"},
		{label: "Gym Members", route: "/app/gym-member"},
		{label: "Book PT Session", route: "/app/book-pt-session"},
		{label: "Mark Attendance", route: "/app/mark-attendance"},
		{label: "Attendance Log", route: "/app/gym-attendance"},
		{label: "Invoices & Billing", route: "/app/sales-invoice"},
		{label: "Record Expense", route: "/app/record-expense"},
		{label: "Expenses", route: "/app/gym-expense"},
		{label: "Gym Plans", route: "/app/gym-plan"},
		{label: "Gym Packages", route: "/app/gym-package"},
		{label: "Promo Codes", route: "/app/gym-promo-code"},
		{label: "Trainers", route: "/app/gym-trainer"},
		{label: "Time Slots", route: "/app/gym-timing-slot"},
		{label: "Membership Status Report", route: "/app/query-report/Gym Membership Status"},
		{label: "Trainer Commission Report", route: "/app/query-report/Gym Trainer Commission"},
		{label: "Revenue by Plan Report", route: "/app/query-report/Gym Revenue By Plan"}
	]
};

gym_management.build_fixed_sidebar = function() {
	try {
		if (!frappe.session.user || frappe.session.user === "Guest") return;
		let roles = (frappe.boot && frappe.boot.user && frappe.boot.user.roles) || frappe.user_roles || [];
		if (frappe.session.user === "Administrator" || roles.includes("System Manager")) return;

		let matched_role = Object.keys(gym_management.NAV_ITEMS).find(r => roles.includes(r));
		if (!matched_role) return;

		document.body.classList.add("gym-fixed-nav-active");

		let el = document.getElementById("gym-fixed-sidebar");
		if (!el) {
			el = document.createElement("div");
			el.id = "gym-fixed-sidebar";
			document.body.appendChild(el);
		}

		let current_route = (frappe.get_route_str && frappe.get_route_str()) || "";
		let items = gym_management.NAV_ITEMS[matched_role] || [];
		let html = "";
		items.forEach(function(item) {
			let route_key = item.route.replace("/app/", "");
			let is_active = current_route.indexOf(route_key) === 0;
			html += '<a href="' + item.route + '" class="gym-nav-link' + (is_active ? ' active' : '') + '">' + item.label + '</a>';
		});
		el.innerHTML = html;
	} catch (e) {
		console.error("[gym-sidebar] ERROR:", e);
	}
};

$(document).on("app_ready", function() {
	gym_management.build_fixed_sidebar();
	frappe.router.on("change", function() {
		setTimeout(gym_management.build_fixed_sidebar, 200);
	});
});
