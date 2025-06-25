from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Depends, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from datetime import timedelta
from app.models.user import User
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from app.helpers.auth_helpers import get_password_hash, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db 
from app.schemas.user import RegisterRequest, UserLogin, UserResponse,Token
from ..helpers.document_helpers import replace_placeholders, convert_docx_to_pdf
from ..helpers.calculation_helpers import calculate_derived_fields
from ..helpers.file_helpers import save_and_generate_pdf

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/user-register")
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email already registered"
        })

    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/login", status_code=303)


@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):

            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Invalid email or password"
            })

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

        return templates.TemplateResponse("upload.html", {
            "request": request,
            "token": access_token
        })

    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"Unexpected error: {str(e)}"
        })


@router.post("/generate-payslips/", response_class=HTMLResponse)
async def generate_payslips(
    request: Request,
    csv_file: UploadFile = File(...),
    token: str = Form(...)  
):
    try:
        current_user = verify_token(token)  
        status_messages = await save_and_generate_pdf(csv_file)

        if not status_messages:
            raise HTTPException(status_code=400, detail="No payslips generated")

        return templates.TemplateResponse("status_report.html", {
            "request": request,
            "status_messages": status_messages
        })

    except Exception as e:
        return templates.TemplateResponse("status_report.html", {
            "request": request,
            "status_messages": [f"Error processing file: {str(e)}"]
        })


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    return response