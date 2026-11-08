# Project Guidance

- Build the frontend with Vite, React, and TypeScript.
- Keep application code in `src/`.
- Store shared duel data in Supabase and enforce access through Row Level Security.
- Do not place Supabase service-role credentials in frontend code or build artifacts.
- Run `npm test` and `npm run build` after changing application behavior.
- Keep the Docker deployment as a static Nginx container.
