from . import __version__ as app_version

app_name = "tourism_portal"
app_title = "Tourism Portal"
app_publisher = "omaralhoori"
app_description = "B2B for tourism companies"
app_email = "tourismportal@mail.com"
app_license = "EULA"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tourism_portal/css/tourism_portal.css"
# app_include_js = "/assets/tourism_portal/js/tourism_portal.js"

# include js, css files in header of web template
# web_include_css = "/assets/tourism_portal/css/tourism_portal.css"
# web_include_js = "/assets/tourism_portal/js/tourism_portal.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tourism_portal/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "tourism_portal.utils.jinja_methods",
#	"filters": "tourism_portal.utils.jinja_filters"
# }

jinja = {
	"methods": [
        "tourism_portal.utils.get_site_logo",
        "tourism_portal.utils.get_site_name",
        "tourism_portal.utils.get_room_extras",
        "tourism_portal.utils.get_room_boards",
        "tourism_portal.utils.has_user_tariff",
        "tourism_portal.utils.get_room_beds",
        "tourism_portal.utils.can_add_user",
        "tourism_portal.utils.can_update_agency",
        "tourism_portal.utils.user_has_subagency",
        "tourism_portal.utils.get_hotel_total_nights",
        "tourism_portal.utils.get_portal_setting",
        "tourism_portal.utils.get_print_settings",
        "tourism_portal.api.company.get_customer_balance",
        "tourism_portal.utils.user_has_desk_access",
        "tourism_portal.utils.create_uuid",
        "tourism_portal.utils.get_website_setting",
        "tourism_portal.utils.get_hotel_stars",
        "tourism_portal.utils.format_url",
    ]
}

# Installation
# ------------

# before_install = "tourism_portal.install.before_install"
# after_install = "tourism_portal.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tourism_portal.uninstall.before_uninstall"
# after_uninstall = "tourism_portal.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tourism_portal.utils.before_app_install"
# after_app_install = "tourism_portal.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tourism_portal.utils.before_app_uninstall"
# after_app_uninstall = "tourism_portal.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tourism_portal.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"tourism_portal.utils.delete_expired_invoices"
	],
    "hourly": [
		"tourism_portal.tourism_portal.doctype.sales_invoice.email_service.check_flight_entered",
	],
}
#	"daily": [
#		"tourism_portal.tasks.daily"
#	],

#	"weekly": [
#		"tourism_portal.tasks.weekly"
#	],
#	"monthly": [
#		"tourism_portal.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "tourism_portal.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "tourism_portal.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "tourism_portal.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tourism_portal.utils.before_request"]
# after_request = ["tourism_portal.utils.after_request"]

# Job Events
# ----------
# before_job = ["tourism_portal.utils.before_job"]
# after_job = ["tourism_portal.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"tourism_portal.auth.validate"
# ]
