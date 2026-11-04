import nh3

# Fresh edge-case and evasion test vectors
extra_test_cases = [
    {
        "name": "Meta tag refresh redirect injection",
        "input": '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">',
        "should_not_contain": ["meta", "javascript"],
    },
    {
        "name": "Details element ontoggle event handler",
        "input": '<details ontoggle="alert(1)"><summary>Click</summary></details>',
        "should_not_contain": "ontoggle",
    },
    {
        "name": "Button formaction attribute protocol injection",
        "input": '<form><button formaction="javascript:alert(1)">Click</button></form>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Heavy whitespace and newline obfuscation in attributes",
        "input": '<img src = "x" \n onerror = "alert(1)" >',
        "should_not_contain": "onerror",
    },
    {
        "name": "Plaintext / Raw text parser consumption vector",
        "input": '<plaintext><script>alert(1)</script>',
        "should_not_contain": "script",
    }
]

print("--- Running Extra HTML Sanitizer Tests (Python) ---\n")
passed = 0

for i, test in enumerate(extra_test_cases, 1):
    output = nh3.clean(test["input"])
    
    success = True
    reason = ""

    # Check forbidden tokens
    if "should_not_contain" in test:
        forbidden = test["should_not_contain"]
        if isinstance(forbidden, str):
            forbidden = [forbidden]
        for f in forbidden:
            if f.lower() in output.lower():
                success = False
                reason = f"Output incorrectly retained forbidden token: '{f}'"
                break

    # Check required safe tokens
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

print(f"\nResult: {passed}/{len(extra_test_cases)} extra tests passed.")