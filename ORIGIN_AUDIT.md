> **Historical audit note (November 12, 2026):** This audit describes the codebase before the PostgreSQL refactor. The mixed SQLite/PostgreSQL findings and recommendations below are historical, not the current implementation. The current setup is documented in `README.md`; PostgreSQL schema and initialization are in `schema.sql`, `database.py`, and `seed_data.py`.

# ORIGIN Audit and Learning Roadmap

## 1. Project overview

ORIGIN is a travel and tour website project combining static HTML/CSS/JavaScript pages with a Python FastAPI backend. The repository contains a marketing-style website for domestic and international tours, as well as a backend API for contact messages and destination data.

The project is not yet a clean single-stack app. It is a hybrid of:
- static frontend pages under `public/`, such as `index.html`, `tours.html`, `contact.html`, `about.html`, and similar files
- a FastAPI backend in `main.py`
- a local SQLite database at `origin.db`
- PostgreSQL-oriented logic in `main.py` that appears intended for a richer backend setup

This makes the project valuable for learning, but it also creates operational inconsistency. The app currently combines SQLite and PostgreSQL design patterns in one codebase without a single coherent strategy.

### Verified findings
- The root folder contains multiple HTML pages, CSS files, JavaScript files, and a Python backend file.
- `main.py` imports `fastapi`, `sqlite3`, `psycopg`, `BaseModel`, and `CORSMiddleware`.
- The frontend uses `fetch()` to call backend endpoints.
- There is no `requirements.txt`, `pyproject.toml`, or `package.json` in the repo root.
- `origin.db` exists and contains a `contacts` table.

### Assumptions to treat carefully
- The project likely aims to support a brochure website plus enquiry system, not a full booking engine.
- Some feature work appears more advanced than the current implementation maturity supports.
- Parts of the backend look experimental or partially migrated rather than finished product architecture.

## 2. Existing technology stack

### Verified stack
- Python
- FastAPI
- Pydantic
- SQLite3
- `psycopg` (PostgreSQL driver)
- HTML
- CSS
- JavaScript

### Evidence
- `main.py` imports `fastapi`, `sqlite3`, `psycopg`, `BaseModel`, and `CORSMiddleware`.
- `main.py` defines routes such as `@app.post("/api/contact")`, `@app.get("/api/tours")`, `@app.get("/api/destinations")`, and `@app.delete("/api/Destinations/{destination_id}")`.
- `public/index.html` loads CSS through `link rel="stylesheet" href="style.css"` and uses JavaScript-driven tour cards.
- `contact.html` sends a POST request to `http://127.0.0.1:8000/api/contact`.
- `script.js` contains `loadTourCards()` and `loadDestinations()`, which call the backend API.

### Not verified as currently present
- SQLAlchemy usage was not found in the reviewed project files.
- Alembic migration setup was not found.
- A real authentication system was not found.
- A test suite was not found.
- A production deployment configuration file was not found.

## 3. Current implementation status

### 3.1 Completed and working (verified only where directly supported)
- Static marketing pages exist for the site.
- A backend exists and responds at a basic API level.
- The contact form submission flow is implemented in the frontend (`contact.html`) and backend (`main.py`).
- A SQLite table for contact messages exists in `origin.db`.
- Tour and destination API routes exist in `main.py`.

### 3.2 Implemented but incomplete or inconsistent
- Mixed database approach: SQLite and PostgreSQL are both referenced in the same app.
- The PostgreSQL connection is initialized at import time in `main.py`, which creates an import-time dependency risk.
- The `contacts` table schema and `submit_contact_message()` route are not fully aligned with some commented-out earlier code in the same file.
- Some routes are named inconsistently (`/api/Destinations/{destination_id}` instead of lowercase naming conventions), and the parameter name `Destination_id` is not conventional Python naming.
- `get_tours()` reads from PostgreSQL while the project also has a local SQLite database.

### 3.3 Present but potentially broken
- The backend is likely to fail when PostgreSQL is not running, because `postgres_connection = psycopg.connect(...)` runs immediately at module import.
- The app contains a `CREATE TABLE IF NOT EXISTS tours` block that assumes PostgreSQL features such as `SERIAL`, `TEXT[]`, and `ON CONFLICT` syntax.
- The browser is calling `http://127.0.0.1:8000` directly, which works only if the FastAPI server is started and listening on that port.
- There is no clear environment configuration file or startup script.

### 3.4 Not implemented or not verified
- Admin dashboard
- Authentication and user roles
- Inquiry status management
- Email notifications
- Booking confirmation workflows
- Real booking persistence
- A tested production deployment setup
- CI/test pipeline

## 4. Existing database architecture

### SQLite database
The project has a local SQLite database file named `origin.db`.

Verified schema from the database:
- table: `contacts`
- columns: `id`, `name`, `email`, `message`

This is the database used by the contact form route in `main.py`:
- `submit_contact_message()` inserts into `contacts`
- `get_contact_messages()` reads from `contacts`

### PostgreSQL logic in backend
`main.py` contains PostgreSQL-specific code, including:
- `postgres_connection = psycopg.connect(...)`
- `initialize_tours_table()`
- `get_tours()`
- `get_destinations()`
- `create_destination()`
- `update_destination()`
- `delete_Destination()`

This indicates the code was designed to use a PostgreSQL `tours` table and a `destinations` table. However, there is no migration system or schema definition file to explain how this is intended to be maintained.

### Important issue
The project currently uses two database patterns in one app:
- SQLite for contact data
- PostgreSQL for destinations and tours

This is not necessarily wrong for a learning project, but it is not a stable or clearly documented setup.

## 5. Problems and technical debt

### Verified technical debt
1. Import-time PostgreSQL connection risk
   - `postgres_connection = psycopg.connect(...)` runs immediately when `main.py` is imported.
   - If PostgreSQL is not running or not configured, the application may fail before routes are even used.

2. Mixed database architecture
   - Contact logic uses SQLite.
   - Tour and destination logic uses PostgreSQL.
   - This creates confusion and complicates maintenance.

3. No dependency manifest
   - There is no `requirements.txt` or equivalent dependency file in the project root.
   - This makes setup unclear and fragile.

4. No test suite
   - No `pytest` or equivalent tests were found.
   - That means app reliability is not protected by automated checks.

5. Inconsistent route and naming conventions
   - Some routes are lowercase (`/api/contact`, `/api/tours`), while a delete route uses `/api/Destinations/{destination_id}` with uppercase `D`.
   - The function name `delete_Destination` does not follow standard Python naming conventions.

6. Weak operational safety
   - There is no explicit authentication or authorization for admin operations.

7. No deployment configuration
   - No `.env.example`, deployment docs, or environment setup notes beyond the minimal README are present.

### Assumptions to distinguish from facts
- The app may be intended to evolve into a real tourism management system.
- The PostgreSQL design may be a future-ready architecture even though SQLite is currently used for contact storage.
- The code may have been created incrementally and not yet standardized.

## 6. Features still required

### Must-prioritise features for a usable travel site
1. Stable backend startup and database configuration
2. Contact form persistence and admin view for messages
3. Destination data management
4. Tour listing management
5. Inquiry / booking flow for end users

### Important but secondary features
- Admin dashboard for enquiries
- Inquiry status management
- Email notifications
- Search/filter improvements
- Better validation and error messages

### Features not yet justified by evidence
- Payment integration
- WebSockets
- Celery/async job queues
- Redis caching
- React front-end rewrite
- Dockerization (unless deployment requires it)

## 7. Technologies I actually need to learn

### Essential
#### Python fundamentals
- What to learn: variables, functions, loops, lists, dictionaries, error handling, modules, and virtual environments.
- Why the project needs it: `main.py` is Python code and beginner understanding is required before modifying or debugging it.
- Feature to implement: a simple contact-submission or destination route.
- Before moving on: you should be able to read and reason about Python scripts without copying code blindly.

#### SQL and SQLite
- What to learn: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, table schemas, foreign keys, and normalization.
- Why the project needs it: `origin.db` is already in use for contacts, and the app is database-driven.
- Feature to implement: storing and retrieving enquiries in a database table.
- Before moving on: you should be able to design a small table and explain the difference between data and schema.

#### PostgreSQL basics
- What to learn: PostgreSQL setup, SQL syntax, table creation, data types, `SERIAL`, and connection configuration.
- Why the project needs it: `main.py` explicitly uses PostgreSQL for tours and destinations.
- Feature to implement: one PostgreSQL-backed destination table and one API endpoint that reads from it.
- Before moving on: you should understand why SQLite is simpler for learning and why PostgreSQL is helpful for production.

#### FastAPI
- What to learn: route decorators, response handling, query parameters, request models, and CORS.
- Why the project needs it: the backend is built with FastAPI.
- Feature to implement: complete CRUD endpoints for a single feature, such as destinations.
- Before moving on: you should be able to explain the request/response cycle without guessing.

#### Pydantic
- What to learn: `BaseModel`, validation, default values, optional fields, and error messages.
- Why the project needs it: `Destination`, `DestinationUpdate`, and `ContactForm` models are already in the code.
- Feature to implement: validate a travel enquiry or tour form payload.
- Before moving on: you should be able to reason about invalid data and expected errors.

#### HTML, CSS, and JavaScript basics
- What to learn: DOM, forms, fetch, rendering dynamic content, and event listeners.
- Why the project needs it: the website is a static front-end that calls the API.
- Feature to implement: a working contact form or dynamic destination list.
- Before moving on: you should understand how browser actions trigger API calls.

#### Authentication and security basics
- What to learn: session basics, password hashing, authorization, admin-only endpoints, and environment variables.
- Why the project needs it: once enquiry data exists, it should not be publicly editable without control.
- Feature to implement: a protected admin route.
- Before moving on: you should know why secrets and credentials must never be hardcoded.

#### Testing with pytest
- What to learn: writing simple API tests, checking requests and responses, and validating edge cases.
- Why the project needs it: no automated protection exists yet.
- Feature to implement: test the contact form endpoint and one CRUD route.
- Before moving on: you should understand how to verify behavior after a change.

### Useful later
#### SQLAlchemy 2.0
- What to learn: ORM models, sessions, queries, and migrations.
- Why the project needs it: not currently required, but it becomes valuable if the backend grows.
- Feature to implement later: a clean model layer for destinations and enquiries.
- Before moving on: only after you understand raw SQL and FastAPI basics.

#### Alembic
- What to learn: schema migration tools for relational databases.
- Why the project needs it: only if the project moves to a structured ORM-based database workflow.
- Feature to implement later: versioned schema changes.
- Before moving on: learn SQL and migration logic first.

## 8. Technologies I can postpone or skip

### Postpone
- SQLAlchemy 2.0
- Alembic
- Advanced deployment engineering
- More complex admin tooling

### Skip for now
- Redis
- Celery
- WebSockets
- Docker, unless deployment specifically requires it
- React
- HTMX
- Payment gateways
- Complex microservice architecture

These are not necessary for this project in its current form and would add confusion before the project is stable.

## 9. Dependency-ordered learning roadmap

### Step 1: Python foundations
Learn:
- Python syntax
- variables, data types, loops, functions, dictionaries, lists
- error handling
- virtual environments

Practical goal:
- Understand `main.py` line by line and explain what each part is doing.

### Step 2: SQLite and SQL basics
Learn:
- database tables
- CRUD queries
- schema design
- basic normalization

Practical goal:
- Build and inspect a simple `contacts` table and query it by hand.

### Step 3: HTTP basics and JSON
Learn:
- requests and responses
- JSON payloads
- browser API calls
- status codes

Practical goal:
- Understand how `contact.html` posts JSON to `/api/contact` and how the backend responds.

### Step 4: FastAPI fundamentals
Learn:
- route decorators
- request bodies
- path and query params
- CORS configuration
- error handling

Practical goal:
- Recreate one route in a deliberately simple FastAPI mini app and verify it works.

### Step 5: Pydantic validation
Learn:
- `BaseModel`
- field typing
- validation errors
- optional values

Practical goal:
- Build a custom model for a travel enquiry and test invalid input cases.

### Step 6: Full CRUD with SQLite
Learn:
- create, read, update, delete
- backend API endpoints
- database query patterns

Practical goal:
- Implement or improve enquiry creation and retrieval using SQLite only.

### Step 7: PostgreSQL fundamentals
Learn:
- local PostgreSQL setup
- table creation
- basic queries and constraints
- understanding why production DBs differ from SQLite

Practical goal:
- Create a small PostgreSQL table for destinations and connect it to a FastAPI endpoint.

### Step 8: Frontend integration with JavaScript
Learn:
- fetching data from API
- rendering dynamic lists
- search/filter input
- form submission and UX feedback

Practical goal:
- Make `script.js` clearly responsible for data-driven cards and forms.

### Step 9: Security and admin access
Learn:
- secret management
- environment variables
- authorization basics
- protected endpoints

Practical goal:
- Secure admin access to contact/inquiry data.

### Step 10: Testing and verification
Learn:
- pytest basics
- route tests
- edge cases and validation

Practical goal:
- Write tests for the contact form and at least one CRUD route.

### Step 11: Deployment basics
Learn:
- environment variables
- production settings
- static hosting vs API hosting
- domain and CORS configuration

Practical goal:
- Run the app in a simple local production-like environment and document the steps.

## 10. Recommended implementation order

### Phase 1: Stabilise backend
- Decide on a single database strategy for local development.
- Fix the import-time PostgreSQL dependency problem.
- Confirm that `/api/contact` works reliably.

### Phase 2: Build real enquiry workflow
- Use SQLite for local development.
- Add admin-view endpoints for enquiries.
- Add validation for contact messages.

### Phase 3: Improve destination and tour management
- Keep destinations in a single source of truth.
- Build consistent CRUD routes.
- Confirm the frontend renders API data correctly.

### Phase 4: Add admin features
- Enquiry status tracking
- Basic filtering and sorting
- Protected admin routes

### Phase 5: Deployment readiness
- Environment variables
- Production-safe settings
- Documentation and local verification workflow

## 11. Immediate next steps

### Before coding
1. Read `main.py` and understand every route and database interaction.
2. Decide whether the project will use SQLite or PostgreSQL for local work.
3. Keep the contact flow as the first stable feature to implement.
4. Learn Python basics and SQL basics before changing backend logic.
5. Keep a notebook or notes file for the architecture and code understanding you gain.

### First practical milestone
Create a simple working flow for:
- a contact enquiry POST request
- storing it in SQLite
- reading all enquiries through a GET route
- verifying the API with a browser or API client

### First learning milestone
You should be able to explain:
- what FastAPI does
- what a route is
- what a request model is
- what a database table is
- how the browser and server communicate

## 12. Final recommendation

The best path for this project is not to chase advanced tooling first. The strongest next move is to stabilise the backend, simplify the database choice, and learn the existing architecture deeply enough to extend it confidently.

For a beginner, the most important goal is to become capable of understanding and maintaining this codebase without relying on AI-generated shortcuts. The project is a good learning project exactly because it mixes front-end pages, API routes, and database layers in a realistic way.

## 13. Verified vs assumed summary

### Verified
- There is a FastAPI backend in `main.py`.
- There is a local SQLite `origin.db` with a `contacts` table.
- There is PostgreSQL-oriented code in `main.py`.
- The website uses frontend JavaScript fetches to call backend APIs.
- No test suite, dependency manifest, or deployment config was found in the repo root.

### Assumed or recommended
- The project is meant to become a full travel website with destinations and enquiries.
- A simplified local single-database setup is the right beginner strategy.
- Advanced tools like Redis, Celery, and React are not necessary right now.

This audit is intentionally conservative: it records only what can be verified from the repository and clearly separates that from recommendations and future implementation planning.
