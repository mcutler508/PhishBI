// PHISH STORY BACKEND SERVER
// Securely handles Claude API calls without exposing your API key

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();

// Load configuration from environment variables
const PORT = process.env.PORT || 3001;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

// Validate required environment variables
if (!ANTHROPIC_API_KEY) {
  console.error('❌ ERROR: ANTHROPIC_API_KEY is not set in .env file');
  console.error('Please create a .env file with your API key (see .env.example)');
  process.exit(1);
}

// Middleware
app.use(cors()); // Allow frontend to call this backend
app.use(express.json()); // Parse JSON bodies

// System Prompt
const SYSTEM_PROMPT = `System Prompt: Phish Narrative Intelligence Engine
You are a Phish performance and attendance analyst, not a fan chatbot and not a hype generator.
Your job is to interpret a single user's longitudinal Phish attendance and setlist data and produce clear, grounded narrative insights that explain patterns, shifts, and tendencies in their history.

Core Principles (Non-Negotiable)
* You analyze patterns, not moments
* You explain why trends emerged, not just what happened
* You avoid exaggeration, nostalgia bait, or fan clichés
* You never speculate beyond the data provided
* You never rank the user against others unless explicitly instructed
* You do not use emojis, slang, or hype language
* You do not moralize taste ("good", "bad", "better")
* You never invent events, songs, or motivations

You are calm, analytical, and observant — like a music historian reviewing a personal archive.

Your Output Objective
Produce a personalized narrative summary titled "Your Phish Story"

Required Output Structure
Your response must contain exactly 5 sections, in this order:

1. Overall Arc
2. Musical Tendencies
3. Era Shifts & Inflection Points
4. Venue & Geography Patterns
5. What Makes This History Distinct

Return ONLY a JSON object with this exact structure:
{
  "title": "Your Phish Story",
  "overall_arc": {
    "summary": "...",
    "confidence": "high|medium|low"
  },
  "musical_tendencies": {
    "summary": "...",
    "confidence": "high|medium|low"
  },
  "era_shifts": {
    "summary": "...",
    "confidence": "high|medium|low"
  },
  "venue_geography": {
    "summary": "...",
    "confidence": "high|medium|low"
  },
  "distinctive_signature": {
    "summary": "...",
    "confidence": "high|medium|low"
  }
}`;

// API Endpoint: Generate Phish Story
app.post('/api/generate-story', async (req, res) => {
  console.log('📥 Received story generation request');
  console.log('User data:', JSON.stringify(req.body, null, 2));

  try {
    // Call Claude API
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2000,
        system: SYSTEM_PROMPT,
        messages: [{
          role: 'user',
          content: JSON.stringify(req.body)
        }]
      })
    });

    console.log('📡 Claude API response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Claude API error:', errorData);
      return res.status(response.status).json({
        error: errorData.error?.message || 'Claude API request failed'
      });
    }

    const data = await response.json();
    console.log('✅ Claude API success');
    
    // Parse the story from Claude's response
    const storyText = data.content[0].text;
    const storyJSON = JSON.parse(storyText);
    
    console.log('📖 Story generated successfully');
    
    // Return to frontend
    res.json(storyJSON);

  } catch (error) {
    console.error('❌ Server error:', error);
    res.status(500).json({
      error: error.message || 'Internal server error'
    });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Phish Story Backend is running!' });
});

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('🎸 ========================================');
  console.log('   PHISH STORY BACKEND - RUNNING');
  console.log('========================================');
  console.log(`📍 Server: http://localhost:${PORT}`);
  console.log('🔒 API Key: Loaded from .env');
  console.log('✅ CORS: Enabled');
  console.log('========================================');
  console.log('');
  console.log('Ready to generate Phish stories! 🎵');
  console.log('');
});
