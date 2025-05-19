# Copyright (c) 2025, SymonMuchemi and Contributors
# See license.txt

import frappe
import uuid
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today



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
    
    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabStock Ledger Entry`")
        frappe.db.sql("DELETE FROM `tabStock Entry`")
        frappe.db.sql("DELETE FROM `tabWarehouse`")
        frappe.db.sql("DELETE FROM `tabItem`")
        frappe.db.commit()

    def test_receipt_entry(self):
        """ Test stock receipt entry creation and validation. """
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
        """ Test stock consume entry creation and validation. """
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
        """ Test stock consume entry with insufficient stock. """

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

    def test_transfer_entry_success(self):
        """ Test stock transfer entry creation and validation. """
        # Create destination warehouse
        dest_warehouse = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Test Bin B",
            "is_group": 0
        }).insert()

        # Receive stock first
        receipt = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "to_warehouse": self.warehouse.name,
            "posting_date": "2025-05-15",
            "items": [{
                "item": self.item.name,
                "quantity": 10,
                "valuation_rate": 15000
            }]
        }).insert()
        receipt.submit()

        # Transfer stock
        transfer = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Transfer",
            "from_warehouse": self.warehouse.name,
            "to_warehouse": dest_warehouse.name,
            "posting_date": "2025-05-17",
            "items": [{
                "item": self.item.name,
                "quantity": 5
            }]
        }).insert()
        transfer.submit()

        sle = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": transfer.name
        }, fields=["warehouse", "actual_quantity", "valuation_rate"])

        self.assertEqual(len(sle), 2)

        outbound = next(s for s in sle if s.actual_quantity < 0)
        inbound = next(s for s in sle if s.actual_quantity > 0)

        self.assertEqual(abs(outbound.actual_quantity), inbound.actual_quantity)
        self.assertEqual(outbound.valuation_rate, inbound.valuation_rate)

    def test_zero_quantity_rejected(self):
        """ Test stock entry with zero quantity. """
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Receipt",
                "to_warehouse": self.warehouse.name,
                "posting_date": "2025-05-15",
                "items": [{
                    "item": self.item.name,
                    "quantity": 0,
                    "valuation_rate": 10000
                }]
            })
            doc.insert()
            doc.submit()

    def test_valuation_rate_after_multiple_receipts(self):
        """ Test moving average valuation rate after multiple receipts. """

        # First Receipt: 5 items @ 10,000
        doc1 = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "to_warehouse": self.warehouse.name,
            "posting_date": "2025-05-01",
            "items": [{
                "item": self.item.name,
                "quantity": 5,
                "valuation_rate": 10000
            }]
        }).insert()
        doc1.submit()

        # Second Receipt: 5 items @ 20,000
        doc2 = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "to_warehouse": self.warehouse.name,
            "posting_date": "2025-05-02",
            "items": [{
                "item": self.item.name,
                "quantity": 5,
                "valuation_rate": 20000
            }]
        }).insert()
        doc2.submit()

        # Expected moving average:
        # Total value: (5 * 10k) + (5 * 20k) = 150,000
        # Total quantity: 10
        # Expected valuation rate = 150,000 / 10 = 15,000

        # Consume 2 items (should be at 15,000 per unit)
        consume = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Consume",
            "from_warehouse": self.warehouse.name,
            "posting_date": "2025-05-03",
            "items": [{
                "item": self.item.name,
                "quantity": 2
            }]
        }).insert()
        consume.submit()

        # Check the valuation rate used in the consume entry
        sle = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": consume.name,
            "item": self.item.name,
            "warehouse": self.warehouse.name
        }, fields=["valuation_rate", "actual_quantity"])

        self.assertEqual(len(sle), 1)
        self.assertEqual(sle[0].valuation_rate, 15000)
        self.assertEqual(sle[0].actual_quantity, -2)

    def test_transfer_entry_uses_source_valuation_rate(self):
        """ Test stock transfer entry uses source warehouse valuation rate. """

        # Create destination warehouse
        dest_warehouse = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Test Bin Transfer Target",
            "is_group": 0
        }).insert()

        # Receive 4 items @ 12,000 in source warehouse
        receipt = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "to_warehouse": self.warehouse.name,
            "posting_date": "2025-05-10",
            "items": [{
                "item": self.item.name,
                "quantity": 4,
                "valuation_rate": 12000
            }]
        }).insert()
        receipt.submit()

        # Transfer 2 items to destination warehouse
        transfer = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Transfer",
            "from_warehouse": self.warehouse.name,
            "to_warehouse": dest_warehouse.name,
            "posting_date": "2025-05-11",
            "items": [{
                "item": self.item.name,
                "quantity": 2
            }]
        }).insert()
        transfer.submit()

        # Fetch the two SLEs from this transfer
        sle_entries = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": transfer.name,
            "item": self.item.name
        }, fields=["warehouse", "actual_quantity", "valuation_rate"])

        self.assertEqual(len(sle_entries), 2)

        # Separate inbound and outbound
        outbound = next(s for s in sle_entries if s.actual_quantity < 0)
        inbound = next(s for s in sle_entries if s.actual_quantity > 0)

        # ✅ Valuation rate should be the same on both
        self.assertEqual(outbound.valuation_rate, 12000)
        self.assertEqual(inbound.valuation_rate, 12000)

        # ✅ Actual quantities should be equal (opposite signs)
        self.assertEqual(abs(outbound.actual_quantity), inbound.actual_quantity)

        # ✅ Warehouses should match correctly
        self.assertEqual(outbound.warehouse, self.warehouse.name)
        self.assertEqual(inbound.warehouse, dest_warehouse.name)

    def test_group_warehouse_not_allowed(self):
        """ Test that group warehouses cannot be used in stock entries. """
        # Create a group warehouse (non-leaf)
        group_wh = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Group Warehouse Test",
            "is_group": 1
        }).insert()

        # 🚫 Try using as Receipt destination
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Receipt",
                "to_warehouse": group_wh.name,
                "items": [{
                    "item": self.item.name,
                    "quantity": 5,
                    "valuation_rate": 9000
                }]
            })
            doc.insert()
            doc.submit()

        # 🚫 Try using as Consume source
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Consume",
                "from_warehouse": group_wh.name,
                "items": [{
                    "item": self.item.name,
                    "quantity": 2
                }]
            })
            doc.insert()
            doc.submit()

        # 🚫 Try using as either side in Transfer
        with self.assertRaises(frappe.ValidationError):
            dest = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Another Bin",
                "is_group": 0
            }).insert()

            doc = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Transfer",
                "from_warehouse": group_wh.name,
                "to_warehouse": dest.name,
                "items": [{
                    "item": self.item.name,
                    "quantity": 1
                }]
            })
            doc.insert()
            doc.submit()

    def test_transfer_within_same_warehouse_should_fail(self):
        """ Test that transferring stock within the same warehouse fails. """
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Transfer",
                "from_warehouse": self.warehouse.name,
                "to_warehouse": self.warehouse.name,  # same warehouse
                "posting_date": "2025-05-20",
                "items": [{
                    "item": self.item.name,
                    "quantity": 3
                }]
            })
            doc.insert()
            doc.submit()
    
    def test_invalid_quantities_should_fail(self):
        """ Test that invalid quantities raise validation errors. """
        invalid_quantities = [0, -1, None]

        for qty in invalid_quantities:
            with self.assertRaises(frappe.ValidationError, msg=f"Quantity: {qty} should raise error"):
                doc = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "type": "Receipt",
                    "to_warehouse": self.warehouse.name,
                    "posting_date": "2025-05-22",
                    "items": [{
                        "item": self.item.name,
                        "quantity": qty,
                        "valuation_rate": 10000
                    }]
                })
                doc.insert()
                doc.submit()

    def test_future_posting_date_should_fail(self):
        future_date = add_days(today(), 3)  # 3 days in the future

        with self.assertRaises(frappe.ValidationError) as context:
            doc = frappe.get_doc({
                "doctype": "Stock Entry",
                "type": "Receipt",
                "to_warehouse": self.warehouse.name,
                "posting_date": future_date,
                "items": [{
                    "item": self.item.name,
                    "quantity": 3,
                    "valuation_rate": 10000
                }]
            })
            doc.insert()
            doc.submit()

        self.assertIn("Posting date cannot be in the future", str(context.exception))

    def test_missing_posting_date_defaults_to_today(self):
        doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "to_warehouse": self.warehouse.name,
            "items": [{
                "item": self.item.name,
                "quantity": 2,
                "valuation_rate": 8000
            }]
        }).insert()
        doc.submit()

        self.assertEqual(str(doc.posting_date), today())
