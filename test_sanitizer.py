import nh3

# Define test payloads and expectations
test_cases = [
    {
        "name": "Basic script injection",
        "input": "<script>alert('XSS')</script>Hello World",
        "should_not_contain": "<script>",
        "expected": "Hello World",
    },
    {
        "name": "Malicious event handler",
        "input": '<img src="x" onerror="alert(1)">Safe Image',
        "should_not_contain": "onerror",
    },
    {
        "name": "JavaScript pseudo-protocol link",
        "input": '<a href="javascript:alert(1)">Click</a>',
        "should_not_contain": "javascript:",
    },
    {
        "name": "Allowed tags check",
        "input": "<p>Hello <b>World</b></p>",
        "should_contain": "<b>",
    },
]

print("--- Running HTML Sanitizer Tests (Python) ---\n")
passed = 0

for i, test in enumerate(test_cases, 1):
    # Sanitize using nh3 (default configuration or custom if needed)
    output = nh3.clean(test["input"])
    
    success = True
    reason = ""

    if "expected" in test and output != test["expected"]:
        success = False
        reason = f"Expected '{test['expected']}', got '{output}'"
    elif "should_not_contain" in test and test["should_not_contain"] in output:
        success = False
        reason = f"Output contained forbidden token: '{test['should_not_contain']}'"
    elif "should_contain" in test and test["should_contain"] not in output:
        success = False
        reason = f"Output missed expected token: '{test['should_contain']}'"

    if success:
        print(f"[PASS] Test {i}: {test['name']}")
        passed += 1
    else:
        print(f"[FAIL] Test {i}: {test['name']}")
        print(f"       Input:  {test['input']}")
        print(f"       Output: {output}")
        print(f"       Reason: {reason}")

print(f"\nResult: {passed}/{len(test_cases)} tests passed.")