# Copyright (c) 2025, SymonMuchemi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockEntry(Document):
    def before_save(self):
        self.validate()

    def validate(self):
        if not self.items:
            frappe.throw("Please add at least one item to the Stock Entry!")

        for row in self.items:
            # ensure quantity > 0
            if not row.quantity or row.quantity <= 0:
                frappe.throw(f"Quantity must be greater than zero for {row.item}")

            # ensure correct warehouse on entry
            if self.type == "Receipt":
                if not self.to_warehouse:
                    frappe.throw(
                        f"To warehouse is required for receipt item - {row.item}"
                    )
                if self.from_warehouse:
                    frappe.thow(f"From warehouse must be blank for {row.item}")

                # ensure warehouse is a leaf
                is_group = frappe.db.get_value(
                    "Warehouse", self.to_warehouse, "is_group"
                )

                if is_group:
                    frappe.throw(
                        f"To warehouse must be a leaf node (not a group) for item {row.item}"
                    )

            elif self.type == "Consume":
                if not self.from_warehouse:
                    frappe.throw(
                        f"From warehouse is required for receipt item - {row.item}"
                    )
                if self.to_warehouse:
                    frappe.thow(f"To warehouse must be blank for {row.item}")

                # ensure warehouse is a leaf
                is_group = frappe.db.get_value(
                    "Warehouse", self.from_warehouse, "is_group"
                )

                if is_group:
                    frappe.throw(
                        f"From warehouse must be a leaf node (not a group) for item {row.item}"
                    )

            elif self.stock_entry_type == "Transfer":
                if not self.from_warehouse or not self.to_warehouse:
                    frappe.throw(
                        f"Both From and To Warehouses are required for Transfer (item {row.item})"
                    )
                if self.from_warehouse == self.to_warehouse:
                    frappe.throw(
                        f"From and To Warehouses cannot be the same for item {row.item}"
                    )

                # ensure warehouse is a leaf
                from_wh_is_group = frappe.db.get_value(
                    "Warehouse", self.from_warehouse, "is_group"
                )
                to_wh_is_group = frappe.db.get_value(
                    "Warehouse", self.from_warehouse, "is_group"
                )

                if from_wh_is_group:
                    frappe.throw(
                        f"From warehouse must be a leaf node (not a group) for item {row.item}"
                    )

                if to_wh_is_group:
                    frappe.throw(
                        f"To warehouse must be a leaf node (not a group) for item {row.item}"
                    )
