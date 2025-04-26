from fastapi import FastAPI
from routes import preferenceRoute, listingRoutes, mapRoutes, authRoutes
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
app.include_router(listingRoutes.router, prefix="/api/listing", tags=["listing"])
app.include_router(mapRoutes.router, prefix="/api/map", tags=["map"])
app.include_router(authRoutes.router, prefix="/auth", tags=["auth"])
