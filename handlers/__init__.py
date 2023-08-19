from aiogram import Router


def setup_routers() -> Router:
    from .users import start, echo
    from .errors import error_handler
    
    router = Router()
    router.include_router(start.router)
    router.include_router(echo.router)
    router.include_router(error_handler.router)
    
    return router
