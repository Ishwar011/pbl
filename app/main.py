from fastapi import FastAPI
from app.database.db import engine
from app.database.models import Base
from app.routes import case_routes, narrative_routes, auth_routes  # ✅ ADD THIS
from app.services.rag_service import add_regulations

# Create FastAPI app
app = FastAPI(title="SAR Narrative Generator")

# Create database tables
Base.metadata.create_all(bind=engine)

# ==========================================================
# 🚀 Initialize Regulations Once at Startup
# ==========================================================
@app.on_event("startup")
def startup_event():
    add_regulations()

# ==========================================================
# Include Routers
# ==========================================================
app.include_router(auth_routes.router)        # ✅ ADD THIS
app.include_router(case_routes.router)
app.include_router(narrative_routes.router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "SAR AI System Running"}

# Trigger Reload
