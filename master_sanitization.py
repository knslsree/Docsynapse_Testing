import nh3

# Master test suite containing diverse HTML injection & XSS vectors
all_injection_vectors = [
    # 1. Basic & Script Tags
    {
        "name": "Standard inline script tag",
        "input": '<script>alert(1)</script>',
        "should_not_contain": "script",
    },
    {
        "name": "Obfuscated uppercase tag (<SCRIPT>)",
        "input": '<SCRIPT>alert(1)</SCRIPT>',
        "should_not_contain": "script",
    },
    {
        "name": "Nested script tag trick (<scr<script>ipt>)",
        "input": '<scr<script>ipt>alert(1)</script>',
        "should_not_contain": "script",
    },

    # 2. Event Handlers & Attributes
    {
        "name": "Img tag with onerror event handler",
        "input": '<img src=x onerror=alert(1)>',
        "should_not_contain": "onerror",
    },
    {
        "name": "Malicious attribute value with backticks",
        "input": '<img src=`x` onerror=`alert(1)`>',
        "should_not_contain": "onerror",
    },
    {
        "name": "Autofocus + onfocus trigger",
        "input": '<input autofocus onfocus="alert(1)">',
        "should_not_contain": ["autofocus", "onfocus", "input"],
    },
    {
        "name": "Details element ontoggle event handler",
        "input": '<details ontoggle="alert(1)"><summary>Click</summary></details>',
        "should_not_contain": "ontoggle",
    },
    {
        "name": "Video source element error handler",
        "input": '<video><source src="invalid.mp4" onerror="alert(1)"></video>',
        "should_not_contain": "onerror",
    },
    {
        "name": "Heavy whitespace & newline obfuscation in attributes",
        "input": '<img src = "x" \n onerror = "alert(1)" >',
        "should_not_contain": "onerror",
    },

    # 3. Pseudo-Protocols & URIs
    {
        "name": "Anchor tag javascript: pseudo-protocol",
        "input": '<a href="javascript:alert(1)">Click Me</a>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Form action javascript: pseudo-protocol",
        "input": '<form action="javascript:alert(1)"><button>Click</button></form>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Button formaction javascript: injection",
        "input": '<form><button formaction="javascript:alert(1)">Click</button></form>',
        "should_not_contain": "javascript",
    },
    {
        "name": "VBScript protocol injection",
        "input": '<a href="vbscript:msgbox(1)">VBScript Link</a>',
        "should_not_contain": "vbscript",
    },
    {
        "name": "HTML Entity encoding in protocol (java&#x09;script:)",
        "input": '<a href="java&#x09;script:alert(1)">Click Here</a>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Newline injection in protocol (java\\nscript:)",
        "input": '<a href="java\nscript:alert(1)">Click Here</a>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Data URI base64 script injection in object tag",
        "input": '<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=="></object>',
        "should_not_contain": "data:",
    },
    {
        "name": "Embed tag javascript: pseudo-protocol",
        "input": '<embed src="javascript:alert(1)">',
        "should_not_contain": ["embed", "javascript"],
    },

    # 4. Dangerous Elements & Meta Header Injections
    {
        "name": "Iframe srcdoc injection",
        "input": '<iframe srcdoc="<script>alert(1)</script>"></iframe>',
        "should_not_contain": "script",
    },
    {
        "name": "Meta tag refresh redirect injection",
        "input": '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">',
        "should_not_contain": ["meta", "javascript"],
    },
    {
        "name": "Meta tag CSP header spoofing",
        "input": '<meta http-equiv="Content-Security-Policy" content="default-src *">',
        "should_not_contain": "meta",
    },
    {
        "name": "CSS @import script injection in style tag",
        "input": '<style>@import "javascript:alert(1)";</style>',
        "should_not_contain": "javascript",
    },
    {
        "name": "Plaintext raw text parser consumption vector",
        "input": '<plaintext><script>alert(1)</script>',
        "should_not_contain": "script",
    },

    # 5. Parser Evasion & Foreign Content Contexts
    {
        "name": "SVG onload event vector",
        "input": '<svg/onload=alert(1)>',
        "should_not_contain": ["onload", "<svg"],
    },
    {
        "name": "SVG foreignObject nested script injection",
        "input": '<svg><foreignObject><script>alert(1)</script></foreignObject></svg>',
        "should_not_contain": "script",
    },
    {
        "name": "MathML / SVG foreign element context breakout",
        "input": '<math><mtext><table><mglyph><style><img src=x onerror=alert(1)></style></mglyph></table></mtext></math>',
        "should_not_contain": ["onerror", "img"],
    },
    {
        "name": "Nested comment script smuggling (Moo-style trick)",
        "input": '<!--<script>alert(1)</script>--><span>Safe Content</span>',
        "should_not_contain": "script",
        "should_contain": "Safe Content",
    },
    {
        "name": "Null byte injection in event handler",
        "input": '<img src="x" onerror\x00="alert(1)">',
        "should_not_contain": "onerror",
    },

    # 6. Integrity & Allowlist Preserving Checks
    {
        "name": "Preserve legitimate safe HTML formatting",
        "input": '<p>This is <b>bold</b> and <i>italic</i> safe text.</p>',
        "should_contain": ["<b>bold</b>", "<i>italic</i>"],
    },
]

print(f"--- Running Complete Master Injection Suite ({len(all_injection_vectors)} Vectors) ---\n")
passed = 0

for i, test in enumerate(all_injection_vectors, 1):
    output = nh3.clean(test["input"])
    
    success = True
    reason = ""

    # Validate forbidden strings
    if "should_not_contain" in test:
        forbidden = test["should_not_contain"]
        if isinstance(forbidden, str):
            forbidden = [forbidden]
        for f in forbidden:
            if f.lower() in output.lower():
                success = False
                reason = f"Output retained forbidden token: '{f}'"
                break

    # Validate required safe strings
    if success and "should_contain" in test:
        required = test["should_contain"]
        if isinstance(required, str):
            required = [required]
        for r in required:
            if r not in output:
                success = False
                reason = f"Output missed expected safe content: '{r}'"
                break

    if success:
        print(f"[PASS] Test {i:02d}: {test['name']}")
        passed += 1
    else:
        print(f"[FAIL] Test {i:02d}: {test['name']}")
        print(f"        Input:  {test['input']}")
        print(f"        Output: {output}")
        print(f"        Reason: {reason}")

print(f"\nFinal Result: {passed}/{len(all_injection_vectors)} injection tests passed.")