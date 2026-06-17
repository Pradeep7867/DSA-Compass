# DSA Compass 

DSA Compass is a Flask-based learning tracker designed to help developers stay consistent while preparing Data Structures & Algorithms (DSA).

The application provides a structured roadmap, daily focus system, revision tracking, and progress monitoring to help learners move through a DSA curriculum without losing momentum.

## Features

### Authentication

* User Registration
* Secure Login
* Password Hashing
* User-specific data isolation

### Curriculum Tracking

* Structured Java DSA roadmap
* Topic-wise progress tracking
* Status management:

  * Not Started
  * In Progress
  * Completed
* Section-wise completion tracking

### Dashboard

* Overall progress percentage
* Topics completed
* Topics in progress
* Current study streak
* Pending revisions
* Section progress overview

### Today's Focus

* Select one topic for daily study
* Mark study session as completed
* Maintain consistency through daily tracking
* Study history tracking

### Revision Queue

* Schedule revisions for completed topics
* Track upcoming revisions
* Mark revisions as completed
* Remove obsolete revision tasks

### Multi-User Architecture

Each user has independent:

* Topic progress
* Daily focus entries
* Study streaks
* Revision schedules

## Tech Stack

### Backend

* Flask
* SQLAlchemy
* Flask-Login
* SQLite

### Frontend

* HTML
* Jinja2
* Bootstrap 5
* Custom CSS

## Database Design

### Core Models

* User
* Section
* Topic
* UserTopicProgress
* FocusEntry
* Revision

## Current Status

### Sprint 1 ✅

* Authentication System
* Curriculum Management
* Dashboard
* Focus Tracking
* Revision Tracking

### Sprint 2 ✅

* Complete Multi-User Migration
* User-Specific Topic Progress
* User-Specific Focus Tracking
* User-Specific Revision Management
* Dashboard Personalization
* Route Security Improvements

## Upcoming Features (Sprint 3)

* Smart Revision Scheduler (Spaced Repetition)
* Problem Solving Tracker
* GitHub-style Consistency Heatmap
* DSA Statistics Dashboard
* Interview Readiness Score
* LeetCode Problem Tracking

## Installation

```bash
git clone <repository-url>
cd DSA-Compass

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

python run.py
```

Open:

```text
http://127.0.0.1:5000
```
##Live Demo
https://dsa-compass.onrender.com/
## Author

Pradeep Sajnani

Built to make DSA preparation structured, measurable, and consistent.
