# Deploy Digital Twin to Render

## Quick Start

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create Render Account**:
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

3. **Deploy from Dashboard**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository: `abhinav-vasudevan/Digital-Twin`
   - Render will automatically detect `render.yaml`
   - Click "Apply" to deploy

## What Gets Deployed

- **Service Type**: Web Service (Free Tier)
- **Runtime**: Python 3.10.12
- **Start Command**: `uvicorn service.api:app --host 0.0.0.0 --port $PORT`
- **Auto-deployed on**: Every push to `main` branch

## Important Notes

### Data Persistence
- **⚠️ Free Tier Limitation**: Render's free tier does NOT persist file storage
- User data in `service/data/*.json` will be lost on every redeploy or sleep
- For production, upgrade to a paid plan or use:
  - PostgreSQL database (Render provides free PostgreSQL)
  - MongoDB Atlas (free tier available)
  - Redis for session storage

### Free Tier Behavior
- App goes to sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- Subsequent requests are fast

## Alternative: Manual Deployment

If Blueprint doesn't work, deploy manually:

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: digital-twin
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && mkdir -p service/data && for file in users.json profile.json meal_plans.json daily_logs.json; do if [ ! -f service/data/$file ]; then echo '{}' > service/data/$file; fi; done`
   - **Start Command**: `uvicorn service.api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Click "Create Web Service"

## Accessing Your App

Once deployed:
- URL: `https://digital-twin-XXXX.onrender.com` (Render assigns unique URL)
- View logs in Render dashboard
- App automatically redeploys on git push

## Troubleshooting

### Build Fails
- Check Render logs for Python/pip errors
- Ensure `requirements.txt` is correct
- Verify Python version compatibility

### App Crashes
- Check "Logs" tab in Render dashboard
- Look for import errors or missing dependencies
- Verify all JSON files are initialized

### Slow First Load
- Normal for free tier (cold start)
- Upgrade to paid tier for instant responses
- Or keep app awake with uptime monitor (e.g., UptimeRobot)

## Upgrading for Production

To handle real users:

1. **Add Database** (Render PostgreSQL):
   - Create PostgreSQL database in Render
   - Update code to use database instead of JSON files
   - Add `psycopg2-binary` to requirements.txt

2. **Upgrade to Starter Plan** ($7/month):
   - Persistent disk storage
   - No sleep/cold starts
   - Better performance

3. **Add Environment Variables**:
   - Set `SECRET_KEY` for secure sessions
   - Configure database connection strings
   - Add any API keys needed

## Repository Structure

```
Digital-Twin/
├── service/
│   ├── api.py              # FastAPI application
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   └── data/              # JSON storage (not persistent on free tier)
├── requirements.txt        # Python dependencies
├── render.yaml            # Render configuration
└── RENDER_DEPLOY.md       # This file
```
