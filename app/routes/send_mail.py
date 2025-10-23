
from app.config import CONFIG
from fastapi import APIRouter
from app.db.schemas import EmailSchema
from pydantic import SecretStr
from fastapi_mail import FastMail,ConnectionConfig,MessageSchema,MessageType

router = APIRouter(tags=["send email"])


conf = ConnectionConfig(
    MAIL_USERNAME = CONFIG.MAIL_USERNAME, 
    MAIL_PASSWORD = SecretStr(CONFIG.MAIL_PASSWORD),
    MAIL_FROM = CONFIG.MAIL_FROM,
    MAIL_PORT = CONFIG.MAIL_PORT,
    MAIL_SERVER = CONFIG.MAIL_SERVER,
    MAIL_STARTTLS = CONFIG.MAIL_STARTTLS,
    MAIL_SSL_TLS = CONFIG.MAIL_SSL_TLS,
    USE_CREDENTIALS = CONFIG.USE_CREDENTIALS,
    VALIDATE_CERTS = CONFIG.VALIDATE_CERTS
)

mail = FastMail( config=conf)

def create_message(recip:list[str],sub:str,body:str):
    message = MessageSchema(
        recipients=recip,
        subject=sub,
        body=body,
        subtype=MessageType.html
    )
    return message


@router.post("/sendmail")
async def send_mail_endpoint(mails: list[str],sub=None,html=None):
    #emails = mails.emails
    if html is None:
        html = "<h1>HI! HOW ARE YOU FROM PSTU-CSE<h1>"
    if sub is None:
        sub = "WECOME TO CPL(CSE PREMIER LEAGE)"
    message =  create_message(
        recip=mails,
        sub= sub,
        body=html
    )
    await mail.send_message(message)
    return {"message":"Email Send Successfull"}


