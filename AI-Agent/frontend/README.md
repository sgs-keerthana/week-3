# AI AGENT

Workspace AI is an AI-powered workspace assistant built using React, FastAPI, LangChain/LangGraph, Qwen, and Ollama.

It provides a single natural-language chat interface for Gmail, Google Calendar, and Weather. The AI agent selects the required tool based on the user's request and can perform multi-tool workflows.

## Features

- AI Agent using Qwen + Ollama
- Gmail search, read, draft, classification, and labeling
- Google Calendar event retrieval, free-slot search, and event creation
- Current weather and forecast
- Multi-tool orchestration
- PostgreSQL conversation memory
- Streaming AI responses
- Terminal execution logs
- Google OAuth authentication

## Tech Stack
Frontend: React
Backend: FastAPI
Language: Python
Agent: LangChain / LangGraph
LLM: Qwen3.5 :4b
Local Model Runtime: Ollama
Database: PostgreSQL
ORM: SQLAlchemy
Email: Gmail API
Calendar: Google Calendar API
Weather: Open-Meteo API

## PROJECT STRUCTURE
AI-Agent/
├── backend/
│   ├── tools/
│   │   ├── gmail.py
│   │   ├── calendar.py
│   │   └── weather.py
│   ├── agent.py
│   ├── main.py
│   ├── crud.py
│   ├── database.py
│   ├── db_models.py
│   ├── schemas.py
│   ├── settings.py
│   └── requirements.txt
│
├── frontend/
│   └── ...
│
├── README.md
└── .gitignore

## Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

## Ollama setup
ollama pull qwen3.5:4b

## Google authentication setup
1. Create a Google Cloud Project
2. Configure OAuth Consent Screen.
3. Create OAuth Credentials
4. Gmail Authentication
5. Calendar Authentication

## Frontend setup
cd frontend
npm install
npm run dev


## Flow
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │  React Frontend │
                  │  Chat Interface │
                  └────────┬────────┘
                           │
                    POST /chat
                           │
                           ▼
                  ┌─────────────────┐
                  │ FastAPI Backend │
                  └────────┬────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       PostgreSQL                  Conversation
       Database                    Context
              │                         │
              └────────────┬────────────┘
                           ▼
                    ┌─────────────┐
                    │  AI Agent   │
                    │ Qwen+Ollama │
                    └──────┬──────┘
                           │
                 Agent decides tool
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Gmail Tool      Calendar Tool    Weather Tool
          │                │                │
          ▼                ▼                ▼
      Gmail API       Google Calendar   Open-Meteo
                           API              API
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                     Tool Result(s)
                           │
                           ▼
                      AI Agent
                           │
                  Generate final answer
                           │
                           ▼
                  FastAPI Streaming
                           │
                           ▼
                    React Frontend
                           │
                           ▼
                         USER
