from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx

app = FastAPI(title="Garena Guest Token API")

class LoginRequest(BaseModel):
    uid: str
    password: str

async def fetch_access_token(uid: str, password: str):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                resp_json = response.json()
                open_id = resp_json.get("open_id")
                access_token = resp_json.get("access_token")
                platform = resp_json.get("platform", 4)
                if open_id and access_token:
                    return {
                        "status": "success",
                        "open_id": open_id,
                        "access_token": access_token,
                        "platform": platform
                    }
                return {"status": "error", "message": "Tokens not found in response", "raw": resp_json}
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limited by server. Try later.")
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")

# Vercel द्वारा भेजे जाने वाले सभी संभावित पाथ्स को हैंडल करने के लिए:
@app.post("/get-token")
@app.post("/api/get-token")
@app.post("/api/index/get-token")
async def get_token_endpoint(req: LoginRequest):
    return await fetch_access_token(req.uid, req.password)

@app.get("/")
@app.get("/api")
def root():
    return {"status": "online"}
