# Test Cases — AI IT Helpdesk Agent

These test cases can be executed manually against the running Streamlit
application (`streamlit run app.py`). "Expected Output" describes the
structural behavior guaranteed by the code; "Actual Output" and "Status"
should be filled in by the student during the actual project demonstration
and viva, since the exact wording depends on whether Demo Mode or a live LLM
is active.

| ID | Input | Expected Output | Actual Output | Status |
|----|-------|------------------|----------------|--------|
| TC01 | "My Wi-Fi is connected but internet is not working" | Category = wifi/internet; response includes Possible Causes, Troubleshooting Steps, Diagnostic Info (internet connectivity + local IP), Recommended Solution, and Knowledge Sources including wifi.txt/internet.txt | *(fill in during demo)* | *(Pass/Fail)* |
| TC02 | "There are no Wi-Fi networks showing up on my laptop" | Category = wifi; response references adapter/driver troubleshooting from wifi.txt | | |
| TC03 | "How can I check my IP address?" | Category = network/general; get_local_ip and get_hostname tools are invoked and their results shown in Diagnostic Information | | |
| TC04 | "Websites don't load, DNS server not responding" | Category = dns; check_dns_resolution tool runs; response references dns.txt content (flush DNS, public DNS servers) | | |
| TC05 | "My laptop is very slow" | Category = performance; get_cpu_usage, get_memory_usage, get_disk_usage tools run; response references performance.txt | | |
| TC06 | "Printer is not printing" | Category = printer; response references printer.txt (spooler restart, driver reinstall) | | |
| TC07 | "Bluetooth is not connecting to my headphones" | Category = bluetooth; response references bluetooth.txt (re-pairing, driver update) | | |
| TC08 | "My application keeps crashing and won't open" | Category = software; response references software.txt (reinstall, dependencies) | | |
| TC09 | "Windows won't boot, stuck on blue screen" | Category = windows; get_system_information tool runs; response references windows.txt (sfc /scannow, safe mode) | | |
| TC10 | "I forgot my Windows password" | Category = login; response references login.txt and explicitly avoids any password bypass instructions | | |
| TC11 | "Ethernet is connected but I can't access shared folders" | Category = network; response references network.txt (network discovery, sharing settings) | | |
| TC12 | (empty input submitted) | Agent returns a friendly prompt asking the user to describe their problem; no crash occurs | | |
| TC13 | Application started with `LLM_API_KEY` blank in `.env` | UI shows "🟡 DEMO MODE" banner; chat still produces full structured responses using templates | | |
| TC14 | Application started with an invalid/expired `LLM_API_KEY` | LLM call fails internally; agent gracefully falls back to Demo Mode response instead of crashing | | |
| TC15 | Diagnostic tool called when no internet hardware/network is available (e.g., airplane mode) | `check_internet_connection` returns `{"status": "success", "internet_connected": false}` instead of raising an unhandled exception; UI shows "No internet connection detected" | | |

## Notes for Report / Viva
- Every test case above exercises a different combination of: intent
  classification, RAG retrieval, tool calling, Demo Mode fallback, and error
  handling — matching the three core AI concepts required by the project
  brief (AI Agent, RAG, Tool Calling).
- TC12–TC15 specifically validate the error-handling requirements (empty
  input, missing/invalid API key, tool failure).
