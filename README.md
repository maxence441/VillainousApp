# VillainousApp

VillainousApp is a French-language React application for recording Claire and Maxence's Villainous duels, exploring statistics, and browsing a character catalog. The frontend is built with Vite and can be hosted on GitHub Pages; Supabase Auth and Postgres provide shared, protected duel storage.

## Requirements

- Node.js 22.12 or newer and npm
- A Supabase project for the Scores and Stats pages

## Configure Supabase

1. Create a Supabase project.
2. In **Project Settings → API**, copy the project URL and the public anon/publishable key.
3. In **Authentication → Providers / Sign In**, disable public email sign-ups. Create accounts only for the people who should access the archives. The app deliberately has no public registration form.
4. Open **SQL Editor** in the Supabase dashboard and run [`supabase/schema.sql`](./supabase/schema.sql).
5. Add these repository Actions secrets for GitHub Pages builds:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

The anon key is public by design and is included in the browser bundle. Row Level Security is enabled for the `duels` table; keep public sign-ups disabled and never put a Supabase service-role key in the frontend or GitHub Pages secrets.

## Run locally

```sh
npm ci
cp .env.example .env.local
```

Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in `.env.local`, then start Vite:

```sh
npm run dev
```

Run checks and create a production build:

```sh
npm test
npm run build
```

Scores and statistics require signing in with a Supabase account provisioned by the project administrator. The character catalog and home page work without Supabase configuration.

## Deploy to GitHub Pages

1. Rename the GitHub repository to `VillainousApp` (the Pages workflow uses that project URL).
2. In the repository, open **Settings → Pages** and select **GitHub Actions** as the build and deployment source.
3. Add the two Supabase Actions secrets listed above.
4. Push to `main` or `master`, or manually run **Deploy VillainousApp to GitHub Pages** from **Actions**.

The deployment uses hash-based routes so direct visits and page refreshes work on GitHub Pages. After the first successful workflow, GitHub Pages displays the site URL in **Settings → Pages**.

## Run with Docker

Docker builds the static app and serves it through Nginx; no backend or database is bundled.

```sh
cp .env.example .env
```

Add the Supabase URL and public anon key to `.env`, then build and start:

```sh
docker compose up --build
```

Open <http://localhost:8080>. Stop with `Ctrl+C` or run `docker compose down`.

## Data migration

The new app reads and writes to the Supabase `duels` table. It does not automatically copy rows from the former PostgreSQL database or the previous local SQLite file. Export/import any records you still need before retiring those databases.
