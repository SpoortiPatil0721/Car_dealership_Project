# Putting LotLine online

Live site: https://car-dealership-project-9uz4.vercel.app

Everything runs on Vercel's free plan:

- The React app is built and served as a normal website.
- The FastAPI backend runs as a Python function from `api/index.py`.
- Both share one address, so the frontend just calls `/api/...` and there's no CORS setup.
- The database is a free Neon PostgreSQL database, created from inside Vercel.

Every push to `main` on GitHub redeploys the site automatically.

## 1. Push the code to GitHub

Create an empty **public** repo on GitHub (no README, no .gitignore). Then, from the project folder:

```bash
git remote add origin https://github.com/<your-username>/car-dealership.git
git push -u origin main
```

Don't run `git init`, the folder already has its history.

## 2. Import the repo into Vercel

1. Go to https://vercel.com and sign up with **Continue with GitHub**.
2. Click **Add New... > Project**, find `car-dealership` and click **Import**.
3. Leave the settings as they are. `vercel.json` in the repo already tells Vercel how to build the frontend and where the API is.
4. Open **Environment Variables** on the same screen and add:

   | Name | Value |
   | --- | --- |
   | `JWT_SECRET` | any long random text, 40+ characters |
   | `ADMIN_EMAILS` | `admin@dealership.com` |
   | `SEED_DEMO_DATA` | `true` |
   | `SEED_PASSWORD` | the password you want for the two demo logins |

5. Click **Deploy**. This first deploy will finish, but logins won't work yet because there's no database. That's the next step.

## 3. Add a free Neon database

1. In your Vercel project, open the **Storage** tab.
2. Click **Create Database**, pick **Neon** (Serverless Postgres) and choose the free plan.
3. Pick a region close to you and connect it to your project (all environments).
4. Go to **Settings > Environment Variables** and check that `DATABASE_URL` is now listed. Vercel adds it for you.
5. Go to **Deployments**, open the menu on the latest one and click **Redeploy**.

The app creates its tables and the demo data on its first request.

## 4. Check it

- Open https://car-dealership-project-9uz4.vercel.app/api/health. You should see `{"status":"ok"}`.
- Open https://car-dealership-project-9uz4.vercel.app and log in with `admin@dealership.com` and your `SEED_PASSWORD`.

## Postman against the live site

Change `baseUrl` in your Postman environment to `https://car-dealership-project-9uz4.vercel.app`. Everything else stays the same.

## If something goes wrong

| Problem | Fix |
| --- | --- |
| Login says "Can't reach the server" | Open `/api/health` on your site. If it errors, check the function logs under **Deployments > (latest) > Functions** |
| Health works but login fails with a server error | `DATABASE_URL` is missing. Redo step 3 and redeploy |
| Admin pages missing after registering your own account | Add your email to `ADMIN_EMAILS`, redeploy, then register with that email |
| Changed an environment variable and nothing happened | Variables only apply to new deployments. Click **Redeploy** |

## Notes

- The first request after the site has been idle can take a second or two while the function and database wake up. After that it's quick.
- Want to run the API somewhere else? It's a normal FastAPI app: `uvicorn app.main:create_app --factory` from `backend/`, with `DATABASE_URL` pointing at any PostgreSQL. Point the frontend at it by building with `VITE_API_URL=<api address>` and add the frontend's address to `CORS_ORIGINS`.
