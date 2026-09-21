from fastapi import APIRouter
from app.api.v1 import auth, users, products, counts, adjustments, sessions, sync, reports, locations, imports, exports, roles, inventory_events, anomalies, risk, forecast, recommendations, demo_pos

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(counts.router, prefix="/counts", tags=["Counts"])
api_router.include_router(adjustments.router, prefix="/adjustments", tags=["Adjustments"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(sync.router, prefix="/sync", tags=["Sync"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(locations.router, prefix="/locations", tags=["Locations"])
api_router.include_router(imports.router, prefix="/imports", tags=["Imports"])
api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])
api_router.include_router(inventory_events.router, prefix="/inventory-events", tags=["Inventory Events"])
api_router.include_router(anomalies.router, prefix="/anomalies", tags=["Anomaly Detection"])
api_router.include_router(risk.router, prefix="/risk", tags=["Inventory Risk"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecasting"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(demo_pos.router, prefix="/demo-pos", tags=["Demo POS"])
