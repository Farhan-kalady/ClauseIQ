# ClauseIQ Frontend Manual Test Checklist (Sprint 3)

This checklist provides standard verification procedures for the ClauseIQ React frontend interface (`http://localhost:5173`).

---

## 1. System Health & Initial Page Loading

- [ ] **1.1 Server Health & Status Indicator**
  - **Action**: Start backend (`uvicorn api.main:app --port 8000`) and frontend (`npm run dev`). Open `http://localhost:5173`.
  - **Expected Result**: Header displays application title "ClauseIQ", "Sprint 3" badge, and green status pill "Model Ready".
  - **Degraded Check**: Stop the backend server. The indicator should transition to a red status pill "Backend Offline".

- [ ] **1.2 Clean UI Presentation**
  - **Action**: Inspect initial render in browser.
  - **Expected Result**: Dark slate theme loads smoothly with radial background gradients, sharp typography (Inter font), and no unstyled flash of content.

---

## 2. Navigation & View Switching

- [ ] **2.1 Tab Switching**
  - **Action**: Click "Classification" and "Clause Search" in the top navigation.
  - **Expected Result**: Active tab highlight transitions seamlessly without full-page reloads. Corresponding view content mounts cleanly.

- [ ] **2.2 Deep Layout Consistency**
  - **Action**: Switch tabs back and forth multiple times.
  - **Expected Result**: Navbar and footer remain static and anchored; form states do not leak unexpectedly between views.

---

## 3. Clause Classification View (Single Clause Input)

- [ ] **3.1 Valid Benchmark Clause Classification**
  - **Action**: Click "Governing Law" sample button or paste:  
    `"This Agreement shall be governed by, and construed in accordance with, the laws of the State of Delaware."`  
    Click **Classify Clause**.
  - **Expected Result**:
    - Button displays loading spinner and "Classifying...".
    - Result card appears showing Predicted Category: **Governing Law**.
    - Confidence meter displays actual probability percentage (e.g., >80%).
    - Top Alternative Categories list displays 3 distinct alternatives with real probabilities.
    - Model metadata indicates `LogisticRegression`.

- [ ] **3.2 Validation on Empty / Whitespace Input**
  - **Action**: Clear text area and click **Classify Clause** (or leave empty).
  - **Expected Result**: Button remains disabled while input is empty. If spaces are entered, an alert banner displays the backend error message without crashing.

- [ ] **3.3 Gibberish / Out-of-Vocabulary Input**
  - **Action**: Enter `@@@ ### $$$ %%%` and submit.
  - **Expected Result**: Displays error alert banner indicating no valid legal or alphanumeric tokens found.

---

## 4. Contract Document Upload (PDF & TXT Multi-Clause)

- [ ] **4.1 PDF Contract Upload & Clause Splitting**
  - **Action**: Switch to "Upload Contract Document", select `data/raw_pdfs/sample_contract.pdf`, and click **Extract & Classify Document**.
  - **Expected Result**:
    - Loading indicator displays "Extracting & Classifying...".
    - Document title and total clause count (e.g., 29 clauses) are shown.
    - Scrollable list displays each extracted clause with its sequence number, clause text, predicted CUAD category badge, and probability score.

- [ ] **4.2 Plain Text Document Upload**
  - **Action**: Create or select a `.txt` contract file and upload.
  - **Expected Result**: Text is parsed, split into sentences, and classified accurately.

- [ ] **4.3 Empty File Handling**
  - **Action**: Upload a 0-byte file.
  - **Expected Result**: Clean error banner displays: "Uploaded file is empty."

---

## 5. Intelligent Clause Search View

- [ ] **5.1 Search Query Execution**
  - **Action**: Navigate to "Clause Search". Click sample query `"termination for convenience"` or type a custom query. Click **Search**.
  - **Expected Result**:
    - Top ranked clauses are returned (default 5 results).
    - Each result displays: Rank `#1`, `#2`, ..., Cosine Similarity score percentage (e.g. `65.4%`), Predicted Category tag, Source Contract ID, and the complete clause text.
    - Scores appear in strictly non-increasing order.

- [ ] **5.2 Top-K Slider Adjustment**
  - **Action**: Adjust Top Results slider to 10 and click **Search**.
  - **Expected Result**: Returns exactly up to 10 ranked matching clauses.

- [ ] **5.3 Category Filter Dropdown**
  - **Action**: Select `"Governing Law"` from the category dropdown and search `"laws of the state"`.
  - **Expected Result**: All returned search results belong exclusively to the selected category.

- [ ] **5.4 Empty Search / Unmatched Query**
  - **Action**: Search for an unrelated query with a non-matching category filter.
  - **Expected Result**: Clean empty-state message appears: "No matching clauses met the query and filter criteria."

---

## 6. Error & Loading States

- [ ] **6.1 Request In-Flight State**
  - **Action**: Submit a classification or search.
  - **Expected Result**: Action buttons are disabled during network requests; spinners indicate progress.

- [ ] **6.2 Network Error Handling**
  - **Action**: Disconnect network or stop API, then trigger an action.
  - **Expected Result**: Graceful error alert banner appears with user-friendly error text.

---

## 7. Responsive Design Verification

- [ ] **7.1 Mobile Viewport (375px - 480px)**
  - **Action**: Open Chrome DevTools, toggle device mode to iPhone SE / Pixel 7.
  - **Expected Result**: Navbar stacks vertically without overflowing; tab buttons remain easily tappable; text areas and result cards adjust to single-column width.

- [ ] **7.2 Tablet Viewport (768px)**
  - **Action**: Toggle to iPad Mini (768px width).
  - **Expected Result**: Two-column grids gracefully collapse or preserve clean proportions; no horizontal scrollbar on body.

- [ ] **7.3 Desktop Viewport (1200px+)**
  - **Action**: Maximize browser window on standard desktop.
  - **Expected Result**: Main container max-width 1200px centers smoothly with balanced margins.
