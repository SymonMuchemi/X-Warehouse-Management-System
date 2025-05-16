# Copyright (c) 2025, SymonMuchemi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Item(Document):
    # make sure valuation rate is 0 before save
    def before_save(self):
        self.valuation_rate = 0
