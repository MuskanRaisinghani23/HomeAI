from fastapi import FastAPI
from routes import preferenceRoute, listingRoutes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(preferenceRoute.router, prefix="/api/preference", tags=["preference"])
app.include_router(listingRoutes.router, prefix="/api/listing", tags=["listing"])\




