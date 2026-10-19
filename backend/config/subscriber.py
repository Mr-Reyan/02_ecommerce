from .redis_client import redis_client


pubsub = redis_client.pubsub()

pubsub.subscribe("notifications")

print("Listening for notifications...")

for message in pubsub.listen():
    print(message)
    if message["type"] == "message":
        print("Received:", message["data"])