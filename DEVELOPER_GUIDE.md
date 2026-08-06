
# Developer Guide

# Application Assistant

---

# Purpose

Application Assistant is a Django web application designed to help job seekers organize and track every aspect of their job search.

The application provides:

- Job application tracking
- Interview management
- Resume optimization using OpenAI
- Analytics dashboard
- User account management

---

# Technology Stack

## Backend

- Python 3
- Django 6
- SQLite3

## Frontend

- HTML5
- CSS3
- JavaScript

## AI

- OpenAI API

## Version Control

- Git
- GitHub

---

# Project Structure

```
application_assistant/

│
├── application_assistant/
│
│   settings.py
│   urls.py
│   wsgi.py
│
├── applications/
│
│   admin.py
│   forms.py
│   models.py
│   urls.py
│   views.py
│
│   services/
│       resume_ai.py
│
├── templates/
│
│   base.html
│
│   applications/
│
├── static/
│
│   css/
│   images/
│
└── manage.py
```

---

# Django Request Flow

A request follows this sequence:

```
Browser

↓

urls.py

↓

views.py

↓

models.py

↓

Database

↓

views.py

↓

Template

↓

Browser
```

---

# URL Routing

The project begins inside

```
application_assistant/urls.py
```

This file routes requests into

```
applications/urls.py
```

Each URL is mapped to a specific view.

Example

```
home/

↓

home_view()

↓

home.html
```

---

# Models

## JobApplication

Stores:

- Company
- Position
- Status
- Salary
- Location
- Recruiter
- Job URL
- Applied Date
- Follow-up Date
- Notes

Purpose:

Represents one job application.

---

## Interaction

Related to JobApplication.

Stores:

- Interview Type
- Date
- Feedback
- Outcome

Purpose:

Allows unlimited interview records for each application.

Relationship

```
JobApplication

1

↓

Many

Interaction
```

---

# Forms

Django Forms validate user input before data reaches the database.

Forms include:

- Create Application
- Update Application
- Resume AI
- User Settings

Benefits

- Validation
- CSRF protection
- Cleaner templates

---

# Views

Views receive HTTP requests.

Responsibilities

- Retrieve database information
- Validate forms
- Build context dictionaries
- Render templates

Example

```
Request

↓

View

↓

Database Query

↓

Context

↓

Template
```

---

# Templates

Templates display data returned by views.

Major templates

- Dashboard
- Applications List
- Application Detail
- Create Application
- Analytics
- Resume AI
- Settings

All templates extend

```
base.html
```

---

# Static Files

CSS is separated by page.

```
styles.css

navbar.css

dashboard.css

application-list.css

application-form.css

application-detail.css

analytics.css

resume-ai.css

settings.css
```

This keeps styling modular and maintainable.

---

# Authentication

Uses Django Authentication.

Anonymous users

↓

Login Required

↓

Authenticated User

↓

Dashboard

Protected views use

```
@login_required
```

---

# Resume AI

Workflow

User pastes

- Job Description

and

- Resume

↓

OpenAI API

↓

Prompt Engineering

↓

Tailored Resume

↓

Displayed to user

---

# Analytics

Dashboard metrics include

- Total Applications
- Active Interviews
- Offers
- Rejections
- Average Response Time
- Recent Applications
- Stale Applications

---

# Future Architecture

Planned additions

- PostgreSQL
- Docker
- Redis
- Celery
- Email notifications
- PDF resume generation
- AI Cover Letters
- Calendar integration
- REST API
- Mobile App

---

# Coding Standards

Naming

Models

PascalCase

Variables

snake_case

Templates

lowercase_with_underscores

CSS

kebab-case

---

# Git Workflow

Feature Branch

↓

Develop

↓

Testing

↓

Main

No code is pushed directly to Main.

---

# Deployment

Current

Local Development

Future

- Render
- Railway
- DigitalOcean
- PostgreSQL
- Cloud Storage

---

# Lessons Learned

This project demonstrates

- Django architecture
- CRUD operations
- Authentication
- Model relationships
- Template inheritance
- Static file organization
- API integration
- AI integration
- Git workflow
