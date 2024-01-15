# multiprocess-undetected-chromedriver-proxy-bot
Multiprocessor bot for anonymously launching a web page through a proxy

Python version = 3.11 

pip install undetected-chromedriver, loguru, Faker 

!important!
fix in undetected - patcher.py ->
import secrets prefix = f"undetected_{secrets.token_hex(8)}"

Since the browser starts in --headless mode, the bot takes screenshots (in '/screenshots' ) confirming its actions