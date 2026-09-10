# Demo Instructions — Step-by-Step

Follow these steps during your project demonstration or viva.

**Step 1: Start the application**
```bash
cd AI_IT_Helpdesk_Agent
venv\Scripts\activate
streamlit run app.py
```

**Step 2: Open the AI Helpdesk chat**
- The Home page and chat interface load together on the main page.
- Note the Mode banner at the top (🟡 Demo Mode or 🟢 Live Mode).

**Step 3: Enter a sample problem**
- Type or click the example button:
  `"My Wi-Fi is connected but internet is not working."`

**Step 4: Show RAG sources**
- After the response appears, expand "📚 Knowledge Sources Used" to show
  which knowledge base files (e.g., `wifi.txt`, `internet.txt`) were
  retrieved and used.

**Step 5: Show diagnostic tool results**
- Point out the "🔧 Diagnostic Information" section in the response, showing
  live internet connectivity and local IP results gathered by the safe
  diagnostic tools.

**Step 6: Show the AI diagnosis**
- Walk through the full structured response: Problem Identified, Possible
  Causes, Troubleshooting Steps, Diagnostic Information, Recommended
  Solution.

**Step 7: Give feedback**
- Click 👍 Helpful or 👎 Not Helpful under the response and show the toast
  confirmation.

**Step 8: Open Chat History**
- Navigate to the "📜 Chat History" page and show the stored conversation
  with its category, response, and feedback.

**Step 9: Open Statistics**
- Navigate to the "📊 Statistics" page and show the total queries, feedback
  counts, and category breakdown chart.

**Step 10: Show System Diagnostics**
- Navigate to the "🛠️ System Diagnostics" page and demonstrate the
  "Check Internet", "Check DNS", "System Information", and
  "Performance Check" buttons.

**Optional Step 11: Show Knowledge Base management**
- Navigate to "📚 Knowledge Base" and demonstrate viewing a document and
  rebuilding the vector database.
