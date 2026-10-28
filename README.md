# FlagRank: E-Commerce Search Ranking Anomaly Detection Framework

FlagRank is an empirical, platform-independent research framework and web application designed to detect potentially unexplained search ranking behaviour on e-commerce marketplaces using observable marketplace signals.

The system builds an expected-ranking baseline using observable attributes (such as price, rating, review volume, discounts, and title relevance) to compute ranking deviations, query-relative peer group inconsistencies, and empirical suspiciousness scores without accessing proprietary search algorithms.

---

## 1. System Architecture

FlagRank consists of two core components:

```
┌─────────────────────────────────────────────────────────────┐
│                      FlagRank System                        │
├─────────────────────────────┬───────────────────────────────┤
│    Frontend Web Client      │      Backend Research API     │
│  (React 19, TypeScript,     │  (FastAPI, Uvicorn, Python,   │
│   Vite, Tailwind CSS 4,     │   scikit-learn, pandas,       │
│   Recharts)                 │   GroupKFold Random Forest)   │
└─────────────────────────────┴───────────────────────────────┘
```

1. **Frontend Web Application (`/src`)**: An interactive research dashboard providing query-level visualisations, candidate ranking tables, out-of-fold model performance charts, and product-level analysis views.
2. **Backend API (`/api/server.py`)**: A high-performance FastAPI service providing real-time NDJSON streaming analysis, input validation, feature engineering, and scoring.
3. **Research Framework (`/research_framework`)**: The standalone, reproducible scientific pipeline containing data preprocessing, feature engineering, modeling, statistical evaluation, and automated unit/integration tests.

---

## 2. Research Methodology & Implemented Pipeline

### Implemented Workflow

```
Raw CSV Dataset
      │
      ▼
1. Preprocessing & Quality Checks (Median price imputation, rank continuity checks)
      │
      ▼
2. Observable Feature Engineering (13 features: pricing, text metrics, frequency encodings)
      │
      ▼
3. Expected-Ranking Baseline Modeling (Random Forest with 5-Fold GroupKFold OOF Validation)
      │
      ▼
4. Raw Ranking Deviation (Δ_rank = Observed Rank - Expected Rank)
      │
      ▼
5. Peer-Group Inconsistency Analysis (Standardized Query-Relative Z-Score & Relative Rank Gap)
      │
      ▼
6. Empirical Suspiciousness Scoring (0–100 Continuous Score via Percentile-Based CDF Normalization)
      │
      ▼
7. Threshold Calibration & Candidate Flagging
      │
      ▼
8. Synthetic Evaluation & Sensitivity Analysis (Controlled Rank Displacement Simulations)
      │
      ▼
9. Interactive UI Visualisation & Product Audit Inspection
```

### Proposed Future Work
The following capabilities represent valuable research extensions beyond the current baseline implementation:
- **Localized Feature Attribution (SHAP / TreeExplainer)**: Providing individualized feature attribution breakdowns per product.
- **Dynamic Marketplace Scrapers**: Real-time temporal rank trajectory tracking.

### Methodological Distinction & Boundaries
- The calculated **Suspiciousness Score (0–100)** is an empirical measure of ranking inconsistency relative to observable evidence within a specific query peer group.
- It is **NOT** a probability, confidence interval, or definitive proof of fraudulent manipulation.
- Observed ranking deviations indicate behaviour that is difficult to explain from public marketplace attributes alone; they do not establish causation or prove platform abuse.

---

## 3. Repository Structure

```
RankingManipulationDetector/
├── api/
│   └── server.py                   # Production FastAPI backend application
├── dist/                           # Static production build output (generated)
├── public/
│   ├── _redirects                  # Netlify SPA routing rewrite rule
│   ├── favicon.svg                 # Application favicon
│   ├── Hero-1.png                  # Landing page hero asset
│   ├── logo.png                    # FlagRank branding logo
│   ├── research_data.json          # Bundled sample research dataset (1,112 products)
│   └── research_metadata.json      # Bundled baseline evaluation metadata
├── research_framework/
│   ├── data/                       # Experimental raw and processed research datasets
│   │   ├── raw/                    # Primary evaluation dataset (amazon_search_dataset.csv)
│   │   └── processed/              # Processed datasets, OOF predictions, and scores
│   ├── reports/                    # Methodological specifications and evaluation reports
│   ├── src/
│   │   ├── analysis/               # Scoring, peer group analysis, and synthetic evaluation
│   │   ├── config/                 # Pipeline settings and hyperparameter configs
│   │   ├── features/               # Feature schema and signal extraction
│   │   ├── models/                 # Random Forest GroupKFold expected-rank baseline
│   │   └── preprocessing/          # Data cleaning and validation pipeline
│   ├── tests/                      # 33 automated pytest test cases (unit and integration)
│   ├── main.py                     # CLI pipeline runner
│   └── requirements.txt            # Python dependencies for research framework
├── src/                            # Frontend source code
│   ├── components/layout/          # Navigation bar and page shell
│   ├── lib/
│   │   ├── api.ts / config.ts      # Configurable API client and endpoint resolver
│   │   └── useResearchData.tsx     # Context hook for state management
│   ├── pages/
│   │   ├── Dashboard.tsx           # Dataset upload, metric cards, candidate table
│   │   ├── Landing.tsx             # Research overview and methodology stages
│   │   ├── ProductAnalysis.tsx     # Product audit view with peer scatter plots
│   │   ├── RankingAnalysis.tsx     # Query-level distribution charts and filters
│   │   └── ResearchEvaluation.tsx  # OOF metrics, robustness checks, synthetic evaluation
│   ├── App.tsx                     # React Router 7 configuration
│   ├── index.css                   # Tailwind CSS 4 theme and font definitions
│   └── main.tsx                    # React application entry point
├── .env.example                    # Template for environment configuration
├── .gitignore                      # Git exclusion rules
├── Dockerfile                      # Production Docker container definition for backend
├── package.json                    # Node.js dependencies and build scripts
├── requirements.txt                # Unified production Python dependencies
├── vercel.json                     # Vercel SPA routing rewrite configuration
└── vite.config.ts                  # Vite build configuration
```

---

## 4. Prerequisites

- **Node.js**: `v18.0.0` or higher (`v20+` recommended)
- **npm**: `v9.0.0` or higher
- **Python**: `3.10`, `3.11`, or `3.12`
- **pip**: Latest version recommended

---

## 5. Local Setup & Execution

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/RankingManipulationDetector.git
cd RankingManipulationDetector
```

### Step 2: Backend Setup
Create a virtual environment and install the required Python packages:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Start the backend development server:
```bash
python api/server.py
# Or with uvicorn directly:
uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload
```
The API is now accessible at `http://127.0.0.1:8000`. You can verify health by visiting `http://127.0.0.1:8000/api/health`.

### Step 3: Frontend Setup
In a new terminal window:

```bash
# Install frontend dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 6. Environment Variables

Copy `.env.example` to `.env` to configure local or deployment options:

```bash
cp .env.example .env
```

| Variable | Target | Default | Description |
|---|---|---|---|
| `HOST` | Backend | `0.0.0.0` | Network interface to bind the FastAPI server. |
| `PORT` | Backend | `8000` | Port for the backend server. |
| `CORS_ORIGINS` | Backend | `*` | Comma-separated list of allowed CORS origins (e.g. `https://my-frontend.vercel.app`). |
| `MAX_UPLOAD_SIZE_MB` | Backend | `50` | Maximum allowed dataset upload size in megabytes. |
| `VITE_API_BASE_URL` | Frontend | `http://127.0.0.1:8000` (dev) / `""` (prod) | Full URL of the backend API (e.g. `https://api.flagrank.com`). In production, leave blank if proxying same-origin. |

---

## 7. Production Deployment Guide

### Option A: Decoupled Deployment (Recommended)

#### 1. Backend (e.g. Render, Railway, Fly.io, AWS App Runner)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn api.server:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `PORT`: Set automatically by platform or `8000`
  - `CORS_ORIGINS`: Set to your deployed frontend domain (e.g., `https://flagrank.vercel.app`)

#### 2. Frontend (e.g. Vercel, Netlify, Cloudflare Pages)
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_BASE_URL`: URL of your deployed backend (e.g. `https://flagrank-backend.onrender.com`)
- **SPA Routing**:
  - Netlify uses the included `public/_redirects`.
  - Vercel uses the included `vercel.json`.

---

### Option B: Docker Container Deployment

Build and run the backend container:

```bash
# Build Docker image
docker build -t flagrank-api .

# Run container
docker run -d -p 8000:8000 --name flagrank-api flagrank-api
```

Test health:
```bash
curl http://localhost:8000/api/health
```

---

### Option C: Single Server / VPS with Nginx

When hosting both frontend and backend on a Linux VM (Ubuntu/Debian):

1. **Build frontend**:
   ```bash
   npm run build
   # Copy dist contents to /var/www/flagrank
   ```
2. **Run backend with systemd or supervisord**:
   ```bash
   uvicorn api.server:app --host 127.0.0.1 --port 8000
   ```
3. **Nginx Configuration**:
   ```nginx
   server {
       listen 80;
       server_name flagrank.example.com;

       root /var/www/flagrank;
       index index.html;

       # Frontend SPA routing
       location / {
           try_files $uri $uri/ /index.html;
       }

       # Backend API reverse proxy
       location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_read_timeout 300s;
           client_max_body_size 50M;
       }
   }
   ```
   *In this configuration, no `VITE_API_BASE_URL` is needed because the frontend and backend share the same origin.*

---

## 8. Verification & Testing

### Backend Unit & Integration Tests (33 Tests)
Run the automated pytest suite:
```bash
python -m pytest research_framework/tests
```
All 33 tests cover:
- Data preprocessor validation and imputation
- Feature extraction and signal leak safeguards
- GroupKFold Random Forest expected-rank model training
- Peer-group z-score and percentile gap calculation
- Suspiciousness score clipping and normalization
- Synthetic perturbation evaluation simulation
- FastAPI endpoint health check, validation rejections, and NDJSON streaming

### Frontend Lint and Build Verification
```bash
# Linting
npm run lint

# Production compilation
npm run build
```

### System Verification & Test Cases (TC01 – TC10)
All 10 core end-to-end and algorithmic test cases have been executed against the actual FlagRank application and raw dataset with concrete verification:
- Full execution details, quantitative metrics, and audit evidence are documented in [Test Cases Execution Report](research_framework/reports/test_cases_execution_report.md).
- Automated end-to-end browser verification can be executed via:
```bash
python research_framework/tests/verify_frontend_e2e.py
```

---

## 9. Known Limitations & Troubleshooting

1. **Minimum Query Constraint**:
   - The Random Forest expected-ranking model requires at least **5 distinct search queries** in the uploaded CSV to perform 5-fold cross-validation. Uploads with fewer than 5 queries will be rejected with a descriptive validation error message.
2. **Required CSV Columns**:
   - Uploaded datasets must include: `query`, `amazon_rank`, `price`, `original_price`, `rating`, `total_reviews`, `brand`, `product_type`, `color`, `title`, `description`, `discounted`, `savings_percent`, and `sponsored`.
   - If `asin` is missing, synthetic unique identifiers (`ASIN_0`, `ASIN_1`, ...) are automatically created.
3. **Direct URL Refreshes**:
   - Because the frontend is a client-side Single Page Application (SPA), web servers must be configured to fall back to `/index.html` on 404 (handled automatically by `_redirects` for Netlify, `vercel.json` for Vercel, and `try_files` for Nginx).
