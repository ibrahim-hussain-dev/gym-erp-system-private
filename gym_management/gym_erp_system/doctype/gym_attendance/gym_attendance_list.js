frappe.listview_settings['Gym Attendance'] = {
    onload: function(listview) {
        listview.set_primary_action = function() {
            listview.page.set_primary_action(__('Mark Attendance'), function() {
                var current_sidebar = frappe.app.sidebar && frappe.app.sidebar.sidebar_title;
                if (current_sidebar) {
                    frappe.route_options = { sidebar: current_sidebar };
                }
                frappe.set_route('mark-attendance');
            });
        };
        listview.set_primary_action();
    }
};
