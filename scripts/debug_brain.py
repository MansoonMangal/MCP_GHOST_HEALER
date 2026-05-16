import httpx, json

dom = "<html><body>" \
    "<input id='user-name' name='user-name' placeholder='Username' />" \
    "<input id='password' name='password' type='password' />" \
    "<input type='submit' id='login-button' class='submit-button btn_action' value='Login' />" \
    "</body></html>"

selectors_to_test = [
    "#login-button-WRONG",
    "#user-name-WRONG",
    "#password-WRONG",
]

for sel in selectors_to_test:
    r = httpx.post(
        "https://ghost-healer-brain.onrender.com/api/heal-locator",
        json={"selector": sel, "action": "click", "dom_snapshot": dom},
        timeout=30
    )
    data = r.json()
    print(f"\nSelector: {sel}")
    print(f"  healed_locator : {data.get('healed_locator')}")
    print(f"  confidence     : {data.get('confidence')}")
    print(f"  confidence_lvl : {data.get('confidence_level')}")
    print(f"  decision       : {data.get('decision')}")
