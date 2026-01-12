# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PhishBI is a dual-component application that combines data analytics with AI-powered narrative generation for Phish concert data:

1. **Python Data Fetcher** (`fetch_phish_data.py`) - Retrieves comprehensive show data from Phish.net API and generates Excel files for Power BI visualization
2. **Node.js Backend Server** (`backend-server.js`) - Secure proxy server that handles Claude API requests to generate personalized concert attendance narratives

## Core Commands

### Backend Server
```bash
# Start production server
npm start

# Start development server with auto-reload
npm run dev
```

### Data Fetcher
```bash
# Fetch all Phish show data and generate Excel output
python fetch_phish_data.py
```

### Setup
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Then edit .env with your actual API keys
```

## Architecture

### Backend Server (`backend-server.js`)

**Purpose**: Acts as a secure proxy between the frontend (Power BI or web clients) and the Anthropic Claude API, preventing API key exposure in client-side code.

**Key Components**:
- **Express Server**: Runs on port 3001 (configurable via `PORT` env var)
- **CORS Enabled**: Allows cross-origin requests from frontend applications
- **System Prompt**: Contains the "Phish Narrative Intelligence Engine" prompt that instructs Claude to analyze attendance patterns and generate structured JSON responses with 5 required sections:
  1. Overall Arc
  2. Musical Tendencies
  3. Era Shifts & Inflection Points
  4. Venue & Geography Patterns
  5. What Makes This History Distinct

**API Endpoints**:
- `POST /api/generate-story` - Accepts Phish attendance data, forwards to Claude API with system prompt, returns structured JSON narrative
- `GET /health` - Health check endpoint

**Response Format**: The server expects Claude to return a specific JSON structure with confidence levels for each section. The response is parsed from Claude's text output and forwarded to the client.

### Data Fetcher (`fetch_phish_data.py`)

**Purpose**: Comprehensive ETL pipeline that fetches all Phish concert data from Phish.net API and structures it for Power BI analysis.

**Data Flow**:
1. **Fetch Phase**: Retrieves data year-by-year (1983-2025) with rate limiting (0.5s delays)
   - All shows via `/shows/showyear/{year}.json`
   - All venues via `/venues.json`
   - All songs via `/songs.json`

2. **Processing Phase**:
   - Adds computed "Era" field to shows based on Phish's historical periods:
     - 1.0 (1983-2000)
     - Hiatus 1 (2001)
     - 2.0 (2001-2004)
     - Hiatus 2 (2005-2008)
     - 3.0 (2009-2020)
     - 4.0 (2021+)
   - Generates aggregate statistics and summaries

3. **Output Phase**: Creates `Phish_Complete_Data_API.xlsx` with 8 sheets:
   - `Fact_Shows` - All show records with venue, location, tour, ratings
   - `Dim_Venues` - Venue dimension table
   - `Dim_Songs` - Song dimension table with play counts
   - `Fact_Era_Summary` - Shows grouped by Phish era
   - `Fact_State_Summary` - Shows grouped by state/location
   - `Fact_Year_Trend` - Annual show counts
   - `Top_50_Songs` - Most frequently played songs
   - `Metadata` - Fetch timestamp and dataset statistics

**Excel Formatting**: Applies professional styling with custom headers (teal background, white text) and auto-sized columns for Power BI readability.

## Environment Variables & Security

**CRITICAL**: This project uses environment variables for all API keys. The `.env` file is git-ignored and must NEVER be committed.

**Required Variables**:
- `ANTHROPIC_API_KEY` - Your Claude API key (from console.anthropic.com)
- `PHISHNET_API_KEY` - Your Phish.net API key (from phish.net/api)
- `PORT` - Server port (default: 3001)

Both scripts validate environment variables on startup and exit with clear error messages if keys are missing.

**Migration Note**: This project previously had hardcoded API keys that were removed in a security migration. See `SECURITY_MIGRATION.md` for details.

## Data Model

### Phish Era Classification
The system recognizes 6 distinct eras in Phish's history, which is fundamental to narrative analysis:
- Era 1.0: The original run (1983-2000)
- Hiatus 1: First break (2001)
- Era 2.0: Return to touring (2001-2004)
- Hiatus 2: Extended break (2005-2008)
- Era 3.0: Modern era begins (2009-2020)
- Era 4.0: Current era (2021-present)

This classification is used for both data analysis (in Python) and narrative generation (in the Claude system prompt).

## API Integration

### Phish.net API v5
- Base URL: `https://api.phish.net/v5`
- Rate limiting: Script includes 0.5s delays between requests
- Error handling: Checks for both HTTP errors and API-level error messages
- Authentication: API key passed as `apikey` parameter

### Claude API (Anthropic)
- Model: `claude-sonnet-4-20250514`
- Max tokens: 2000
- API version: `2023-06-01`
- The system prompt is ~80 lines and defines strict analytical guidelines for narrative generation
- Expected output: Valid JSON matching the predefined structure

## Development Notes

### Modifying the Narrative Engine
If changing the Claude system prompt or response structure:
1. Update the `SYSTEM_PROMPT` constant in `backend-server.js:27-78`
2. Ensure the JSON parsing logic handles the new structure (`backend-server.js:119-120`)
3. Update any frontend code that consumes the API response

### Extending Data Collection
If adding new data sources from Phish.net:
1. Add new fetch function following the pattern in `fetch_phish_data.py` (see `fetch_all_shows()`, etc.)
2. Create corresponding processing function to structure the data
3. Add new sheet to `dataframes_dict` before calling `create_excel_with_formatting()`

### Power BI Integration
The Excel output is designed for direct import into Power BI:
- Fact tables prefixed with `Fact_`
- Dimension tables prefixed with `Dim_`
- IDs (ShowID, VenueID, SongID) are preserved for relationship modeling
- Era field enables time-based analysis beyond raw years
