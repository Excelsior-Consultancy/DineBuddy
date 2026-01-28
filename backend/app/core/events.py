def notify_customers(restaurant_id: int, event: str, payload: dict):
    """
    Broadcast event to all connected customers.
    Replace this with your WebSocket, Redis Pub/Sub, or Socket.IO logic.
    """
    print(f"[REAL-TIME EVENT] Restaurant {restaurant_id}: {event} -> {payload}")
