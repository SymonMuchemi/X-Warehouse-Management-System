# Copyright (c) 2025, SymonMuchemi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class Warehouse(NestedSet):
    def before_save(self):
        self.validate_parent()

    def validate_parent(self):
        parent_is_group = frappe.db.get_value(
            "warehouse", self.parent_warehouse, "is_group"
        )
        if parent_is_group == 0:
            print(f"is group value: {parent_is_group}")
            frappe.throw(
                f"Invalid operation, {self.parent_warehouse} is not a valid parent!"
            )
