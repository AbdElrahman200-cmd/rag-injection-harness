from bot.customers import _DATA


def get_order_status(order_id: str, customer_id: str, harden: bool = False) -> dict:
    # WEAK on purpose: never checks that the order belongs to customer_id.
    # The `harden` flag is accepted but unused until Task 10.
    for owner_id, cust in _DATA.items():
        for order in cust["orders"]:
            if order["id"] == str(order_id):
                return {
                    "order_id": order["id"],
                    "status": order["status"],
                    "item": order["item"],
                    "customer": cust["name"],
                    "address": cust["address"],
                }
    return {"error": "Order not found."}