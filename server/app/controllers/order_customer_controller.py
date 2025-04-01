from typing import Any

from server.app.models.order_model import Order
from server.app.models.user_model import User
from server.app.models.team_model import Team


class OrderCustomerController:
    @staticmethod
    def get_all_customer_orders(customer_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        return Order.get_orders_by_customer(customer_id)

    @staticmethod
    def get_all_customer_performers(
        customer_id: int,
        performers: str | None = None
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        if performers == "single":
            return Order.get_performers_by_customer(customer_id)
        if performers == "team":
            return Order.get_performer_teams_by_customer(customer_id)
        
        return (
            Order.get_performers_by_customer(customer_id) 
            + Order.get_performer_teams_by_customer(customer_id)
        )
    
    @staticmethod
    def increase_price(order_id: int, percent: int) -> dict[str, Any]:
        return Order.increase_order_price(order_id, percent)

    @staticmethod
    def decrease_price(order_id: int, percent: int) -> dict[str, Any]:
        return Order.decrease_order_price(order_id, percent)

    @staticmethod
    def get_order_details(order_id: int) -> dict[str, Any] | None:
        order = Order.get_order_details(order_id)

        if (
            order["execution_type"] == "single" 
            and order.get("performer_id")
        ):
            order["performer"] = User.get_order_performer(order["performer_id"])
        if (
            order["execution_type"] == "team" 
            and order.get("performer_team_id")
        ):
            order["team"] = Team.get_order_team(order.get("performer_team_id"))

        order.pop("performer_id")
        order.pop("performer_team_id")

        return order

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
