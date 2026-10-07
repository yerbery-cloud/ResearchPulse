# ResearchPulse

An AI-powered research intelligence engine for collecting, filtering, and organizing research information.

## Current Features

- Collect papers from multiple arXiv RSS feeds
- Remove duplicate entries
- Score papers by research relevance
- Automatically assign research tags
- Store papers in SQLite
- Search and rank papers with SQL

## Project Structure

```text
.
├── main.py
├── collector.py
├── filter.py
├── database.py
├── config.py
├── data/
└── requirements.txt
```

## Run
```text
pip install -r requirements.txt
python main.py
```

## Status
Early development version