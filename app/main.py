from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import payslip_generator
from app.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/generated_payslips", StaticFiles(directory="generated_payslips"), name="generated_payslips")


app.include_router(payslip_generator.router)

