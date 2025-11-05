<br>

# CPL: CSE PREMIER LEAGUE (Patuakhali Science And Technology University)

<br>

```md
# Author: Nobarun_19
#  _   _  ____   ____    _    ____  _   _  _   _  _  ____  _  _  _ 
# | \ | |/ __ \ / __ \  / \  |  _ \| \ | || \ | |/ ||  _ \| || || |
# |  \| | |  | | |  | |/ _ \ | |_) |  \| ||  \| ' / | |_) | || || |
# | |\  | |  | | |  | / ___ \|  _ <| |\  || |\   <| |  _ <| ||_||_|
# |_| \_|\____/ \____/_/   \_\_| \_\_| \_||_| \_|\_\_| \_\(_)(_)(_)
#                            _  ___ 
#                           (_)/ _ \
#                            _| (_) |
#                           (_)\___/

```

### Backend:
- FASTAPI (Python)
- DATABASE (POSTGRESQL)

### Dot env file format:
```md
#====== database postgressql ======
DB_ROLE_NAME=""
DB_PASSWORD=""
DB_HOST=""
DATABASE=""
DB_PORT=""


#====== fastapi =========
SECRET_KEY=""
ALGORITHM=""
ACCESS_TOKEN_EXPIRE_MINUTES=""
SCHEMES=""

#====== Email Configuration ======
MAIL_USERNAME=""
MAIL_PASSWORD=""
MAIL_FROM=""
MAIL_PORT=""
MAIL_SERVER=""
MAIL_FROM_NAME=""

```

### Citeria For Uploading Imgae Background Image
- **File Format:** 'png', 'jpg', 'jpeg'
- **File Name:** ["all_rounder","batsman","bowler","wk_batsman"]
    - **Example:** [bowler.jpg or bowler.png or bowler.jpeg]
    

```python 
python -m venv venv  
.\venv\Scripts\activate
pip install --upgrade pip 
pip install -r requirements.txt
uvicorn app.main:app --host 192.168.0.117  --port 8000 --reload
```
