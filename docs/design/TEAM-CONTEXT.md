# Smart Bookstore: Team Context

Use this file as context when you work on your part of the Phase 2 design report or the code. You can read it, or paste it into an AI tool before you ask it to write your sections. It lists what is already decided, the class and method names everyone must use, and the format each report section follows.

- Report: "Jie Wei Report 2" (Google Doc, owned by Rasul)
- Repository: https://github.com/rasulmohammad/Smart_Bookstore
- Team: GMI (Bryant Chen, Rasul Mohammad, Thierno Diallo, Rosina Zhou, Dair)

---

## 1. The system in short

- A standalone **desktop app in Python**. Everything runs offline on the local machine. There is no cloud service and no database server.
- **MVC design:**
  - Model: local JSON files (users, books, orders, ledger, reviews, taboo words, order lists, browse log) plus a documents folder for the RAG assistant. All reads and writes go through the shared `JsonStore` class (`src/smart_bookstore/storage/json_store.py`, methods `read(name, default)` and `write(name, data)`). It writes to a temp file first, so a crash cannot corrupt data.
  - View: one desktop GUI window. Screens show or hide by role. The GUI library is **not decided yet** (issue #5).
  - Controller: the classes of the five subsystems below.
- **Local AI:** YOLOv8 (face), librosa + PyTorch classifier (voice), an image model for image search (not decided yet), Ollama (RAG chat and embeddings).
- **Roles:** Visitor (VS), Registered Customer (RC), VIP Customer (VC), Super-User (SU).

## 2. Who owns what

| # | Subsystem | Owner | Code folder |
|---|---|---|---|
| S1 | Biometric Auth & User Management | Rasul | `src/smart_bookstore/auth` |
| S2 | Catalog Search & Recommendation | Thierno | `src/smart_bookstore/catalog` |
| S3 | Transaction, Deposit & Financial Processing | Dair | `src/smart_bookstore/transactions` |
| S4 | Content Moderation & Community Reviews | Bryant | `src/smart_bookstore/moderation` |
| S5 | RAG Intelligence & Inventory Administration | Rosina | `src/smart_bookstore/rag_inventory` |

## 3. Classes and methods (use these exact names)

These names come from `docs/design/section1/gen_class_diagrams.py`, which draws every class diagram in Sections 1.2 to 1.7. If your pseudo-code (Section 4) or code uses a different name, either change your text or change the generator and render the diagrams again, so the report agrees with itself.

| Subsystem | Class | Methods |
|---|---|---|
| S1 | BiometricAuth | `login(face_image, voice_clip)`, `enroll_user(user_id, samples)`, `create_session(user)` |
| S1 | FaceRecognizer | `detect_face(image)`, `identify_face(face)`, `train_model(samples)` |
| S1 | VoiceClassifier | `extract_features(audio)`, `identify_speaker(audio)`, `train_model(samples)` |
| S1 | AccountManager | `check_status(user_id)`, `suspend_user(user_id, reason)`, `reinstate_user(user_id)`, `add_warning(user_id)`, `demote_user(user_id)` |
| S1 | TierPolicy | `check_upgrade(user_id)`, `promote_to_vip(user_id)` |
| S2 | RecommendationEngine | `get_top3(user)`, `global_top3()`, `personal_top3(user_id)` |
| S2 | SearchService | `browse(category, author, year)`, `search_keywords(text)`, `search_image(image)` |
| S2 | ImageMatcher | `embed_image(image)`, `find_similar(vector, k)` |
| S2 | BrowseTracker | `log_view(user_id, book_id)`, `get_history(user_id)`, `least_viewed(n)` |
| S3 | TransactionService | `purchase_book(user, book)`, `apply_discount(user, price)`, `apply_overdraft_fine(user)` |
| S3 | DepositService | `deposit(user, amount)`, `validate_amount(amount)` |
| S3 | OrderHistory | `add_order(order)`, `get_orders(user_id)`, `has_purchased(user_id, book_id)` |
| S3 | Ledger | `record_entry(user_id, type, amount)`, `get_entries(period)` |
| S3 | FinanceReport | `build_summary(period)`, `total_revenue()`, `total_fines()` |
| S4 | ReviewService | `submit_review(user, book, stars, text)`, `get_reviews(book_id)`, `weighted_average(book_id)` |
| S4 | ModerationFilter | `scan_text(text)`, `count_taboo(text)`, `mask_words(text)` |
| S4 | TabooWordManager | `get_taboo_words()`, `add_word(word)`, `remove_word(word)` |
| S4 | ConductEnforcer | `on_blocked(user)` |
| S4 | OrderListPolicy | `evaluate_book(book_id)`, `get_to_order()`, `get_no_order()` |
| S5 | RagAssistant | `handle_query(user, text)`, `is_local_question(text)`, `label_source(answer)` |
| S5 | AccessPolicy | `get_access_level(role)`, `is_allowed(role, topic)` |
| S5 | VectorIndex | `build_index(docs)`, `search(query, k)` |
| S5 | OllamaClient | `embed(text)`, `generate(prompt)` |
| S5 | InventoryManager | `add_book(fields)`, `remove_book(book_id)`, `auto_prune(n)`, `validate_fields(fields)` |

Shared entities used by several subsystems:
- **User:** user_id, name, role, status, balance, warnings, demoted
- **Book:** book_id, title, author, category, price, stock, avg_rating

### Calls between subsystems

| Caller | Calls | Why |
|---|---|---|
| TransactionService (S3) | `AccountManager.suspend_user(user_id, reason)` (S1) | Balance went below $0 after a purchase |
| TransactionService (S3) | `TierPolicy.check_upgrade(user_id)` (S1) | Check VIP promotion after every purchase |
| ConductEnforcer (S4) | `AccountManager.add_warning(user_id)` (S1) | A review was blocked |
| ReviewService (S4) | `OrderHistory.has_purchased(user_id, book_id)` (S3) | Buyers' ratings get more weight |
| RecommendationEngine (S2) | `OrderHistory.get_orders(user_id)` (S3) | Personal top-3 picks |
| TierPolicy (S1) | `OrderHistory.get_orders(user_id)` (S3) | Count purchases and total spent |
| RagAssistant (S5) | `FinanceReport.build_summary(period)` (S3) | SU financial questions only |
| InventoryManager (S5) | `BrowseTracker.least_viewed(n)` (S2) | Find rarely viewed books to prune |
| InventoryManager (S5) | `OrderListPolicy.get_to_order()` (S4) | Do not prune books on the to-order list |

## 4. What Subsystem 1 (Rasul) gives you

If you call an S1 method, this is what it does and returns.

| Method | Returns | What it does |
|---|---|---|
| `AccountManager.check_status(user_id)` | `"Active"`, `"Suspended"`, or None | Reads the account status |
| `AccountManager.suspend_user(user_id, reason)` | bool | Sets status to Suspended and creates a Suspension record. If already suspended, adds the reason to the open record. Ends the user's session. |
| `AccountManager.reinstate_user(user_id)` | bool | SU only. Works only if the balance is **above $0**. Sets status to Active and resets warnings to 0. |
| `AccountManager.add_warning(user_id)` | bool | Adds 1 warning. A **VC is demoted** to RC. An **RC with more than 2 warnings is suspended**. S4 does not need to suspend or demote anyone itself. |
| `AccountManager.demote_user(user_id)` | bool | VC to RC, and sets `demoted = true` |
| `TierPolicy.check_upgrade(user_id)` | bool (true if promoted) | RC becomes VC if they have **more than 3 purchases or more than $200 spent**. Skips users with `demoted = true`. |

S1 data tables (Section 3.2): **User**, **Biometric Profile** (user_id, face_label, voice_label, face_sample_dir, voice_sample_dir, enrolled_at), and **Suspension** (suspension_id, user_id, reason, suspended_at, reinstated_at, reinstated_by).

## 5. Decisions already made

- **Login:** face **and** voice must both match the same user. If the camera or microphone is not available, the remaining method alone is used (UC-01).
- **Reinstatement:** balance must be **positive (> $0)**. This matches the project description. The Phase 1 SRS said >= $0.
- **Demotion:** a VC who is demoted to RC **cannot be promoted again automatically** (the `demoted` flag on User). This may become less strict later.
- **VIP rule:** more than 3 purchases or more than $200 spent. VC gets 10% off.
- **Overdraft:** a purchase that costs more than the balance gets a $1 fine, the purchase still completes, the balance goes negative, and the account is suspended (UC-07, UC-02).

## 6. Still open (settle before you submit or code)

These are tracked as GitHub issues labeled `decision` (#4 to #7).

- **Moderation (Bryant, #4):** the project description and UC-10 disagree on:
  - Block limit: description says more than 3 taboo words (4+). UC-10 says 3 or more.
  - Who gets a warning: description warns only the author of a blocked comment. UC-10 also warns for 1 to 2 masked words.
  - VC penalty: description says demote a VC; UC-10 demotes after one blocked comment. `add_warning` currently demotes a VC on any warning.
  - Who can review: description says any user (buyers get more weight). UC-09 says only buyers.
- **RAG roles (Rosina):** the description says answers get more detailed from VS to RC to VC to SU. UC-12 only separates SU from the rest. Define what each role sees.
- **Image search (Thierno):** description says covers **or internal figures**; UC-06 says only covers. Name the image model.
- **Tech stack (#5):** GUI library, face pipeline details, image matcher, vector index.
- **JSON schemas (#6)** and **creative feature (#7)**. Section 5.7 still has the placeholder "[INPUT FEATURE CHOSEN TOO]".

## 7. Problems found in the report (please fix your part)

- **Method names in Section 4 do not match the class diagrams:**
  - S4 (Bryant): `get_taboo_word()` should be `get_taboo_words()`, and `on_block(user)` should be `on_blocked(user)`.
  - S5 (Rosina): pseudo-code uses `answer_query`, `can_access`, `allowed_levels`, `add_document`, `fallback_answer`, `is_financial_query`, `find_prune_candidates`, `prune_inventory`. The diagram has `handle_query`, `is_allowed`, `get_access_level`, `build_index`, `is_local_question`, `label_source`, `auto_prune`, `validate_fields`. Pick one set and update the other.
- **Order History has no price (Dair):** `TierPolicy.check_upgrade` needs the amount spent. Add an `amount` column to Order History, or S1 will total the Ledger purchase entries instead.
- **`has_purchased` (Dair):** the pseudo-code adds an order. It should only return true or false, because ReviewService uses it as a check.
- **`build_summary` (Dair):** Output is empty and the pseudo-code is unfinished.
- **Empty sections:** 3.1 (full E-R diagram, still has "[include E/R Diagram...]" placeholders), 3.3 (Thierno), 3.7 (shared entities), 4.2 (Thierno), 5.4 and 5.7 screens, 6.1 meeting logs.
- **Other edits:** revision history date "11/17" needs the year (11/17/2026). Heading 4 should say "pseudo-code" (not "psuedo-code"). Search the doc for "[" before you export to PDF.

## 8. Report section formats

**Section 1.3 to 1.7 (per subsystem):** three numbered parts: 1. Subsystem Overview, 2. Core Responsibilities and Functionalities, 3. Key Classes and Their Relationships.

**Section 2 use cases:** UC title, Actor, Normal Scenario (numbered steps), Exceptional Scenario (bullets with a bold name). Use the class names from Section 3 of this file in the steps.

**Section 3 E-R tables:** columns Attribute | Type | Key | Description.

**Section 4 pseudo-code:** one block per method, grouped by class:

```
method_name(param1, param2)
Input: param1 (type), param2 (type)
Output: return type and meaning
Function: one sentence on what the method does.
Pseudo-code:
Connect to database;
...
Close connection;
return result;
```

Call methods of other classes as `ClassName.method(...)` so readers can match them to the class diagram.

## 9. Files in the repo

| Path | What it is |
|---|---|
| `docs/design/section1/NOTES.md` | Paste-ready text for Sections 1.1 to 1.7 and open questions per subsystem |
| `docs/design/section1/gen_class_diagrams.py` | Source of every class diagram. Edit, run `python3 gen_class_diagrams.py`, then render the `.puml` files |
| `docs/design/section1/*.png` | 1.1a architecture, 1.2a/b/c full class diagram in three parts, 1.3 to 1.7 subsystem diagrams |
| `docs/design/section2/` | Petri nets for UC-01, UC-07, UC-10, and the UC-04 diagram |
| `docs/design/section5/` | Screen mockups 5.1 home, 5.2 login, 5.3 catalog, 5.5 balance, 5.6 chat (HTML sources in `src/`) |
| `src/smart_bookstore/storage/json_store.py` | Shared JsonStore |

---

## Appendix: Section 4.1 pseudo-code (Subsystem 1, Rasul)

Full text as it goes in the report. Use it as an example of the Section 4 format and as the exact behavior of the S1 methods you call.

```
BiometricAuth

login(face_image, voice_clip)
Input: face_image (image or None), voice_clip (audio or None)
Output: session object if login succeeds, otherwise an error message (string)
Function: logs a user in with face and voice, then checks that the account is active.
Pseudo-code:
if face_image is None and voice_clip is None:
    return "No camera or microphone found";
face_id = None;
voice_id = None;
if face_image is not None:
    face = FaceRecognizer.detect_face(face_image);
    if face is None:
        return "Biometric Verification Failed";
    face_id = FaceRecognizer.identify_face(face);
    if face_id is None:
        return "Biometric Verification Failed";
if voice_clip is not None:
    voice_id = VoiceClassifier.identify_speaker(voice_clip);
    if voice_id is None:
        return "Biometric Verification Failed";
if face_id is not None and voice_id is not None and face_id != voice_id:
    return "Identity mismatch, please try again";
user_id = face_id if face_id is not None else voice_id;
if AccountManager.check_status(user_id) == "Suspended":
    return suspension notice with the reason;
Connect to database;
user = get user with user_id;
Close connection;
return create_session(user);

enroll_user(user_id, samples)
Input: user_id (int), samples (list of face images and list of voice clips)
Output: boolean, true if enrollment succeeds
Function: saves a new customer's face and voice samples and retrains both models.
Pseudo-code:
if samples.faces is empty or samples.voices is empty:
    return false;
Connect to database;
if user_id not in User records:
    Close connection;
    return false;
save samples.faces to folder face_samples/user_id;
save samples.voices to folder voice_samples/user_id;
create Biometric Profile record (user_id, face_label = user_id, voice_label = user_id,
    face_sample_dir, voice_sample_dir, enrolled_at = now);
Close connection;
all_faces = face samples of every enrolled user;
all_voices = voice samples of every enrolled user;
if not FaceRecognizer.train_model(all_faces):
    return false;
if not VoiceClassifier.train_model(all_voices):
    return false;
return true;

create_session(user)
Input: user (entity)
Output: session object
Function: starts a session and opens the dashboard for the user's role.
Pseudo-code:
session = new session with user_id = user.user_id, role = user.role, login_time = now;
show dashboard for user.role (RC, VC, or SU);
return session;


FaceRecognizer

detect_face(image)
Input: image (webcam frame)
Output: cropped face image, or None if no face is found
Function: finds the face in a webcam frame with YOLOv8.
Pseudo-code:
boxes = YOLOv8 face detector finds faces in image;
if boxes is empty:
    return None;
best = box in boxes with the highest confidence;
if best.confidence < DETECT_THRESHOLD:
    return None;
return image cropped to best;

identify_face(face)
Input: face (cropped face image)
Output: user_id (int), or None if no enrolled user matches
Function: matches a face to an enrolled user.
Pseudo-code:
load trained face model from local file;
scores = model predicts a score for each enrolled user;
best = user_id with the highest score;
if scores[best] < FACE_MATCH_THRESHOLD:
    return None;
return best;

train_model(samples)
Input: samples (list of (user_id, face image) pairs)
Output: boolean, true if training succeeds
Function: trains the face model on the enrollment samples.
Pseudo-code:
faces = empty list;
for (user_id, image) in samples:
    face = detect_face(image);
    if face is not None:
        faces.append((face, user_id));
if faces is empty:
    return false;
train YOLOv8 classification model on faces, with user_id as the label;
save model to local file;
return true;


VoiceClassifier

extract_features(audio)
Input: audio (voice clip)
Output: feature vector (list of float)
Function: turns a voice clip into MFCC features with librosa.
Pseudo-code:
signal = load audio with librosa at a fixed sample rate;
signal = remove silence at the start and end of signal;
mfcc = librosa MFCC values of signal for each frame;
return average of mfcc over all frames;

identify_speaker(audio)
Input: audio (voice clip)
Output: user_id (int), or None if no enrolled user matches
Function: predicts which enrolled user is speaking.
Pseudo-code:
features = extract_features(audio);
load trained PyTorch classifier from local file;
probs = classifier predicts a probability for each enrolled user from features;
best = user_id with the highest probability;
if probs[best] < VOICE_MATCH_THRESHOLD:
    return None;
return best;

train_model(samples)
Input: samples (list of (user_id, voice clip) pairs)
Output: boolean, true if training succeeds
Function: trains the voice classifier on the enrollment samples.
Pseudo-code:
X = empty list;
y = empty list;
for (user_id, clip) in samples:
    X.append(extract_features(clip));
    y.append(user_id);
if X is empty:
    return false;
for epoch in 1 to EPOCHS:
    train classifier on X with labels y;
save classifier to local file;
return true;


AccountManager

check_status(user_id)
Input: user_id (int)
Output: string, "Active" or "Suspended", or None if the user does not exist
Function: tells other classes if an account is in good standing.
Pseudo-code:
Connect to database;
user = get user with user_id;
Close connection;
if user is None:
    return None;
return user.status;

suspend_user(user_id, reason)
Input: user_id (int), reason (string)
Output: boolean, true if the account is suspended
Function: suspends an account and records the reason.
Pseudo-code:
Connect to database;
user = get user with user_id;
if user is None:
    Close connection;
    return false;
if user.status == "Suspended":
    add reason to the user's open Suspension record;
else:
    user.status = "Suspended";
    create Suspension record (next suspension_id, user_id, reason,
        suspended_at = now, reinstated_at = None, reinstated_by = None);
save user;
Close connection;
end the user's session if the user is logged in;
return true;

reinstate_user(user_id)
Input: user_id (int)
Output: boolean, true if the account is reinstated
Function: lets the SU restore a suspended account with a positive balance.
Pseudo-code:
Connect to database;
user = get user with user_id;
if user is None or user.status != "Suspended":
    Close connection;
    return false;
if user.balance <= 0:
    Close connection;
    return false;
user.status = "Active";
user.warnings = 0;
suspension = user's open Suspension record;
suspension.reinstated_at = now;
suspension.reinstated_by = user_id of the logged-in SU;
save user and suspension;
Close connection;
return true;

add_warning(user_id)
Input: user_id (int)
Output: boolean, true if the warning is recorded
Function: adds a warning, then demotes a VC or suspends an RC with more than 2 warnings.
Pseudo-code:
Connect to database;
user = get user with user_id;
if user is None:
    Close connection;
    return false;
user.warnings += 1;
save user;
Close connection;
if user.role == "VC":
    demote_user(user_id);
else if user.role == "RC" and user.warnings > 2:
    suspend_user(user_id, "More than 2 warnings");
return true;

demote_user(user_id)
Input: user_id (int)
Output: boolean, true if the user is demoted
Function: changes a VC back to RC and blocks automatic re-promotion.
Pseudo-code:
Connect to database;
user = get user with user_id;
if user is None or user.role != "VC":
    Close connection;
    return false;
user.role = "RC";
user.demoted = true;
save user;
Close connection;
return true;


TierPolicy

check_upgrade(user_id)
Input: user_id (int)
Output: boolean, true if the user is promoted to VC
Function: checks the VIP rule after each purchase.
Pseudo-code:
Connect to database;
user = get user with user_id;
Close connection;
if user is None or user.role != "RC" or user.demoted == true:
    return false;
orders = OrderHistory.get_orders(user_id);
count = length of orders;
total = 0;
for order in orders:
    total += order.amount;
if count > 3 or total > 200:
    return promote_to_vip(user_id);
return false;

promote_to_vip(user_id)
Input: user_id (int)
Output: boolean, true if the role is changed
Function: changes an RC to VC and tells the user.
Pseudo-code:
Connect to database;
user = get user with user_id;
if user is None:
    Close connection;
    return false;
user.role = "VC";
save user;
Close connection;
show upgrade notification on the user's dashboard;
return true;
```
