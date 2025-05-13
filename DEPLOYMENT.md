# Deployment Guide

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ATT-FIN-Real-Estate-AI-BOT.git
cd ATT-FIN-Real-Estate-AI-BOT
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Running the Application

### CLI Tool
```bash
# Analyze a specific zipcode
python run_bot.py analyze --zipcode=90210

# Start interactive chat mode
python run_bot.py chat
```

### Dashboard
```bash
streamlit run dashboard.py
```

## Production Deployment

### Frontend (Streamlit)

#### Option 1: Streamlit Cloud
1. Push your code to GitHub
2. Connect your repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Configure environment variables in Streamlit Cloud dashboard
4. Deploy

#### Option 2: Vercel
1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

### Backend (FastAPI)

#### Deploy to Fly.io
1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login and create app:
```bash
fly auth login
fly launch
```

3. Configure secrets:
```bash
fly secrets set OPENAI_API_KEY=your_key_here
fly secrets set ATTOM_API_KEY=your_key_here
```

4. Deploy:
```bash
fly deploy
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key
- `CLAUDE_API_KEY`: Anthropic Claude API key (optional)
- `ATTOM_API_KEY`: ATTOM Data API key
- `DEFAULT_AI_PROVIDER`: Default AI provider (openai/claude/custom)
- `REDIS_URL`: Redis connection URL
- `DATABASE_URL`: PostgreSQL connection URL

## Security Notes

1. Never commit `.env` files or API keys
2. Use secret management in production
3. Enable CORS only for trusted domains
4. Rate limit API endpoints
5. Validate and sanitize all inputs

## Monitoring

1. Set up Prometheus metrics
2. Configure Grafana dashboards
3. Enable error tracking (e.g., Sentry)
4. Monitor API usage and costs

## Scaling

1. Use Redis caching for API responses
2. Configure auto-scaling on Fly.io
3. Implement request queuing for heavy analysis
4. Cache AI responses when possible

## Troubleshooting

Common issues:
1. API rate limits: Implement exponential backoff
2. Memory usage: Monitor and adjust cache TTLs
3. Cold starts: Use warm-up endpoints
4. Database connections: Implement connection pooling
