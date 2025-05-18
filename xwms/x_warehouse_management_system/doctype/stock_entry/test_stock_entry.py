# Copyright (c) 2025, SymonMuchemi and Contributors
# See license.txt

import frappe
import uuid
from frappe.tests.utils import FrappeTestCase


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        unique_code = f"TEST-TV-{uuid.uuid4().hex[:6]}"
        self.item = frappe.get_doc({
            "doctype": "Item",
            "code": unique_code,
            "item_name": "Test TV",
            "unit": "Nos"
        }).insert()

        unique_warehouse = f"Test Bin A-{uuid.uuid4().hex[:6]}"
        self.warehouse = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": unique_warehouse,
            "is_group": 0
        }).insert()

    def test_receipt_entry(self):
        doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "posting_date": "2025-05-15",
            "to_warehouse": self.warehouse.name,
            "items": [
                {
                    "item": self.item.name,
                    "quantity": 5,
                    "valuation_rate": 10000
                }
            ]
        })
        doc.insert()
        doc.submit()

        sle = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": doc.name,
            "item": self.item.name,
            "warehouse": self.warehouse.name
        }, fields=["actual_quantity", "valuation_rate"])

        self.assertEqual(len(sle), 1)
        self.assertEqual(sle[0].actual_quantity, 5)
        self.assertEqual(sle[0].valuation_rate, 10000)

    def test_consume_entry_success(self):
        # First, receive stock
        receipt = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "to_warehouse": self.warehouse.name,
            "posting_date": "2025-05-15",
            "items": [{
                "item": self.item.name,
                "quantity": 10,
                "valuation_rate": 10000
            }]
        }).insert()
        receipt.submit()

        # Then consume a part of it
        consume = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Consume",
            "from_warehouse": self.warehouse.name,
            "posting_date": "2025-05-16",
            "items": [{
                "item": self.item.name,
                "quantity": 4
            }]
        }).insert()
        consume.submit()

        sle = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": consume.name,
            "item": self.item.name,
            "warehouse": self.warehouse.name
        }, fields=["actual_quantity", "valuation_rate"])

        self.assertEqual(len(sle), 1)
        self.assertEqual(sle[0].actual_quantity, -4)
        self.assertGreater(sle[0].valuation_rate, 0)

    def test_consume_entry_insufficient_stock(self):
        # No receipt here → stock is 0

        with self.assertRaises(frappe.ValidationError):
            consume = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Consume",
                "from_warehouse": self.warehouse.name,
                "posting_date": "2025-05-16",
                "items": [{
                    "item": self.item.name,
                    "quantity": 1
                }]
            })
            consume.insert()
            consume.submit()

