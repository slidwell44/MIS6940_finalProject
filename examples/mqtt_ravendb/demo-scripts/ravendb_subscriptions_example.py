import json
import time
import threading
from pyravendb.store.document_store import DocumentStore
from pyravendb.subscriptions.data import SubscriptionCreationOptions, SubscriptionWorkerOptions

store = DocumentStore(urls=["http://localhost:8080"], database="Mcp")
store.initialize()

options = SubscriptionCreationOptions(query="from dev where id() = '_ravendb/examples/hello-world'")

subscription_name = store.subscriptions.create(options)
print(f"Subscription created with name: {subscription_name}")


def process_documents(batch):
    for item in batch.items:
        doc = item.result
        doc_dict = doc.__dict__
        print("Received document change:")
        print(json.dumps(doc_dict, indent=4))


worker_options = SubscriptionWorkerOptions(subscription_name)
worker_options.time_to_wait_before_connection_retry = 5

subscription = store.subscriptions.get_subscription_worker(worker_options)


def run_subscription():
    subscription.run(process_documents)


subscription_thread = threading.Thread(target=run_subscription)
subscription_thread.daemon = True
subscription_thread.start()

print("Subscription is running. Waiting for document changes...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing subscription...")
    subscription.close()
    store.close()
