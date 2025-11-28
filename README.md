# Bill Data Extraction API

Extracts line items from bills/invoices using Google Gemini 1.5 Flash Vision.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your Google AI Studio API key:
```
GOOGLE_API_KEY=your_key_here
```

4. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

POST `/extract-bill-data`

```json
{
    "document": "https://example.com/invoice.pdf"
}
```

## Response Format

```json
{
    "is_success": true,
    "token_usage": {
        "total_tokens": 1234,
        "input_tokens": 1000,
        "output_tokens": 234
    },
    "data": {
        "pagewise_line_items": [...],
        "total_item_count": 10
    }
}
```

## Deployment

### Option 1: Render (Recommended - Free tier available)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add `GOOGLE_API_KEY=your_key_here`
5. Deploy!

### Option 2: Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variable: `GOOGLE_API_KEY`
4. Railway auto-detects FastAPI and deploys

### Option 3: Fly.io

1. Install flyctl: `iwr https://fly.io/install.ps1 -useb | iex`
2. Login: `fly auth login`
3. Initialize: `fly launch` (in project directory)
4. Set secret: `fly secrets set GOOGLE_API_KEY=your_key_here`
5. Deploy: `fly deploy`

### Option 4: Vercel (Serverless)

1. Install Vercel CLI: `npm i -g vercel`
2. Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [{"src": "app/main.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app/main.py"}]
}
```
3. Deploy: `vercel`
4. Set env var: `vercel env add GOOGLE_API_KEY`

**Note**: For all platforms, make sure to set the `GOOGLE_API_KEY` environment variable in the platform's dashboard.
