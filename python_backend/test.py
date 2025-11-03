from google.cloud import firestore
from datetime import datetime, timezone
import os

# ------------------------------
# 🔑 Firestore Setup
# ------------------------------
# If running locally, make sure this file exists beside scheduler.py
# and you’ve downloaded it from Firebase > Project Settings > Service Accounts
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "serviceAccountKey.json"

db = firestore.Client()


# ------------------------------
# ⚙️ Helper functions
# ------------------------------
def get_event_date(event_id):
    """Fetch event date for a given event_id."""
    event_ref = db.collection("events").document(event_id).get()
    if event_ref.exists:
        event_data = event_ref.to_dict()
        event_date_map = event_data.get("event_date", {})
        return event_date_map.get("date_value")
    return None


def has_successful_transaction(contract_id):
    """Check if the contract has a successful payment (ESCROW)."""
    tx_ref = db.collection("transactions")
    tx_query = (
        tx_ref.where("contract_id", "==", contract_id)
        .where("status", "in", ["HOLD", "COMPLETED"])
        .stream()
    )
    return any(True for _ in tx_query)


def has_delivery(contract_id):
    """Check if the contract has at least one delivery record."""
    del_ref = db.collection("deliveries")
    del_query = del_ref.where("contract_id", "==", contract_id).stream()
    return any(True for _ in del_query)


# ------------------------------
# 🧠 Main Logic
# ------------------------------


def safe_parse_date(date_str):
    """Safely parse YYYY-MM-DD date strings."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        print(f"⚠️ Invalid date format skipped: {date_str}")
        return None


def send_notification(receiver_id, contract_id, event_name, role):
    """Add a notification document for supplier or planner."""
    title = "Contract Auto-Cancelled"
    message = (
        f"The contract for '{event_name}' has been automatically cancelled because the event has passed "
        "and there were no successful transactions or deliveries."
    )

    notification_data = {
        "avatar": "A",
        "title": title,
        "message": message,
        "receiver_id": receiver_id,
        "referenced_id": contract_id,
        "referenced_type": "contract",
        "unread": True,
        "createdAt": datetime.now(timezone.utc),
    }

    db.collection("notifications").add(notification_data)
    print(f"📩 Notification sent to {role}: {receiver_id}")


# ------------------------------
# 🧠 Main Logic
# ------------------------------
def auto_cancel_contracts():
    print(f"[{datetime.now()}] Checking for inactive or expired contracts...")
    contracts_ref = db.collection("contracts").stream()

    for contract_doc in contracts_ref:
        contract = contract_doc.to_dict()
        contract_id = contract_doc.id

        event_id = contract.get("event_id")
        if not event_id:
            continue

        # Fetch event
        event_ref = db.collection("events").document(event_id).get()
        if not event_ref.exists:
            continue

        event_data = event_ref.to_dict()
        event_date_str = event_data.get("event_date", {}).get("date_value")
        event_name = event_data.get("event_name", "Untitled Event")

        event_date = safe_parse_date(event_date_str)
        if not event_date:
            continue

        if contract.get("status") in ["Cancelled", "Completed"]:
            print(
                f"⏩ Skipping contract {contract_id} (already {contract.get('status')})"
            )
            continue

        now = datetime.now()
        if event_date < now:
            # Check for transactions
            transactions = (
                db.collection("transactions")
                .where("contract_id", "==", contract_id)
                .where("status", "in", ["HOLD", "COMPLETED"])
                .get()
            )

            # Check for deliveries
            deliveries = (
                db.collection("deliveries")
                .where("contract_id", "==", contract_id)
                .get()
            )

            if not transactions and not deliveries:
                print(f"🚫 Cancelling contract {contract_id} (expired and no activity)")

                # Update contract status
                db.collection("contracts").document(contract_id).update(
                    {"status": "Cancelled", "updated_at": datetime.now(timezone.utc)}
                )

                # Send notifications
                supplier_id = contract.get("supplier_id")
                planner_id = contract.get("planner_id")

                if supplier_id:
                    send_notification(supplier_id, contract_id, event_name, "supplier")
                if planner_id:
                    send_notification(planner_id, contract_id, event_name, "planner")

    print("✅ Auto-cancel process complete.\n")


# ------------------------------
# 🕒 Run Once (for Cron Job)
# ------------------------------

auto_cancel_contracts()
