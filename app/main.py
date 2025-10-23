
from fastapi import FastAPI
from app.lifespan import lifespan
from app.middleware import register_middleware
from app.routes import login,signup,current_user,admin
from app.internal.error import register_all_errors


version = "v1"

app = FastAPI(
    lifespan=lifespan,
    root_path="/",
    version=version,
    title="PSTU_CSE_CRICKET"
    ) 

register_all_errors(app)
register_middleware(app)


# ============== ALL THE ENDPOINT =================
app.include_router(signup.router,prefix=f"/api/{version}")
app.include_router(login.router,prefix=f"/api/{version}")
app.include_router(current_user.router,prefix=f"/api/{version}")
app.include_router(admin.router,prefix=f"/api/{version}/admin")


@app.get("/")
async def test_log():
    return "everything is working fine :)"
    