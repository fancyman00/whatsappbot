import uvicorn

from app.main import get_app



if __name__ == "__main__":
    uvicorn.run(app=get_app())
