import nh3

# A comprehensive list of advanced test vectors
advanced_test_cases = [
    {
        "name": "Case-insensitivity and obfuscated tags",
        "input": "<ScRiPt>alert(1)</ScRiPt>Safe",
        "should_not_contain": "script",
    },
    {
        "name": "Nested / broken tags parser confusion",
        "input": "<<SCRIPT>alert(" "XSS" ");<</SCRIPT>",
        "should_not_contain": "script",
    },
    {
        "name": "Data URI base64 encoded XSS",
        "input": '<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=">Click</a>',
        "should_not_contain": "data:",
    },
    {
        "name": "Style attribute script injection (expression/javascript)",
        "input": '<div style="background-image: url(\'javascript:alert(1)\');">Test</div>',
        "should_not_contain": "javascript:",
    },
    {
        "name": "Null byte injection (parser evasion)",
        "input": '<s\0cript>alert(1)</script>',
        "should_not_contain": "script",
    },
    {
        "name": "Allowed safe attributes check",
        "input": '<a href="https://example.com" title="Example Website">Link</a>',
        "should_contain": ['href="https://example.com"', 'title="Example Website"'],
    },
    {
        "name": "Disallowed attributes stripping",
        "input": '<p class="danger" onclick="stealCookies()">Paragraph</p>',
        "should_not_contain": ["onclick", "class"],
    }
]

print("--- Running Advanced HTML Sanitizer Tests (Python) ---\n")
passed = 0

for i, test in enumerate(advanced_test_cases, 1):
    output = nh3.clean(test["input"])
    
    success = True
    reason = ""

    # Check forbidden strings
    if "should_not_contain" in test:
        forbidden = test["should_not_contain"]
        if isinstance(forbidden, str):
            forbidden = [forbidden]
        for f in forbidden:
            if f.lower() in output.lower():
                success = False
                reason = f"Output incorrectly retained forbidden token: '{f}'"
                break

    # Check expected safe inclusions
    if success and "should_contain" in test:
        required = test["should_contain"]
        if isinstance(required, str):
            required = [required]
        for r in required:
            if r not in output:
                success = False
                reason = f"Output missed expected safe token: '{r}'"
                break

    if success:
        print(f"[PASS] Test {i}: {test['name']}")
        passed += 1
    else:
        print(f"[FAIL] Test {i}: {test['name']}")
        print(f"       Input:  {test['input']}")
        print(f"       Output: {output}")
        print(f"       Reason: {reason}")

print(f"\nResult: {passed}/{len(advanced_test_cases)} advanced tests passed.")