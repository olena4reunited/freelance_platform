from typing import Any

from server.app.models.order_model import Order


class OrderCustomerController:
    @staticmethod
    def get_all_customer_orders(customer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        return Order.get_orders_by_customer(customer_id)

    @staticmethod
    def get_all_customer_performers(customer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        return Order.get_performers_by_customer(customer_id)

    @staticmethod
    def get_order_details(order_id: int) -> dict[str, Any] | None:
        return Order.get_order_details(order_id)

    @staticmethod
    def create_order(order_data: dict[str, Any], customer_id: int) -> dict[str, Any]:
        return Order.create_order(customer_id=customer_id, order_data=order_data)

    @staticmethod
    def update_order(
            order_id: int,
            order_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        copy_keys = [key for key in order_data.keys()]
        for key in copy_keys:
            if not order_data[key]:
                order_data.pop(key)

        return Order.update_order_by_id(order_id=order_id, order_data=order_data)

    @staticmethod
    def delete_order(order_id: int) -> None:
        Order.delete_record_by_id(order_id)
