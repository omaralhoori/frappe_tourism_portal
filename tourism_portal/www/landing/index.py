import frappe
from frappe import _
import json

from tourism_portal.api.reserve import get_all_invoices

no_cache = 1
def get_context(context):
    context.no_cache = True