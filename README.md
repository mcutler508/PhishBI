# Phish Story Backend

A secure backend server for generating personalized Phish concert stories using Claude AI and fetching data from Phish.net API.

## 🔒 Security

This project uses environment variables to protect API keys. **Never commit the `.env` file to version control.**

## 📋 Setup Instructions

### 1. Install Dependencies

#### Node.js (Backend Server)
```bash
npm install
```

#### Python (Data Fetcher)
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   - `ANTHROPIC_API_KEY`: Your Anthropic Claude API key
   - `PHISHNET_API_KEY`: Your Phish.net API key
   - `PORT`: Server port (default: 3001)

### 3. Run the Applications

#### Start Backend Server
```bash
npm start
```

#### Run Data Fetcher
```bash
python fetch_phish_data.py
```

## 📁 Files

- `backend-server.js` - Express server that handles Claude API calls
- `fetch_phish_data.py` - Python script to fetch Phish data from Phish.net API
- `.env` - Your secret API keys (NOT in version control)
- `.env.example` - Template for required environment variables
- `.gitignore` - Prevents sensitive files from being committed

## 🔑 Getting API Keys

### Anthropic Claude API
1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### Phish.net API
1. Visit [https://phish.net/api/](https://phish.net/api/)
2. Register for an account
3. Request an API key
4. Use the provided API key

## ⚠️ Important Security Notes

- **NEVER** commit `.env` files to Git
- **NEVER** hardcode API keys in your source code
- **NEVER** share your API keys publicly
- The `.gitignore` file is configured to exclude `.env` files

## 🚀 API Endpoints

### Health Check
```
GET /health
```
Returns server status

### Generate Story
```
POST /api/generate-story
```
Accepts Phish attendance data and returns a personalized story from Claude

## 📊 Power BI Integration

The Python script generates `Phish_Complete_Data_API.xlsx` which can be imported directly into Power BI for data visualization and analysis.

