# Section 1 notes (paste-ready)

Each section below has three parts:
- **Image**: the PNG to insert (Insert > Image > Upload from computer).
- **Text to paste**: goes under the heading in the Google Doc.
- **For the team**: items to check before you submit. Do not paste these.

The `.puml` file next to each PNG is the source. Edit it and render it again if the team changes a class name.

---

## 1.1 Overall System Architecture

**Image:** `1.1-overall-architecture.png`

**Text to paste:**

The Smart Bookstore is a local desktop application. It follows the Model-View-Controller (MVC) pattern and has four layers:

1. **View layer.** One desktop window (MainWindow). It shows the screens for each subsystem. MainWindow holds the current Session and shows or hides screens based on the user's role (VS, RC, VC, SU).
2. **Controller layer.** It holds all business rules. Each of the five subsystems has its own controllers. A subsystem calls another subsystem only through that subsystem's controller or repository (dashed arrows).
3. **Local AI services.** YOLOv8 for face recognition, a librosa + PyTorch classifier for voice, an image matcher for cover search, and a vector index with Ollama for the RAG chat. All models run on the local machine. No cloud service is used.
4. **Model layer.** Repositories read and write JSON files through one shared JsonStore class. JsonStore writes to a temporary file and then renames it, so a crash cannot leave a half-written file.

All data is in a local `data/` folder. The system uses JSON files and no database, as the project description allows.

**For the team:**
- The diagram does not name a GUI library (Tkinter, PyQt, etc.). Add it to the text when the team decides.
- The creative feature is not in any diagram yet. Add it when the team chooses it.

---

## 1.2 Collaboration Class Diagram: Full System

**Image:** `1.2-collaboration-class-diagram.png`

**Text to paste:**

This diagram shows all major classes of the five subsystems and how they collaborate. Each colored box is one subsystem. Black arrows are calls inside one subsystem. Red arrows are calls between subsystems. Dashed arrows show that a class creates or returns an entity.

The main cross-subsystem collaborations are:
- **Purchase (S3 to S1, S2):** TransactionService updates the balance through UserRepository, lowers stock through BookRepository, calls AccountManager to suspend an account with a negative balance, and calls TierPolicy to check for a VIP upgrade.
- **Moderation (S4 to S1, S3):** ConductEnforcer calls AccountManager to add warnings, suspend, or demote. ReviewService asks OrderRepository whether the reviewer bought the book, to set the review weight.
- **Recommendation (S2 to S3):** RecommendationEngine reads purchase history from OrderRepository.
- **RAG chat (S5 to S3):** RagAssistant calls FinanceReport only when the user is an SU.
- **Inventory (S5 to S2, S4):** InventoryManager edits BookRepository, uses BrowseTracker to find books that are rarely viewed, and reads the to-order / no-order lists from OrderListPolicy.

Account state (status, tier, warnings, balance) has one owner: Subsystem 1. Other subsystems change it only through AccountManager, TierPolicy, or UserRepository.

---

## 1.3 Biometric Authentication & User Management (Rasul)

**Image:** `1.3-subsystem1-auth.png`

**Text to paste:**

This subsystem identifies users with face and voice samples and owns all account state.

Class responsibilities:
- **AuthView:** Shows the login screen, captures a face image and a voice clip, and lets a visitor continue without logging in.
- **EnrollmentView:** Captures training samples when a new RC/VC/SU is registered.
- **SuspendedUsersView (SU):** Lists suspended accounts and lets the SU reinstate one.
- **BiometricAuth:** Sends the samples to both classifiers, compares the confidence to a threshold, checks the account status, and creates the Session.
- **FaceRecognizer (YOLOv8):** Detects the face in the image and classifies it as a known user.
- **VoiceClassifier (librosa + PyTorch):** Extracts MFCC features from the clip and classifies the speaker.
- **AccountManager:** Checks status, suspends, reinstates, adds warnings, and demotes VC to RC. Subsystems 3 and 4 call it.
- **TierPolicy:** After each purchase, promotes an RC to VC when purchases > 3 or total spent > $200.
- **UserRepository / User / Session:** Read and write `users.json`. Session holds the logged-in user and role.

**For the team:**
- The project description says log in with face **and/or** voice. UC-01 in the SRS requires **both**. The design supports either. Pick one rule and state it.
- UC-03 allows reinstatement at balance ≥ $0. The project description says the account must have **positive** money. Decide if $0 is enough.
- The description requires a procedure to **train** the face/voice classifier. No use case covers enrollment. I added EnrollmentView and `train()` methods for this.

---

## 1.4 Catalog Search & Recommendation (Thierno)

**Image:** `1.4-subsystem2-catalog.png`

**Text to paste:**

This subsystem shows the top-3 books on the home page and lets users browse and search the catalog by text or image.

Class responsibilities:
- **HomeView:** Shows the top-3 books.
- **CatalogView:** Browse by category, author, or year. Search by keywords or by an uploaded image.
- **BookDetailView:** Shows one book with its stock, rating, and reviews. Opens the purchase and review screens.
- **RecommendationEngine:** For VS and SU, returns the 3 most purchased and browsed books overall. For RC and VC, returns 3 books based on that user's browsing and purchase history. Falls back to the global list when the user has no history.
- **SearchService:** Filters `books.json` by metadata and keywords. Sends image queries to ImageMatcher.
- **ImageMatcher:** Converts an image to a feature vector and returns the closest book covers or figures.
- **BrowseTracker:** Records each book view in `browse_log.json`. RecommendationEngine and InventoryManager use this log.
- **BookRepository / Book:** Read and write `books.json`.

**For the team:**
- The project description says image search works on the cover **or internal figures**. UC-06 mentions only covers. The image index can hold both.
- The SRS does not say which vision model ImageMatcher uses. Name it in the text.

---

## 1.5 Transaction, Deposit & Financial Processing (Dair)

**Image:** `1.5-subsystem3-transactions.png`

**Text to paste:**

This subsystem handles purchases, deposits, fines, and the financial records the SU can view.

Class responsibilities:
- **PurchaseView / DepositView:** Confirm a purchase and show the receipt. Accept a deposit amount and show the new balance.
- **FinanceView (SU):** Shows the financial summary.
- **TransactionService:** Applies the 10% VC discount, compares price to balance, deducts the price, applies the $1 overdraft fine, lowers stock, writes the order and ledger entries, then calls AccountManager (suspend if balance < 0) and TierPolicy (upgrade check).
- **DepositService:** Checks that the amount is > 0, credits the balance, and writes a ledger entry.
- **FinanceReport:** Builds totals from the ledger and orders. The SU finance view and the RAG chat (SU only) use it.
- **OrderRepository / Order:** Read and write `orders.json`. Also answers "did this user buy this book?" for review weighting.
- **Ledger / LedgerEntry:** Append-only record of every PURCHASE, DEPOSIT, and FINE in `ledger.json`.

**For the team:**
- The project description says a purchase that costs more than the balance gets a $1 fine. It does not say if the purchase still goes through. UC-07 completes the purchase and makes the balance negative. Confirm this with the team, because it decides whether TransactionService saves the order.

---

## 1.6 Content Moderation & Community Reviews (Bryant)

**Image:** `1.6-subsystem4-moderation.png`

**Text to paste:**

This subsystem accepts ratings and comments, filters taboo words, applies conduct penalties, and keeps the to-order and no-order lists.

Class responsibilities:
- **ReviewView:** Form for 1–5 stars and a comment.
- **TabooWordView (SU):** Lets the SU add or remove taboo words.
- **ReviewService:** Sends the text to ModerationFilter, saves the review, gives a higher weight to reviews from buyers, updates the book's average rating, and calls OrderListPolicy.
- **ModerationFilter:** Counts taboo words, replaces each with `*`, and marks the review blocked when the count is above the limit.
- **ConductEnforcer:** When a review is blocked, adds a warning through AccountManager. AccountManager suspends or demotes based on the warning count.
- **TabooWordManager:** Reads and writes `taboo_words.json`.
- **OrderListPolicy:** A book with more than 3 ratings and an average below 2 goes on the no-order list. A book with more than 3 ratings and an average above 4 goes on the to-order list. Writes `order_lists.json`.
- **ReviewRepository / Review:** Read and write `reviews.json`.

**For the team (the SRS and the project description disagree here):**
- **Block limit:** the description blocks a comment with **more than 3** taboo words (4 or more). UC-10 blocks at **3 or more**.
- **Who gets a warning:** the description warns only the author of a **blocked** comment. UC-10 also warns for 0–2 masked words.
- **VC penalty:** the description says an RC with more than 2 warnings is suspended and "a VC will be demoted". UC-10 demotes a VC after one blocked comment. The description most likely means a VC with more than 2 warnings is demoted.
- **Who can review:** the description says **any user** can comment, and buyers get a higher weight. UC-09 allows only buyers.
- The to-order / no-order lists are in the project description but not in the SRS. I added OrderListPolicy for them.

---

## 1.7 RAG Intelligence & Inventory Administration (Rosina)

**Image:** `1.7-subsystem5-rag-inventory.png`

**Text to paste:**

This subsystem answers chat questions with local documents or the local LLM, and lets the SU manage the book inventory.

Class responsibilities:
- **ChatView:** Text box for questions. Shows the answer and its source.
- **InventoryView (SU):** Form to add a book, and buttons to remove one or auto-prune rarely viewed books.
- **RagAssistant:** Checks the role with AccessPolicy, searches the local documents with VectorIndex, and answers from them when the match is good enough (answer is labeled "answered via RAG"). Otherwise it sends the question to the Ollama LLM (answer is labeled "answered via LLM").
- **AccessPolicy:** Decides what each role may ask about. VS < RC < VC < SU. Only the SU gets financial reports.
- **VectorIndex:** Stores embeddings of the files in `rag_docs/` and returns the closest passages with a score.
- **OllamaClient:** Calls the local Ollama server for embeddings and text generation.
- **InventoryManager:** Checks required fields and price > 0, adds and removes books, and uses browse data and the order lists to choose books to prune or reorder.

**For the team:**
- The project description says answers get **increasingly more** detail from VS to RC to VC to SU. UC-12 only separates SU from the others. Define what each of the four roles can see.
- Every answer must say whether it came from RAG or the LLM. `Answer.source` holds this.
