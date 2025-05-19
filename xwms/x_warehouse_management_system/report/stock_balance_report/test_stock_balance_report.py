# Copyright (c) 2025, SymonMuchemi and Contributors
# See license.txt

import frappe
import uuid
from frappe.tests.utils import FrappeTestCase
from .stock_balance_report import execute


class TestStockBalanceReport(FrappeTestCase):
    def setUp(self):
        # create a test item
        self.item = frappe.get_doc(
            {
                "doctype": "Item",
                "code": f"REPORT-TV{uuid.uuid4()}",
                "item_name": "Report TV",
                "unit": "Nos",
            }
        ).insert()

        # create a test warehouse
        self.warehouse = frappe.get_doc(
            {"doctype": "Warehouse", "warehouse_name": "Report Bin A", "is_group": 0}
        ).insert()

        # create a stock entry (receipt)
        doc = frappe.get_doc(
            {
                "doctype": "Stock Entry",
                "type": "Receipt",
                "posting_date": "2025-05-16",
                "to_warehouse": self.warehouse.name,
                "items": [
                    {"item": self.item.name, "quantity": 5, "valuation_rate": 15000}
                ],
            }
        ).insert()
        doc.submit()
        self.receipt_name = doc.name

    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabStock Ledger Entry`")
        frappe.db.sql("DELETE FROM `tabStock Entry`")
        frappe.db.sql("DELETE FROM `tabWarehouse`")
        frappe.db.sql("DELETE FROM `tabItem`")
        frappe.db.commit()

    def test_stock_balance_reflects_receipt(self):
        filters = {
            "item": self.item.name,
            "warehouse": self.warehouse.name,
            "posting_date": "2025-05-16",
        }

        columns, data = execute(filters)

        self.assertTrue(
            any(
                row["item"] == self.item.name
                and row["warehouse"] == self.warehouse.name
                for row in data
            ),
            "Stock Balance Report should include the receipt entry.",
        )

    def test_stock_balance_calculation(self):
        filters = {
            "item": self.item.name,
            "warehouse": self.warehouse.name,
            "posting_date": "2025-05-16",
        }

        columns, data = execute(filters)

        # Check if the stock value is calculated correctly
        expected_stock_value = 5 * 15000
        actual_stock_value = data[0]["stock_value"]

        self.assertEqual(
            actual_stock_value,
            expected_stock_value,
            "Stock Balance Report should calculate stock value correctly.",
        )

    def test_stock_balance_no_data(self):
        filters = {
            "item": "Nonexistent Item",
            "warehouse": "Nonexistent Warehouse",
            "posting_date": "2025-05-16",
        }

        columns, data = execute(filters)

        self.assertEqual(
            len(data),
            0,
            "Stock Balance Report should not return any data for nonexistent item and warehouse.",
        )
    
