# Indian Military Heroes — 6-Week Story Course

A fully static, database-free self-learning web course with **30 stories** of Indian military heroes — valor, sacrifice, and service across six weeks of structured learning. No backend, no framework, no build step — open `index.html` via any static server or deploy to Netlify in one click.

---

## Table of Contents

1. [Course Overview](#1-course-overview)
2. [Architecture](#2-architecture)
3. [Design](#3-design)
4. [Data Model](#4-data-model)
5. [Application Logic](#5-application-logic)
6. [File Structure](#6-file-structure)
7. [Local Development](#7-local-development)
8. [Deployment — Netlify](#8-deployment--netlify)
9. [Adding or Editing Content](#9-adding-or-editing-content)
10. [Adding Hero Photos](#10-adding-hero-photos)
11. [Progress & Storage](#11-progress--storage)

---

## 1. Course Overview

| | |
|---|---|
| **Duration** | 6 weeks (modules) |
| **Stories** | 30 (5 per module) |
| **Story quiz questions** | 150 (5 per story) |
| **Module quiz questions** | 30 (5 per module) |
| **Reflection prompts** | 30 (1 per story) |
| **Module summaries** | 6 (1 per war/module) |

Each module covers one war or operational period in India's military history:

| Week | War / Conflict | Period | Heroes |
|------|---------------|--------|--------|
| 1 | 1947–48 Kashmir War | Oct 1947 – Jan 1949 | Somnath Sharma, Jadunath Singh, Piru Singh, Karam Singh, Mohammad Usman |
| 2 | 1962 Sino-Indian War | Oct – Nov 1962 | Shaitan Singh, Joginder Singh, Jaswant Singh Rawat, Dhan Singh Thapa, Karam Singh (Rezang La) |
| 3 | 1965 Indo-Pak War | Aug – Sep 1965 | Abdul Hamid, Ardeshir Tarapore, Desmond Hayde, Trevor Keelor, Nirmal Singh |
| 4 | 1971 Liberation War | Dec 1971 | Sam Manekshaw, Arun Khetarpal, Nirmal Jit Sekhon, Albert Ekka, Kuldip Singh Chandpuri |
| 5 | Kargil War | May – Jul 1999 | Vikram Batra, Manoj Kumar Pandey, Sanjay Kumar, Yogendra Singh Yadav, K.K. Nachiketa |
| 6 | Special Ops & Peacekeeping | 1940s – 1990s | K.S. Thimayya, Nand Singh, Gurbachan Salaria, Bana Singh, Ramaswamy Parameswaran |

### Learning path per module

```
Lesson 1 → Lesson 2 → Lesson 3 → Lesson 4 → Lesson 5
                                                    ↓
                                        Module Summary & Quiz
                                                    ↓
                                           Module Badge Earned
```

Each lesson contains:
- **Story blocks** — Life Story · Impact on India · Legacy
- **Reflection prompt** — a personal writing exercise saved in-browser
- **Story quiz** — 5 MCQ questions on that hero

After completing all 5 lessons in a module, the **Module Summary & Quiz** unlocks:
- A rich war-context summary (causes, key battles, outcome, lasting significance)
- A heroes roll-call showing completion status
- An activity and a real-world challenge
- A 5-question **module-level quiz** on the war itself

Completing all 30 lessons and all 6 module quizzes unlocks the **Certificate of Completion**.

---

## 2. Architecture

### Principle: Zero-dependency static site

```
Browser
  │
  ├── GET /index.html          → app shell (HTML skeleton only)
  ├── GET /styles.css          → all styles
  ├── GET /app.js              → all app logic
  └── GET /data/course.json    → all course content (246 KB, one fetch)
```

There is no server-side rendering, no API, no database, and no build pipeline. The entire course is one JSON file fetched once at startup. All routing is hash-based (`#module/module-1/lesson-1-1`), so the server never needs to handle URL routing — it always serves `index.html`.

### Request lifecycle

```
1. Browser loads index.html
2. app.js executes → reads window.location.hash → calls init()
3. init() → fetch('/data/course.json') → state.course populated
4. render() dispatches to renderHome() / renderModulePage() / renderCertificate()
5. User navigates → hashchange event fires → render() called again
6. All subsequent navigation is instant (data already in memory)
```

### State

All runtime state lives in a single `state` object in the IIFE closure:

```
state = {
  route:   { name, moduleId, lessonId }   ← parsed from window.location.hash
  course:  { title, subtitle, modules[] } ← loaded from course.json, never mutated
  progress: { completed, scores,          ← read from / written to localStorage
               reflections, moduleQuizScores }
}
```

---

## 3. Design

### Technology choices

| Concern | Choice | Reason |
|---------|--------|--------|
| Language | Vanilla JS (ES2020) | No build step, no bundler, no dependencies |
| Styling | Plain CSS with custom properties | No preprocessor needed; responsive via grid + clamp() |
| Routing | Hash-based (`#route/params`) | Works on any static host without server config |
| Data | Single JSON file | One fetch, zero API surface, trivially editable |
| Storage | `localStorage` | No login, no server, progress survives page refresh |
| Hosting | Netlify (static) | Free tier, global CDN, automatic HTTPS |

### UI layout

**Home page**
```
┌─────────────────────────────────────────────────────────┐
│ Topbar: brand · nav (Course / Modules / Certificate)    │
├──────────────────────────────┬──────────────────────────┤
│ Hero banner:                 │ Progress panel:          │
│  title + subtitle            │  weeks / stories /       │
│  [Start Week 1] [Modules]    │  completed stats         │
│                              │  progress bar            │
├──────────────────────────────┴──────────────────────────┤
│ Module grid (3 columns):                                │
│  card: week pill · title · war · progress bar · heroes  │
└─────────────────────────────────────────────────────────┘
```

**Module page**
```
┌─────────────────────┬───────────────────────────────────┐
│ Sidebar (sticky):   │ Lesson content area:              │
│  ← All modules      │  Hero header (photo, award, hook) │
│  Module card        │  Story blocks (Life/Impact/Legacy)│
│  Lesson tabs ×5     │  Reflection textarea              │
│  ─────────────────  │  Quiz (5 MCQ questions)           │
│  Module Summary tab │                                   │
└─────────────────────┴───────────────────────────────────┘
```

**Module Summary page** (unlocked after all 5 lessons)
```
┌─────────────────────┬───────────────────────────────────┐
│ Sidebar (same)      │ Summary header (war + period)     │
│                     │ War context paragraph             │
│                     │ Activity + Challenge              │
│                     │ Heroes roll-call grid             │
│                     │ Module Quiz (5 MCQ)               │
└─────────────────────┴───────────────────────────────────┘
```

### Responsive breakpoints

| Breakpoint | Change |
|---|---|
| `> 980px` | Two-column layout (sidebar + content); three-column module grid |
| `≤ 980px` | Single-column layout; sidebar unsticks; two-column grid |
| `≤ 660px` | Single-column grid; topbar stacks vertically; reduced padding |

### Colour palette

| Token | Value | Used for |
|---|---|---|
| `--ink` | `#1f2623` | Body text |
| `--muted` | `#5f6965` | Secondary text, labels |
| `--paper` | `#fbfaf5` | Page background |
| `--surface` | `#ffffff` | Card backgrounds |
| `--saffron` | `#d97824` | Progress bar gradient start |
| `--green` | `#1f7a55` | Progress bar gradient end, correct answers |
| `--gold` | `#bf8b28` | Week pills, module summary accents |
| `--maroon` | `#8b2f35` | Eyebrow text, story block headings |
| `--blue` | `#285b8f` | Pill default, activity section accent |

---

## 4. Data Model

All course content lives in `data/course.json`. The shape is:

```
course
├── title
├── subtitle
├── sourceNote
└── modules[]
    ├── id             "module-1" … "module-6"
    ├── week           1 … 6
    ├── title
    ├── war
    ├── period
    ├── focus          one-sentence description shown on module cards
    ├── activity       learning activity for the module
    ├── challenge      real-world action prompt
    ├── summary        6–8 sentence war context paragraph
    ├── moduleQuiz[]   5 × { question, options[4], answer(index) }
    └── lessons[]      5 per module
        ├── id         "lesson-1-1" … "lesson-6-5"
        ├── hero       display name
        ├── rank
        ├── years      "YYYY–YYYY"
        ├── regiment
        ├── award
        ├── war
        ├── value      short descriptor shown as pill
        ├── link       Wikipedia / authoritative URL
        ├── hook       one-line dramatic opening sentence
        ├── photoUrl   "/images/heroes/<name>.jpg"
        ├── blocks[]   3 × { title, body }
        │              titles: "Life Story" / "Impact on India" / "Legacy"
        ├── reflection single thought-provoking question
        └── quiz[]     5 × { question, options[4], answer(index) }
```

Quiz `answer` is a **0-based index** into the `options` array.

---

## 5. Application Logic

All logic is in [`app.js`](app.js) — a single self-executing function with no global exports.

### Key functions

| Function | Responsibility |
|---|---|
| `init()` | Fetch `course.json`, populate `state.course`, call `render()` |
| `parseRoute()` | Parse `window.location.hash` into `{ name, moduleId, lessonId }` |
| `render()` | Dispatch to `renderHome` / `renderModulePage` / `renderCertificate` |
| `renderHome()` | Course landing page with module grid |
| `renderModulePage()` | Sidebar + lesson or summary content |
| `lessonMarkup()` | Hero header, story blocks, reflection, quiz HTML |
| `moduleSummaryMarkup()` | War summary, hero roll, activity, module quiz HTML |
| `bindLesson()` | Wire up complete/quiz/reflection button events |
| `bindModuleQuiz()` | Wire up module quiz check/reset events |
| `evaluateQuiz(prefix, questions)` | Mark correct/wrong options, return `{ correct, total }` |
| `resetQuiz(prefix, count)` | Clear all radio selections and colour classes |
| `renderCertificate()` | Badge wall, completion status, certificate generator |
| `progressBar(done, total)` | Returns progress bar HTML string |
| `loadProgress()` / `saveProgress()` | Read/write `localStorage` |

### Quiz system

Story quizzes and module quizzes share the same engine but are distinguished by a `prefix` string (`"lq"` for lesson quiz, `"mq"` for module quiz). Each `<fieldset>` carries `data-qi` (question index) and `data-prefix` so `evaluateQuiz()` can target them independently without any ID collisions:

```html
<fieldset class="question" data-qi="2" data-prefix="mq"> … </fieldset>
```

### Progress model

```js
progress = {
  completed:        { "lesson-1-1": true, … }           // per-lesson
  scores:           { "module-1:lesson-1-1": {correct, total}, … }
  reflections:      { "lesson-1-1": "text…", … }
  moduleQuizScores: { "module-1": {correct, total}, … }
}
```

Saved to `localStorage` under key `indian-icons-course-progress-v2` on every write. Progress survives full page refresh and browser restarts.

---

## 6. File Structure

```
.
├── index.html              App shell — static HTML skeleton, no content
├── app.js                  All routing, rendering, quiz, and progress logic
├── styles.css              All styles (responsive, custom properties)
├── favicon.ico
│
├── data/
│   └── course.json         Full course content — 6 modules × 5 lessons
│                           246 KB · single fetch at startup
│
├── images/
│   └── heroes/             Hero portrait photos (optional)
│                           Filename format: kebab-case-hero-name.jpg
│
├── netlify.toml            Netlify build settings + HTTP cache headers
├── _redirects              Netlify SPA fallback rule
│
└── scripts/                Legacy seed scripts (not used at runtime)
    ├── seed_military_heroes.js
    ├── seed_course_data.js
    └── seed_db.py
```

> The `scripts/`, `schema.sql`, and `server.py` files are **not used at runtime**. They are the previous SQLite-backed implementation and can be ignored or deleted.

---

## 7. Local Development

The app uses `fetch()` to load `course.json`, which requires an HTTP server (browsers block `fetch` on `file://` URLs).

**Option A — Node (recommended)**
```bash
npx serve .
# Opens at http://localhost:3000
```

**Option B — Python**
```bash
python -m http.server 8000
# Opens at http://localhost:8000
```

**Option C — VS Code**
Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension, then click **Go Live** in the status bar.

No compilation, no `npm install`, no environment variables.

---

## 8. Deployment — Netlify

### One-time setup

1. Push the repository to GitHub (or GitLab / Bitbucket).
2. Log in to [app.netlify.com](https://app.netlify.com) → **Add new site → Import an existing project**.
3. Select the repository.
4. In **Build settings**, set:
   - **Build command**: *(leave blank)*
   - **Publish directory**: `.`
5. Click **Deploy site**.

Netlify reads [`netlify.toml`](netlify.toml) automatically. No further configuration is needed.

### What `netlify.toml` does

```toml
[build]
  publish = "."          ← serve from repo root

[[headers]]
  for = "/data/course.json"
  Cache-Control = "public, max-age=3600"    ← 1 hour CDN cache

[[headers]]
  for = "/*.js"
  Cache-Control = "public, max-age=86400"   ← 1 day

[[headers]]
  for = "/images/*"
  Cache-Control = "public, max-age=604800"  ← 7 days

[[redirects]]
  from = "/*"
  to   = "/index.html"
  status = 200                              ← SPA fallback
```

The `_redirects` file provides the same SPA fallback rule as a plain-text alternative — Netlify supports both formats and the toml rule takes precedence.

### Re-deploying after content changes

Because this is a static site with no build step, every `git push` to the connected branch triggers an instant re-deploy. Netlify typically deploys in under 10 seconds.

To update course content: edit `data/course.json` → commit → push → done.

### Custom domain

In the Netlify dashboard: **Site configuration → Domain management → Add a domain**. Netlify provisions a free Let's Encrypt HTTPS certificate automatically.

---

## 9. Adding or Editing Content

All content is in [`data/course.json`](data/course.json). It is plain JSON — edit it in any text editor.

### Editing a story block

Find the lesson by `id` (e.g. `"lesson-3-2"`) and update the `blocks` array:

```json
"blocks": [
  { "title": "Life Story",      "body": "…" },
  { "title": "Impact on India", "body": "…" },
  { "title": "Legacy",          "body": "…" }
]
```

### Editing a quiz question

Find the lesson's `quiz` array. Each question is:

```json
{
  "question": "What was …?",
  "options":  ["Option A", "Option B", "Option C", "Option D"],
  "answer":   1
}
```

`answer` is a **0-based index** — `1` means "Option B" is correct.

### Adding a module quiz question

Find the module's `moduleQuiz` array. Same shape as story quiz questions.

### Validating the JSON after edits

```bash
python -c "import json; json.load(open('data/course.json', encoding='utf-8')); print('Valid JSON')"
```

Or use any JSON validator / IDE with JSON schema support.

---

## 10. Adding Hero Photos

Photos are optional. The app gracefully omits the `<img>` element when `photoUrl` points to a file that does not exist.

1. Add the photo to `images/heroes/`:
   ```
   images/heroes/vikram-batra.jpg
   images/heroes/somnath-sharma.jpg
   ```

2. The `photoUrl` field in each lesson already contains the correct path:
   ```json
   "photoUrl": "/images/heroes/vikram-batra.jpg"
   ```

**Recommended spec:**
- Format: JPEG
- Dimensions: 400 × 500 px (portrait orientation)
- File size: < 80 KB (the app sets `loading="lazy"` on all hero images)

---

## 11. Progress & Storage

All learner progress is stored in `localStorage` under the key `indian-icons-course-progress-v2`. No data leaves the browser.

| Key | Value |
|---|---|
| `completed` | Object mapping lesson IDs → `true` |
| `scores` | Object mapping `"moduleId:lessonId"` → `{ correct, total }` |
| `reflections` | Object mapping lesson IDs → reflection text string |
| `moduleQuizScores` | Object mapping module IDs → `{ correct, total }` |

### Resetting progress

Open the browser console on the course page and run:

```js
localStorage.removeItem("indian-icons-course-progress-v2");
location.reload();
```

### Certificate unlock condition

The certificate page becomes generatable when **both** of the following are true:
- All 30 story lessons are marked complete (`completed[lessonId] === true` for all 30)
- All 6 module quizzes have been attempted (`moduleQuizScores[moduleId]` exists for all 6)
