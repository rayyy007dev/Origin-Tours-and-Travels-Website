# ORIGIN Tours & Travels — PostgreSQL version

This is the ORIGIN website codebase updated to use PostgreSQL for tours, destinations, and contact enquiries. The existing HTML/CSS design and page structure are retained.

## What changed

- Removed SQLite from the application. Contact submissions now go to PostgreSQL too.
- Replaced the one global PostgreSQL connection with one connection per API request.
- Database setup runs when FastAPI starts, not when `main.py` is imported.
- Added an idempotent `schema.sql` and starter-data seeding. Existing tour rows are not overwritten; sample destinations are inserted only when the destinations table is empty.
- Added protected create/update/delete endpoints for tours and destinations.
- Protected contact-message listing and deletion. Public visitors can submit a message but cannot read other people's messages.
- Added an admin API key requirement to tour/destination management and private enquiry retrieval. The public contact-form submission remains unauthenticated by design.
- Updated the contact form to submit phone and subject fields as well.
- Changed destination-card rendering to use DOM text nodes rather than inserting database content as HTML.

## 1. Requirements

- Python 3.10 or newer
- PostgreSQL installed and running
- pgAdmin 4 (optional GUI for managing the database)

## 2. Create the database in pgAdmin

1. Open pgAdmin and connect to your local PostgreSQL server.
2. Right-click **Databases** → **Create** → **Database**.
3. Name it `origin_db` and save.

Do not create the tables manually. FastAPI creates them on first startup.

## 3. Configure credentials

From the project folder in PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set `POSTGRES_PASSWORD` to the password for your PostgreSQL `postgres` user. Replace `ADMIN_API_KEY` with a long private random value (generate one with `py -c "import secrets; print(secrets.token_urlsafe(32))"`). Keep `.env` private; it is excluded by `.gitignore`.

## 4. Install Python packages

Recommended: create a virtual environment in the project folder.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can install and run with the virtual-environment interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 5. Start FastAPI

Run this from the folder containing `main.py`:

```powershell
py -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

On startup, the application:

1. Connects to `origin_db`.
2. Creates `tours`, `destinations`, and `contact_messages` if they do not exist.
3. Inserts the starter tours if their slugs are not already present.
4. Inserts the sample destinations only if the destinations table is empty.

The setup does not drop tables or delete existing rows.

## 6. Check the database in pgAdmin

Refresh **Servers → PostgreSQL → Databases → origin_db → Schemas → public → Tables**. You should see:

- `tours`
- `destinations`
- `contact_messages`

Right-click a table → **View/Edit Data** → **All Rows**. You can also use the Query Tool:

```sql
SELECT * FROM tours ORDER BY category, sort_order;
SELECT * FROM destinations ORDER BY id;
SELECT * FROM contact_messages ORDER BY created_at DESC;
```

## 7. API routes

Public routes:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Check database connection |
| GET | `/api/tours` | List all tours |
| GET | `/api/tours?category=domestic` | Filter tours by category |
| GET | `/api/destinations` | List destinations |
| POST | `/api/contact` | Save a contact enquiry |
| GET | `/api/services` | List services |

Admin-key-protected routes:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/contact` | Read private contact enquiries |
| DELETE | `/api/contact/{contact_id}` | Delete an enquiry |
| POST / PUT / DELETE | `/api/tours` and `/api/tours/{tour_id}` | Manage tours |
| POST / PUT / DELETE | `/api/destinations` and `/api/destinations/{destination_id}` | Manage destinations |

For protected endpoints in `/docs`, provide the `X-Admin-Key` header using the value of `ADMIN_API_KEY` from `.env`. Never put this key in frontend JavaScript. A future admin dashboard must call the API through a secure server-side authentication/session design; this simple key is suitable only for local development and controlled testing.

## Important notes

- FastAPI serves the website from `public/`. PostgreSQL stores package and enquiry data, while the website uses local image files in `public/New folder/`; the database stores image paths, not image binaries.
- This ZIP does not contain your real `.env` or any local database file.
- Old records in the excluded SQLite `origin.db` are not automatically migrated. This code creates a new PostgreSQL `contact_messages` table. Keep a backup of any old database and migrate it separately if those enquiries matter.
- The API is suitable for local development. Do not deploy it publicly with the simple `X-Admin-Key` setup as its only admin security. Production requires proper user authentication, authorization, HTTPS, rate limiting, backups, and schema migrations.
