# Viva Preparation — 20 Questions & Answers

Answers are given in simple English, with a short Tanglish version below each
for easier verbal explanation.

---

**1. What is an AI Agent?**
An AI Agent is a program that can perceive an input (like a user's question),
decide what steps to take, and act — for example, retrieving information or
calling a tool — before producing a final response, rather than just giving
a single fixed reply.
*Tanglish:* AI Agent nu solra oru program, adhu user kேட்கிற question-a
puriuchikitu, ethana steps edukanum nu decide pannitu, tools/RAG use panni
final answer kudukkum.

**2. What is RAG?**
RAG (Retrieval-Augmented Generation) is a technique where the AI first
searches a knowledge base for relevant information, then uses that retrieved
information to generate a more accurate, grounded answer instead of relying
only on what it was trained on.
*Tanglish:* RAG na, AI first knowledge base la irundhu relevant info
search pannum, apram andha info vechu answer generate pannum — idhu vechu
answer accurate ah irukum.

**3. Why is RAG used in this project?**
It ensures troubleshooting answers are grounded in a specific, curated IT
knowledge base rather than generic or possibly incorrect general knowledge.
*Tanglish:* Namma specific IT troubleshooting knowledge base vechu correct
answer kudukanumnu RAG use pannirukom.

**4. What is a vector database?**
A vector database stores text as numerical vectors (embeddings) and allows
fast similarity search to find the most relevant pieces of text for a query.
*Tanglish:* Vector database na, text-a numbers (vectors) ah maathi store
pannum, apram similar meaning irukura text-a fast ah search pannalam.

**5. What are embeddings?**
Embeddings are numerical representations of text that capture its meaning,
so that texts with similar meaning have vectors that are close to each other.
*Tanglish:* Embeddings na, text oda meaning-a number vector ah convert
pandradhu — same meaning irukura sentences oda vectors close ah irukum.

**6. What is a Sentence Transformer?**
A Sentence Transformer is a pretrained model that converts a sentence or
paragraph into a fixed-length embedding vector, used here to embed both
knowledge base chunks and user queries.
*Tanglish:* Sentence Transformer nu oru model, adhu sentence ah fixed-size
vector ah convert pannum.

**7. What is tool calling?**
Tool calling is when the AI agent decides to invoke a specific, predefined
function (like checking internet connectivity) to get real, live information
before answering.
*Tanglish:* Tool calling na, AI agent live system info (internet check,
CPU usage) edukka oru specific function-a call pannum.

**8. Why is Streamlit used?**
Streamlit allows building an interactive, multi-page web UI in pure Python
quickly, without needing separate frontend frameworks like React or HTML/CSS.
*Tanglish:* Streamlit vechu fast ah, pure Python la, nice UI create
pannalam — React, HTML thevai illa.

**9. Why is Python used?**
Python has mature libraries for AI/ML (Sentence Transformers, ChromaDB), web
UI (Streamlit), and system diagnostics (psutil), making it ideal for
integrating all three components of this project.
*Tanglish:* Python la AI, ML, system diagnostics ku nalla libraries
irukku, so idha use pannirukom.

**10. How does the AI Agent work in this project?**
It classifies the problem category using keyword matching, retrieves
relevant knowledge base chunks via RAG, decides which diagnostic tools (if
any) apply to that category, runs them, and combines everything into a
final structured response.
*Tanglish:* Agent first category detect pannum, apram RAG use panni
info edukkum, appuram tools run pannum, final ah ellam serthu answer
kudukkum.

**11. How does RAG work in this project?**
Knowledge base .txt files are chunked, embedded using Sentence Transformers,
and stored in ChromaDB. A user's query is embedded the same way and compared
against stored chunks using similarity search to find the top-k most
relevant pieces.
*Tanglish:* Knowledge base files chunk pannitu, embed pannitu, ChromaDB la
store pandrom. User query kூட embed pannitu, similar chunks find
pandrom.

**12. How does the system retrieve documents?**
Using cosine-similarity search over stored embedding vectors in ChromaDB;
the closest matching chunks (lowest distance) are returned as context.
*Tanglish:* ChromaDB la stored vectors kூட user query vector-a compare
pannitu, close ah irukura chunks-a edukkum.

**13. How is conversation memory implemented?**
A `ConversationMemory` class stores the recent turns (user + assistant
messages) and the last detected category in the Streamlit session state, so
follow-up messages can be understood in context.
*Tanglish:* ConversationMemory class recent messages-a store pannum, so
next question ku andha context use pandrom.

**14. Why is SQLite used?**
SQLite is a lightweight, file-based, zero-configuration database that is
perfect for a single-user college project needing persistent chat history
and feedback storage without a separate database server.
*Tanglish:* SQLite na simple file-based database, separate server thevai
illa, so college project ku easy ah use pannalam.

**15. How is security handled?**
Only a fixed set of predefined, read-only diagnostic functions can be
called; no user input is ever passed into a shell command, and there is no
code path for arbitrary command execution, credential access, or destructive
system operations.
*Tanglish:* Fixed safe functions mattum than call pandrom, user kudukra
command edhuvum direct ah run pannoma — idhu security ku romba
important.

**16. What happens when the API key is missing?**
The application automatically detects the missing key and switches to Demo
Mode, showing a yellow banner and using rich template-based responses while
keeping RAG, tools, memory, and database features fully functional.
*Tanglish:* API key illana, app automatic ah Demo Mode ku switch aagum,
but ella features um work aagum.

**17. What are the limitations of this project?**
The intent classifier is keyword-based rather than a trained ML model, Demo
Mode answers are template-based, and diagnostics cover common checks only,
not deep hardware-level diagnostics.
*Tanglish:* Intent classify pandradhu keyword based, ML model illa; Demo
Mode answers templates than; deep hardware diagnostics illa.

**18. What is the difference between a chatbot and an AI Agent?**
A simple chatbot usually maps input patterns directly to fixed responses. An
AI Agent perceives the input, reasons about what additional steps are
needed (retrieval, tool calls), takes those actions, and then generates a
response based on the combined results.
*Tanglish:* Chatbot na fixed pattern ku fixed reply mattum kudukkum. AI
Agent na, adhu reason pannitu, tools/RAG use pannitu, apram answer
kudukkum — so agent smart ah irukum.

**19. What are the future enhancements planned?**
Replacing keyword classification with a trained ML/NLP classifier, adding
voice input and multilingual support, integrating with real ticketing
systems, and expanding the diagnostic tool set.
*Tanglish:* ML classifier add pannradhu, voice input, multiple languages,
ticketing system integration, more diagnostic tools — idhu ellam future
plans.

**20. What is your contribution to this project?**
*(To be answered personally by the student — e.g., designing the agent
pipeline, implementing the RAG retrieval system, building the Streamlit UI,
writing the knowledge base content, and testing the end-to-end system.)*
*Tanglish:* *(Idha personal ah, neenga enna work pannirukeenga nu solli
solunga.)*
