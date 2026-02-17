# FactorLens: Full-Stack Fama-French Factor Analysis Platform

## Overview

A full-stack quantitative finance application using Spring Boot (Java 21), React, PostgreSQL, and Python to perform Fama-French five-factor analysis on a user's stock portfolio.

**Learning Focus**: Spring Boot, PostgreSQL (Docker), and React. Python handles the quant logic.

---

## How This Project Works

User signs up → adds stock holdings (ticker + quantity) → clicks "Run Analysis" → sees results.

Behind the scenes: Spring Boot sends the holdings to a Python Flask service. Flask fetches historical prices from Yahoo Finance, retrieves Fama-French factor data, runs an OLS regression, and returns factor exposures (betas), alpha, and R-squared. Results are stored in PostgreSQL and displayed as charts in React.

---

## Project Explanation (For Non-Finance People)

**What is this project?**

Imagine you own some stocks (like Apple, Tesla, Amazon). You want to understand *why* your portfolio goes up or down. Is it because:
- The whole stock market went up? (Market risk)
- You own small companies that did well? (Size risk)
- You own "cheap" stocks that recovered? (Value risk)
- You own profitable companies? (Profitability)
- You own companies that don't spend much on expansion? (Investment style)

This project uses a famous academic model called the **Fama-French Five-Factor Model** to break down your portfolio's performance into these 5 categories. It's like a nutrition label for your investments—instead of showing calories and protein, it shows how much of your returns came from each "risk factor."

**The Five Factors:**
| Factor | What it measures |
|--------|-----------------|
| MKT-RF (Market) | How much your portfolio moves with the overall market |
| SMB (Size) | Exposure to small companies vs large companies |
| HML (Value) | Exposure to "cheap" stocks vs "expensive" growth stocks |
| RMW (Profitability) | Exposure to highly profitable companies |
| CMA (Investment) | Exposure to conservative vs aggressive companies |

**Why is this useful?**
- If 90% of your risk comes from "small companies," you know you're heavily exposed if small companies crash
- You can see if you're actually skilled at picking stocks (alpha) or just riding market waves
- Professional fund managers use this exact analysis to understand their portfolios

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  React Frontend │◄───►│  Spring Boot API │◄───►│   PostgreSQL    │
│   (Port 3000)   │     │   (Port 8080)    │     │                 │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Python Flask   │
                       │   (Port 5000)    │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  External APIs   │
                       │  yfinance, FF    │
                       └──────────────────┘
```

**Communication Flow:**
1. React UI → Spring Boot (JWT authenticated REST)
2. Spring Boot → Python Flask (analysis requests)
3. Flask → yfinance/Ken French data library
4. Results stored in PostgreSQL

---

## Database Schema

**Design**: Each user has exactly **one portfolio**. User adds holdings (ticker + quantity), clicks "Run Analysis", sees results.

### Entity Relationships

```
User (1) ──────────── (N) Holding
User (1) ──────────── (N) FactorAnalysisResult
FamaFrenchFactor (standalone - cached data)
```

### Entities

**User** - Account info
| Column | Purpose |
|--------|---------|
| id | Primary key (UUID) |
| email | Login identifier |
| passwordHash | BCrypt-hashed password |
| role | USER or ADMIN |

**Holding** - A stock position in the user's portfolio
| Column | Purpose |
|--------|---------|
| id | Primary key |
| userId | FK to User |
| ticker | Stock symbol (e.g., "AAPL") |
| quantity | Number of shares owned |

**FamaFrenchFactor** - Cached factor data from Ken French's library
| Column | Purpose |
|--------|---------|
| id | Primary key |
| factorDate | Date for this data point |
| mktRf, smb, hml, rmw, cma, rf | The 5 factor values + risk-free rate |

**FactorAnalysisResult** - Saved analysis output
| Column | Purpose |
|--------|---------|
| id | Primary key |
| userId | FK to User |
| analysisDate | When analysis was run |
| alpha | Excess return (stock-picking skill) |
| betaMkt, betaSmb, betaHml, betaRmw, betaCma | Factor exposures |
| rSquared | How much the factors explain (0-1) |

---

## Key API Endpoints

### Auth
```
POST /api/v1/auth/register        - Register new user
POST /api/v1/auth/login           - JWT login
POST /api/v1/auth/refresh         - Refresh token
```

### Holdings (User's Portfolio)
```
GET  /api/v1/holdings             - Get user's holdings
POST /api/v1/holdings             - Add a holding
PUT  /api/v1/holdings/{id}        - Update holding quantity
DELETE /api/v1/holdings/{id}      - Remove holding
```

### Analysis
```
POST /api/v1/analysis/run         - Run factor analysis on user's portfolio
GET  /api/v1/analysis/history     - Get past analysis results
GET  /api/v1/analysis/{id}        - Get specific analysis result
```

---

## Features

### Core Features
1. **Dashboard** - View holdings list
2. **Factor Analysis** - Run FF5 regression, view factor exposures (betas), alpha, R-squared
3. **Results Visualization** - Bar chart of factor exposures, summary table

### Optional Features (If Time Permits)
4. **Analysis History** - View past analysis results
5. **Risk Decomposition** - Pie chart showing systematic vs idiosyncratic risk

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, React Router, Axios, Recharts |
| Backend | Spring Boot 4, Java 21, Spring Security, Spring Data JPA |
| Quant Engine | Python 3.11, Flask, statsmodels, pandas, yfinance |
| Database | PostgreSQL 16, JPA/Hibernate |
| DevOps | Docker, Docker Compose |

## Deployment

| Service | Platform | Cost |
|---------|----------|------|
| React Frontend | **Vercel** | Free |
| Spring Boot API | **Render** | Free tier |
| Python Flask | **Render** | Free tier |
| PostgreSQL | **Supabase** | Free (500MB) |

### Production Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│     Vercel      │     │      Render      │     │    Supabase     │
│  React Frontend │────►│  Spring Boot API │────►│   PostgreSQL    │
│                 │     │    (Port 8080)   │     │    (Free)       │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │      Render      │
                        │   Python Flask   │
                        │    (Port 5000)   │
                        └──────────────────┘
```

### Why This Stack?
- **Vercel**: Best-in-class for React, free SSL, automatic deploys from GitHub
- **Render**: Native Docker support, services communicate internally, easy setup
- **Supabase**: Free PostgreSQL forever (500MB), no credit card required

### Environment Variables (Production)
**Spring Boot (Render)**:
```
DATABASE_URL=postgresql://[supabase-connection-string]
JWT_SECRET_KEY=[generate-secure-key]
FLASK_SERVICE_URL=https://[flask-service].onrender.com
```

**Flask (Render)**:
```
FLASK_ENV=production
```

**React (Vercel)**:
```
VITE_API_URL=https://[spring-boot-service].onrender.com
```

---

## To-Do Checklist

### Phase 1: Docker + PostgreSQL
```
[ ] Create docker-compose.yml with PostgreSQL service
[ ] Run docker-compose up -d and verify connection
```

### Phase 2: Spring Boot + JPA Entities
```
[ ] Generate Spring Boot project (Web, JPA, PostgreSQL, Security, Validation, Lombok)
[ ] Configure application.yml (datasource, hibernate ddl-auto: update)
[ ] Create User entity with role enum (USER, ADMIN)
[ ] Create Holding entity (ticker, quantity, @ManyToOne to User)
[ ] Create FamaFrenchFactor entity
[ ] Create FactorAnalysisResult entity (@ManyToOne to User)
[ ] Create repositories and basic services
[ ] Verify Hibernate auto-creates tables
```

### Phase 3: Spring Security + JWT
```
[ ] Add jjwt dependencies
[ ] Create JwtService (generate, validate tokens)
[ ] Create JwtAuthenticationFilter
[ ] Create SecurityConfig with filter chain
[ ] Create AuthController (/register, /login)
[ ] Test auth flow with Postman
```

### Phase 4: Python Flask Service
```
[ ] Create Flask app with blueprints
[ ] Implement factor analysis endpoint
[ ] Fetch FF factors and stock prices
[ ] Run OLS regression with statsmodels
[ ] Return coefficients, t-stats, R-squared
[ ] Test with sample ticker
```

### Phase 5: Spring Boot ↔ Flask Integration
```
[ ] Create PythonServiceClient with RestTemplate/WebClient
[ ] Create AnalysisService and AnalysisController
[ ] Save results to PostgreSQL
[ ] Test end-to-end flow
```

### Phase 6: React Frontend
```
[ ] Create React app with Vite
[ ] Set up AuthContext and ProtectedRoute
[ ] Build Login/Register pages
[ ] Build Dashboard: holdings table + "Add Holding" form + "Run Analysis" button
[ ] Build results display: factor exposure bar chart + summary table
```

### Phase 7: Polish
```
[ ] Add form validation
[ ] Add loading states and error handling
[ ] Basic styling
[ ] Test full user journey
```

### Phase 8: Deployment
```
[ ] Set up Supabase PostgreSQL and get connection string
[ ] Create Dockerfile for Spring Boot
[ ] Create Dockerfile for Flask
[ ] Deploy Spring Boot to Render
[ ] Deploy Flask to Render
[ ] Configure internal service communication on Render
[ ] Deploy React to Vercel
[ ] Configure environment variables on all platforms
[ ] Test production end-to-end
```

---

## Spring Boot Key Concepts

| Concept | Where Used |
|---------|------------|
| `@Entity`, `@Table` | User, Holding, FactorAnalysisResult entities |
| `@ManyToOne`, `@OneToMany` | User ↔ Holding relationship |
| `@Repository` | Data access layer |
| `@Service` | Business logic |
| `@RestController` | REST endpoints |
| `@ControllerAdvice` | Global exception handling |

---

## React Key Concepts

| Concept | Where Used |
|---------|------------|
| `useState`, `useEffect` | Component state, fetching holdings/results |
| `useContext` | Auth state (JWT token) |
| React Router | Login → Dashboard navigation |
| Axios | API calls to Spring Boot |
| Recharts | Factor exposure bar chart |

---

## Flask Quant Service

### Dependencies (requirements.txt)
```
flask==3.0.*
flask-cors
pandas
numpy
statsmodels
yfinance
pandas-datareader
gunicorn
```

### Key Endpoints
```
POST /api/analysis/factor-regression   - Run FF5 regression
GET  /api/health                       - Health check
```
