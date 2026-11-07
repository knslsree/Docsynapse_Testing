
import threading
import time
from datetime import datetime

# Race Condition Security Testing
# Local simulation - no real transactions are performed.

INITIAL_BALANCE = 1000.00
TRANSACTION_AMOUNT = 700.00

balance = INITIAL_BALANCE
unsafe_results = []

# Intentionally unsafe transaction function
def unsafe_transaction(user_id):

    global balance

    current_balance = balance

    # Simulate processing delay
    time.sleep(0.1)

    if current_balance >= TRANSACTION_AMOUNT:
        balance = current_balance - TRANSACTION_AMOUNT

        unsafe_results.append({
            "user": user_id,
            "status": "SUCCESS",
            "balance": balance
        })
    else:
        unsafe_results.append({
            "user": user_id,
            "status": "REJECTED",
            "balance": balance
        })


# Safe transaction function using a lock
safe_balance = INITIAL_BALANCE
safe_results = []
transaction_lock = threading.Lock()


def safe_transaction(user_id):

    global safe_balance

    with transaction_lock:

        if safe_balance >= TRANSACTION_AMOUNT:

            safe_balance -= TRANSACTION_AMOUNT

            safe_results.append({
                "user": user_id,
                "status": "SUCCESS",
                "balance": safe_balance
            })

        else:

            safe_results.append({
                "user": user_id,
                "status": "REJECTED",
                "balance": safe_balance
            })


def run_test(transaction_function):

    threads = []

    for user in range(1, 6):

        thread = threading.Thread(
            target=transaction_function,
            args=(user,)
        )

        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


print("=" * 65)
print("RACE CONDITION SECURITY TEST")
print("=" * 65)

print("\nINITIAL BALANCE:", INITIAL_BALANCE)
print("TRANSACTION AMOUNT:", TRANSACTION_AMOUNT)
print("SIMULTANEOUS USERS: 5")

# Test 1: Unsafe transaction processing
print("\n[TEST 1] UNSAFE SIMULTANEOUS TRANSACTIONS")

run_test(unsafe_transaction)

for result in unsafe_results:
    print(result)

successful = sum(
    1 for result in unsafe_results
    if result["status"] == "SUCCESS"
)

print("\nSuccessful transactions:", successful)
print("Final balance:", balance)

if successful * TRANSACTION_AMOUNT > INITIAL_BALANCE:
    print("[FAIL] Potential race condition detected")
else:
    print("[INFO] No overspending observed in this run")


# Test 2: Safe transaction processing
print("\n[TEST 2] LOCK-PROTECTED TRANSACTIONS")

run_test(safe_transaction)

for result in safe_results:
    print(result)

successful_safe = sum(
    1 for result in safe_results
    if result["status"] == "SUCCESS"
)

print("\nSuccessful transactions:", successful_safe)
print("Final balance:", safe_balance)

if successful_safe * TRANSACTION_AMOUNT <= INITIAL_BALANCE:
    print("[PASS] No overspending detected")
else:
    print("[FAIL] Transaction integrity issue")

print("\nTEST COMPLETED:", datetime.now())
