"""
agent/helpdesk_agent.py
--------------------------
The AI Agent layer: the "brain" that ties together intent classification,
RAG retrieval, tool calling, and LLM response generation.

Agent pipeline:
    1. Receive user query
    2. Classify problem category (intent)
    3. Decide whether RAG is needed (almost always, for IT problems)
    4. Retrieve relevant knowledge base chunks
    5. Decide whether a diagnostic tool is needed, based on category
    6. Call the appropriate predefined safe tool(s)
    7. Combine retrieved knowledge + diagnostic results
    8. Generate the final structured response (via LLM, or Demo Mode)
    9. Return the response for the caller to store in memory/database
"""

import re
from typing import Dict, List, Optional

from config.config import Config
from rag.retriever import retrieve_context, ensure_vector_database_ready
from tools import system_tools

# ---------------------------------------------------------------------------
# Intent / category classification
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "wifi": ["wifi", "wi-fi", "wireless network", "no wifi", "wifi not connecting"],
    "internet": ["internet", "no internet", "broadband", "isp", "slow internet", "connection speed"],
    "dns": ["dns", "site can't be reached", "server not found", "dns_probe"],
    "network": ["network", "ethernet", "lan", "ip address", "ip conflict", "shared folder"],
    "printer": ["printer", "printing", "print job", "spooler", "cartridge", "toner"],
    "bluetooth": ["bluetooth", "pairing", "paired device", "headphones", "earbuds"],
    "software": ["application", "app ", "software", "program", "install", "crash", "not opening"],
    "windows": ["windows", "blue screen", "bsod", "boot", "update fail", "won't start", "restart loop"],
    "performance": ["slow", "lag", "freeze", "hang", "high cpu", "high memory", "performance", "disk space"],
    "login": ["password", "login", "log in", "locked out", "sign in", "account access", "2fa", "authentication"],
}

# When two categories tie on keyword-match score, this priority order breaks
# the tie (earlier entries win). This matters for queries like "I forgot my
# Windows password", which matches both "windows" (OS name mentioned) and
# "login" (password/account keyword) - "login" should win because it is the
# more specific, actionable intent.
CATEGORY_PRIORITY = [
    "login",
    "dns",
    "printer",
    "bluetooth",
    "wifi",
    "internet",
    "network",
    "software",
    "performance",
    "windows",
]


def classify_category(query: str) -> str:
    """
    Classify the user's query into one of the supported problem categories
    using simple, transparent keyword matching (a lightweight rule-based
    intent classifier appropriate for a college demonstration project).

    Ties in keyword-match score are broken using CATEGORY_PRIORITY so that
    more specific intents (e.g. "login") win over incidental mentions (e.g.
    the word "Windows" appearing in a password-related query).
    """
    text = query.lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 1

    top_score = max(scores.values())
    if top_score == 0:
        return "general"

    # Among all categories tied for the top score, return the one that
    # appears earliest in CATEGORY_PRIORITY.
    tied_categories = [cat for cat, score in scores.items() if score == top_score]
    for preferred in CATEGORY_PRIORITY:
        if preferred in tied_categories:
            return preferred

    # Fallback (should not normally happen since CATEGORY_PRIORITY covers
    # every category), but kept for safety.
    return tied_categories[0]


def requires_diagnostic_tool(category: str, query: str) -> List[str]:
    """
    Decide which safe diagnostic tool(s), if any, should be called for this
    category. Returns a list of tool names (matching functions in
    tools/system_tools.py) to invoke.
    """
    text = query.lower()
    tools_to_run: List[str] = []

    if category in ("wifi", "internet", "network"):
        tools_to_run += ["check_internet_connection", "get_local_ip"]
    if category == "dns":
        tools_to_run += ["check_dns_resolution"]
    if category == "performance":
        tools_to_run += ["get_cpu_usage", "get_memory_usage", "get_disk_usage"]
    if category == "windows":
        tools_to_run += ["get_system_information"]
    if "ip address" in text or "my ip" in text:
        tools_to_run += ["get_local_ip", "get_hostname"]
    if "ping" in text:
        tools_to_run += ["ping_public_host"]

    # De-duplicate while preserving order.
    seen = set()
    unique_tools = []
    for t in tools_to_run:
        if t not in seen:
            seen.add(t)
            unique_tools.append(t)
    return unique_tools


TOOL_FUNCTION_MAP = {
    "get_system_information": system_tools.get_system_information,
    "get_hostname": system_tools.get_hostname,
    "get_local_ip": system_tools.get_local_ip,
    "check_internet_connection": system_tools.check_internet_connection,
    "check_dns_resolution": system_tools.check_dns_resolution,
    "ping_public_host": system_tools.ping_public_host,
    "get_cpu_usage": system_tools.get_cpu_usage,
    "get_memory_usage": system_tools.get_memory_usage,
    "get_disk_usage": system_tools.get_disk_usage,
}


def run_diagnostic_tools(tool_names: List[str]) -> Dict:
    """Execute each requested (predefined, safe) tool and collect results."""
    results = {}
    for name in tool_names:
        func = TOOL_FUNCTION_MAP.get(name)
        if func:
            try:
                results[name] = func()
            except Exception as exc:
                results[name] = {"status": "error", "message": str(exc)}
    return results


def format_diagnostic_results(results: Dict) -> str:
    """Turn raw diagnostic tool results into a short human-readable block."""
    if not results:
        return "No diagnostic checks were required for this issue."

    lines = []
    for name, result in results.items():
        if result.get("status") != "success":
            lines.append(f"- {name}: could not complete ({result.get('message', 'unknown error')})")
            continue

        if name == "check_internet_connection":
            lines.append(f"- Internet Connectivity: {'Connected' if result['internet_connected'] else 'Not Connected'}")
        elif name == "check_dns_resolution":
            lines.append(f"- DNS Resolution: {'Working' if result['dns_working'] else 'Not Working'} (tested host: {result['resolved_host']})")
        elif name == "get_local_ip":
            lines.append(f"- Local IP Address: {result['local_ip']}")
        elif name == "get_hostname":
            lines.append(f"- Hostname: {result['hostname']}")
        elif name == "ping_public_host":
            lines.append(f"- Ping to {result['target']}: {'Reachable' if result['reachable'] else 'Unreachable'}")
        elif name == "get_cpu_usage":
            lines.append(f"- CPU Usage: {result['cpu_usage_percent']}%")
        elif name == "get_memory_usage":
            lines.append(f"- Memory Usage: {result['memory_usage_percent']}% ({result['available_gb']} GB free of {result['total_gb']} GB)")
        elif name == "get_disk_usage":
            lines.append(f"- Disk Usage: {result['disk_usage_percent']}% used ({result['free_gb']} GB free of {result['total_gb']} GB)")
        elif name == "get_system_information":
            lines.append(f"- Operating System: {result['os']} {result['os_release']}")
        else:
            lines.append(f"- {name}: {result}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo Mode responses (used when no LLM API key is configured)
# ---------------------------------------------------------------------------

DEMO_RESPONSES = {
    "wifi": {
        "problem": "Your device appears to be having a Wi-Fi connectivity issue.",
        "causes": [
            "Incorrect Wi-Fi password or expired credentials.",
            "Router requires a restart.",
            "Wi-Fi adapter driver is outdated.",
            "Too many devices connected to the same network.",
        ],
        "steps": [
            "Confirm Wi-Fi is enabled and Airplane Mode is off.",
            "Restart the router by unplugging it for 30 seconds.",
            "Forget the Wi-Fi network on your device and reconnect.",
            "Update the Wi-Fi adapter driver via Device Manager.",
        ],
        "solution": "Restart both the router and your device, then reconnect to the Wi-Fi network with the correct password.",
    },
    "internet": {
        "problem": "You appear to be experiencing an internet connectivity issue.",
        "causes": [
            "ISP outage in your area.",
            "Modem/router needs a restart.",
            "Loose cable connection.",
            "Firewall or antivirus blocking network traffic.",
        ],
        "steps": [
            "Check the modem/router status lights for errors.",
            "Restart the modem and router (power cycle for 30 seconds).",
            "Test another device on the same network.",
            "Contact your ISP if the issue persists across all devices.",
        ],
        "solution": "Power cycle your modem and router; if multiple devices are affected, contact your ISP.",
    },
    "windows": {
        "problem": "You appear to be experiencing a Windows operating system issue.",
        "causes": [
            "Corrupted system files.",
            "A recent faulty Windows update.",
            "Driver incompatibility.",
        ],
        "steps": [
            "Restart the computer.",
            "Run 'sfc /scannow' from an elevated Command Prompt.",
            "Check Windows Update for a recent update to roll back.",
            "Boot into Safe Mode to isolate the cause if the issue persists.",
        ],
        "solution": "Run the System File Checker (sfc /scannow) and ensure Windows is fully updated.",
    },
    "printer": {
        "problem": "Your printer appears to be having a connectivity or configuration issue.",
        "causes": [
            "Printer is offline or not set as default.",
            "Print spooler service has stalled.",
            "Outdated printer driver.",
        ],
        "steps": [
            "Confirm the printer is powered on and connected.",
            "Set the printer as default in Settings > Printers.",
            "Restart the Print Spooler service (services.msc).",
            "Reinstall the printer driver if the issue continues.",
        ],
        "solution": "Restart the Print Spooler service and confirm the printer is set as default.",
    },
    "bluetooth": {
        "problem": "Your device appears to be having a Bluetooth pairing or connection issue.",
        "causes": [
            "Bluetooth disabled on one of the devices.",
            "Device not in pairing mode.",
            "Outdated Bluetooth driver.",
        ],
        "steps": [
            "Ensure Bluetooth is enabled on both devices.",
            "Remove the device from paired devices and pair again.",
            "Update the Bluetooth driver via Device Manager.",
        ],
        "solution": "Remove and re-pair the Bluetooth device, updating the driver if needed.",
    },
    "software": {
        "problem": "An application on your computer appears to be malfunctioning.",
        "causes": [
            "Corrupted installation files.",
            "Missing dependency (e.g., .NET Framework or Visual C++ Redistributable).",
            "Conflicting background process.",
        ],
        "steps": [
            "Restart the computer and try opening the application again.",
            "Run the application as Administrator.",
            "Reinstall the application.",
            "Install any missing dependencies.",
        ],
        "solution": "Reinstall the application after confirming all required dependencies are present.",
    },
    "network": {
        "problem": "You appear to be experiencing a general local network issue.",
        "causes": [
            "IP address conflict.",
            "Network discovery disabled.",
            "Faulty Ethernet cable or port.",
        ],
        "steps": [
            "Release and renew the IP address (ipconfig /release, ipconfig /renew).",
            "Enable Network Discovery in Network and Sharing Center.",
            "Try a different Ethernet cable or port.",
        ],
        "solution": "Renew the IP configuration and confirm devices are on the same network profile.",
    },
    "performance": {
        "problem": "Your computer appears to be running slower than expected.",
        "causes": [
            "High CPU or memory usage from background processes.",
            "Too many startup applications.",
            "Low free disk space.",
        ],
        "steps": [
            "Open Task Manager and check CPU/Memory usage.",
            "Close unnecessary applications and browser tabs.",
            "Disable unneeded startup programs.",
            "Free up disk space using Disk Cleanup.",
        ],
        "solution": "Identify and close the top resource-consuming process, then free up disk space.",
    },
    "login": {
        "problem": "You appear to be having trouble logging into your account.",
        "causes": [
            "Forgotten password.",
            "Account temporarily locked after failed attempts.",
            "Two-factor authentication device unavailable.",
        ],
        "steps": [
            "Use the official 'Reset password' option on the login screen.",
            "Wait for a lockout timer to expire, or contact an administrator.",
            "Use backup codes if 2FA is unavailable.",
        ],
        "solution": "Use the account provider's official password reset process; never attempt unofficial bypass methods.",
    },
    "dns": {
        "problem": "You appear to be experiencing a DNS resolution issue.",
        "causes": [
            "ISP DNS server is slow or down.",
            "Corrupted local DNS cache.",
            "Misconfigured DNS settings.",
        ],
        "steps": [
            "Flush the DNS cache: ipconfig /flushdns.",
            "Switch to a public DNS server such as 8.8.8.8 or 1.1.1.1.",
            "Restart the router.",
        ],
        "solution": "Flush the DNS cache and switch to a public DNS provider such as Google DNS (8.8.8.8).",
    },
    "general": {
        "problem": "Your query has been noted as a general IT issue.",
        "causes": [
            "The issue may span multiple categories.",
            "More specific details would help narrow down the cause.",
        ],
        "steps": [
            "Restart the affected device or application.",
            "Check for pending updates.",
            "Describe the specific error message or symptom for more targeted help.",
        ],
        "solution": "Try a restart first, then provide more specific details for targeted troubleshooting.",
    },
}


def build_demo_response(category: str, diagnostic_text: str, sources: List[str]) -> str:
    """Construct a structured demo-mode response using static templates."""
    template = DEMO_RESPONSES.get(category, DEMO_RESPONSES["general"])

    causes_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(template["causes"]))
    steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(template["steps"]))
    sources_text = "\n".join(f"- {s}" for s in sources) if sources else "- (no matching knowledge base sources found)"

    warning_text = (
        "⚠️ This assistant will never bypass account security or execute unsafe system commands."
        if category == "login"
        else "⚠️ Always save your work before restarting your device."
    )

    response = f"""🔍 Problem Identified

{template['problem']}

📌 Possible Causes

{causes_text}

🛠️ Troubleshooting Steps

{steps_text}

🔧 Diagnostic Information

{diagnostic_text}

{warning_text}

✅ Recommended Solution

{template['solution']}

📚 Knowledge Sources Used

{sources_text}

💬 Did this solve your problem? (👍 Helpful / 👎 Not Helpful)
"""
    return response.strip()


# ---------------------------------------------------------------------------
# LLM-backed response generation (used when an API key IS configured)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an AI IT Helpdesk Agent. You help ordinary computer users solve
common IT problems using simple, non-technical language.

You are given:
1. The user's problem description.
2. Relevant knowledge base excerpts (retrieved via RAG).
3. Results from safe, predefined system diagnostic tools (if any were run).
4. Recent conversation history for context.

Always structure your reply using EXACTLY this format, with these emoji headers:

🔍 Problem Identified

📌 Possible Causes

🛠️ Troubleshooting Steps

🔧 Diagnostic Information

⚠️ Warning (include only if relevant; otherwise write "No specific safety warnings.")

✅ Recommended Solution

💬 Did this solve your problem? (👍 Helpful / 👎 Not Helpful)

Rules:
- Base your answer primarily on the provided knowledge base excerpts.
- Reference the diagnostic information naturally if it was provided.
- Never suggest bypassing security, cracking passwords, or accessing another
  person's account or credentials.
- Never instruct the user to run arbitrary or destructive commands.
- Keep language simple and avoid unnecessary jargon.
"""


def call_llm(user_query: str, context_text: str, diagnostic_text: str, history_text: str) -> Optional[str]:
    """
    Call the configured LLM provider to generate the final response.
    Returns None if the call fails for any reason (caller should fall back
    to Demo Mode in that case).
    """
    if Config.DEMO_MODE:
        return None

    user_prompt = f"""Recent Conversation History:
{history_text or '(no prior history)'}

User's Current Problem:
{user_query}

Relevant Knowledge Base Excerpts:
{context_text or '(no relevant knowledge base content found)'}

Diagnostic Tool Results:
{diagnostic_text}
"""

    try:
        if Config.LLM_PROVIDER == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=Config.LLM_API_KEY)
            response = client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=1200,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return "".join(
                block.text for block in response.content if hasattr(block, "text")
            ).strip()

        elif Config.LLM_PROVIDER == "openai":
            from openai import OpenAI

            client = OpenAI(api_key=Config.LLM_API_KEY)
            response = client.chat.completions.create(
                model=Config.LLM_MODEL,
                max_tokens=1200,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content.strip()

        else:
            return None
    except Exception:
        # Any LLM failure gracefully falls back to Demo Mode content.
        return None


# ---------------------------------------------------------------------------
# Main agent entry point
# ---------------------------------------------------------------------------

def process_user_query(user_query: str, history_text: str = "") -> Dict:
    """
    Full agent pipeline for a single user query.

    Returns:
        {
            "category": str,
            "response_text": str,
            "sources": List[str],
            "used_llm": bool,
            "diagnostics": Dict,
        }
    """
    user_query = (user_query or "").strip()
    if not user_query:
        return {
            "category": "general",
            "response_text": "Please describe your IT problem so I can help you (e.g. 'My Wi-Fi is not connecting').",
            "sources": [],
            "used_llm": False,
            "diagnostics": {},
        }

    # Step 1: classify problem category (intent).
    category = classify_category(user_query)

    # Step 2 & 3: RAG retrieval.
    ensure_vector_database_ready()
    retrieval = retrieve_context(user_query)

    # Step 4: decide + run diagnostic tools.
    tool_names = requires_diagnostic_tool(category, user_query)
    diagnostic_results = run_diagnostic_tools(tool_names)
    diagnostic_text = format_diagnostic_results(diagnostic_results)

    # Step 5: generate final response (LLM if available, else Demo Mode).
    llm_response = call_llm(
        user_query=user_query,
        context_text=retrieval["context_text"],
        diagnostic_text=diagnostic_text,
        history_text=history_text,
    )

    if llm_response:
        response_text = llm_response
        used_llm = True
    else:
        response_text = build_demo_response(category, diagnostic_text, retrieval["sources"])
        used_llm = False

    return {
        "category": category,
        "response_text": response_text,
        "sources": retrieval["sources"],
        "used_llm": used_llm,
        "diagnostics": diagnostic_results,
    }
