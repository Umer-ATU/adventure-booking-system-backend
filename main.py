from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import bookings, admin

app = FastAPI(title="Adventure Park Booking System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router)
app.include_router(admin.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
