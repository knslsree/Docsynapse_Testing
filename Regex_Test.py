
import re
import time
import multiprocessing
import queue

# Vulnerable regex: nested quantifiers
VULNERABLE_REGEX = r"^(a+)+$"

# Safer alternative
SAFE_REGEX = r"^a+$"


def regex_worker(pattern, value, result_queue):
    start = time.perf_counter()
    try:
        re.search(pattern, value)
        result_queue.put(time.perf_counter() - start)
    except Exception as exc:
        result_queue.put(str(exc))


def test_regex(pattern, value, timeout=2):
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=regex_worker,
        args=(pattern, value, result_queue)
    )

    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return "TIMEOUT - Possible ReDoS"

    try:
        return f"{result_queue.get_nowait():.6f} seconds"
    except queue.Empty:
        return "No result"


def main():
    print("=" * 60)
    print("REGEX DENIAL OF SERVICE (ReDoS) TEST")
    print("=" * 60)

    print("\nTesting vulnerable regex:", VULNERABLE_REGEX)

    for length in [8, 12, 16, 20, 24, 28]:
        payload = "a" * length + "!"

        result = test_regex(
            VULNERABLE_REGEX,
            payload
        )

        print(f"Input length: {length} | Result: {result}")

    print("\nTesting safer regex:", SAFE_REGEX)

    for length in [8, 16, 24, 28]:
        payload = "a" * length + "!"

        result = test_regex(
            SAFE_REGEX,
            payload
        )

        print(f"Input length: {length} | Result: {result}")

    print("\nTEST COMPLETED")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
