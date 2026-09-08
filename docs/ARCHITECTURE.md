# System Architecture

CodeGate is a multi-service platform designed to intercept GitHub Pull Requests, analyze them asynchronously, store the results persistently, and display them in a modern web dashboard.

## High-Level Architecture Diagram

```mermaid
flowchart TD
    %% External Systems
    GH[GitHub PR Webhook]
    AI[AI Provider\nGroq/OpenAI]
    
    %% User Interfaces
    Browser[Web Browser]
    Launcher[CodeGateLauncher.exe]
    
    %% Frontend Layer
    subgraph Frontend
        React[React / Vite SPA]
    end
    
    %% Backend Layer
    subgraph Backend
        FastAPI[FastAPI Server\nPort 8000]
        API[REST API Routers]
        Auth[OAuth Handlers]
        Webhook[Webhook Handlers]
        
        FastAPI --- API
        FastAPI --- Auth
        FastAPI --- Webhook
    end
    
    %% Async Layer
    subgraph Async Pipeline
        Redis[(Redis Broker\nPort 6379)]
        Celery[Celery Worker]
        
        %% Engines
        Engine_AI[AI Review Engine\nPR-Agent Core]
        Engine_SA[Static Analysis Engine\nRuff, Bandit]
        Engine_Test[Test Engine\nDockerTestExecutor]
        Engine_Score[Scoring Engine\nQuality & Risk]
        
        Celery --- Engine_AI
        Celery --- Engine_SA
        Celery --- Engine_Test
        Celery --- Engine_Score
    end
    
    %% Storage Layer
    subgraph Storage
        Postgres[(PostgreSQL 16\nPort 5432)]
    end
    
    %% Test Environment
    subgraph Isolation
        TestContainer[Sandbox Test Container]
    end
    
    %% Connections
    Launcher -.->|Manages| Frontend
    Launcher -.->|Manages| Backend
    Launcher -.->|Manages| Async Pipeline
    Launcher -.->|Manages| Storage
    
    Browser -->|HTTP/REST| React
    React -->|HTTP/REST| API
    
    GH -->|HTTP POST| Webhook
    Webhook -->|Enqueue| Redis
    Redis -->|Dequeue| Celery
    
    API -->|Read/Write| Postgres
    Celery -->|Read/Write| Postgres
    
    Engine_AI -->|API Calls| AI
    Engine_Test -->|Docker API| TestContainer
    Engine_Score -->|Publish Check| GH
```

## Component Details

### 1. Frontend (React / Vite)
- Serves the User Interface. 
- In Product Mode, this is a statically built application served by an Nginx container.
- Connects to the backend via standard REST APIs.

### 2. Backend (FastAPI)
- Handles user authentication via GitHub OAuth.
- Provides CRUD endpoints for Workspaces, Repositories, and Dashboard analytics.
- Receives GitHub App webhooks. It quickly acknowledges the webhook and offloads the actual processing to Redis.

### 3. Async Pipeline (Redis + Celery)
- **Redis**: Acts as the message broker.
- **Celery Worker**: Picks up `AnalysisJob` tasks. It orchestrates the complex, time-consuming analysis pipeline without blocking the web server.

### 4. Engines
- **AI Review Engine**: Wraps the upstream PR-Agent capabilities using `LiteLLM` to generate code suggestions, summaries, and identify bugs.
- **Static Analysis Engine**: Runs `ruff`, `bandit`, and `radon` against the changed files.
- **Test Engine**: Spawns a sibling Docker container (`DockerTestExecutor`) to run the user's test suite and parse coverage reports safely.
- **Scoring Engine**: Normalizes the outputs of all the above engines into a `Quality Score` (0-100) and `Risk Score`, then evaluates them against the workspace's Merge Policy.

### 5. Storage (PostgreSQL 16)
- Stores all relational data: Users, Workspaces, Repositories, Pull Requests, Analysis Runs, and individual findings (AI issues, static analysis flaws).
- Managed entirely via SQLAlchemy ORM and Alembic migrations.
