import nh3

# Brand-new parser evasion and structural manipulation test vectors
parser_test_cases = [
    {
        "name": "Nested comment script smuggling (Moo-style comment trick)",
        "input": '<!--<script>alert(1)</script>--><span>Safe Content</span>',
        "should_not_contain": "script",
        "should_contain": "Safe Content",
    },
    {
        "name": "Form action JavaScript pseudo-protocol injection",
        "input": '<form action="javascript:alert(1)"><button>Click</button></form>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Foreign content element (MathML/SVG context breakout)",
        "input": '<math><mtext><table><mglyph><style><img src=x onerror=alert(1)></style></mglyph></table></mtext></math>',
        "should_not_contain": ["onerror", "img"],
    },
    {
        "name": "Malicious attribute value with backticks",
        "input": '<img src=`x` onerror=`alert(1)`>',
        "should_not_contain": "onerror",
    },
    {
        "name": "VBScript or legacy data schema protocol checks",
        "input": '<a href="vbscript:msgbox(1)">VBScript Link</a>',
        "should_not_contain": "vbscript",
    }
]

print("--- Running New Parser & Structural Sanitizer Tests (Python) ---\n")
passed = 0

for i, test in enumerate(parser_test_cases, 1):
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

print(f"\nResult: {passed}/{len(parser_test_cases)} parser tests passed.")