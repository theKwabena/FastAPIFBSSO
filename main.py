import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_sso.sso.facebook import FacebookSSO

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Minimal User Interface using Jinja
@app.get("/login/", response_class=HTMLResponse)
async def read_item(request: Request, ):
    return templates.TemplateResponse("facebook-login.html", {"request": request, })


# SSO Config
FACEBOOK_CLIENT_ID = ''
FACEBOOK_CLIENT_SECRET = ''

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
facebook_sso = FacebookSSO(
    FACEBOOK_CLIENT_ID,
    FACEBOOK_CLIENT_SECRET,
    "http://localhost:8000/v1/facebook/callback",
    allow_insecure_http=True
)


@app.get("/v1/facebook/login", tags=['Facebook SSO'])
async def facebook_login():
    return await facebook_sso.get_login_redirect()


@app.get("/v1/facebook/callback", tags=['Facebook SSO'])
async def facebook_callback(request: Request):
    """Process login response from Facebook and return user info"""

    with facebook_sso:
        try:
            user = await facebook_sso.verify_and_process(request)

            # Remaining Logic, i.e. checks with db to see if user exists, create user etc

            return user

        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"{e}")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")
