import json
import random
import httpx
import time
import requests

with open('input/config.json') as config_file:
    config = json.load(config_file)

with open("input/proxies.txt") as f:
    proxies = f.read().splitlines()

api_key = config["captcha"]["apikey"]
url = "https://discord.com/channels/@me"
sitekey = "a9b5fb07-92ff-493f-86fe-352a2803b3df"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'

if not config["captcha"]["proxyless"]:
    proxy = random.choice(proxies).strip()
    proxies = f"http://{proxy}"

else:
    proxies = None

class Solver:
    def update_proxy(self):
        global proxies
        if not config["captcha"]["proxyless"]:
            proxy = random.choice(proxies).strip()
            proxies = {f"http://{proxy}"}
            return proxies
        
    def csolver(self, rqdata=str):
        endpoint = "https://api.csolver.xyz/solve"
        headers = {'API-Key': "71144850f4fb4cc55fc0ee6935badddf"}

        payload = {
            'sitekey': sitekey,
            'site': "discord.com",
            'rqdata': rqdata
        }

        start = time.time()
        response = httpx.post(endpoint, headers=headers, json=payload)
        end = time.time()
        elapsed = end - start
        e = round(elapsed, 2)
        if response.status_code == 200:
            data = response.json()
            solution = data.get('solution')
            return solution
        else:
            return None

    def razorcap(self, rqdata, timeout=120):
        payload = {
            'key': api_key,
            'type': 'hcaptcha_enterprise',
            'data': {
                'sitekey': sitekey,
                'siteurl': "discord.com",
                'proxy': proxies,
                'rqdata': rqdata
            }
        }

        try:
            # Create the captcha solving task
            response = httpx.post('https://api.razorcap.xyz/create_task', json=payload, timeout=10)
            if response.status_code != 200 or "task_id" not in response.json():
                print("Failed to create task.")
                return None
            
            task_id = response.json()["task_id"]
            start_time = time.time()

            # Poll for the solution
            while time.time() - start_time < timeout:
                result = httpx.get(f'https://api.razorcap.xyz/get_result/{task_id}', timeout=10).json()
                if result["status"] == "solved":
                    return result.get("response_key")
                elif result["status"] == "solving":
                    time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")

        print("Captcha solving failed or timed out.")
        return None

        

    def procap(self):
        headers = {
            'accept': 'application/json',
            'apikey': api_key,
            'Content-Type': 'application/json',
        }

        self.update_proxy()
        json_data = {
            'url': url,
            'sitekey': sitekey,
            'userAgent': user_agent,
        }

        response = httpx.post('https://api.procap.wtf/createTask', headers=headers, json=json_data)
        task_id = response.json()["ID"]

        headers2 = {
            'accept': 'application/json',
        }

        while True:
            try:
                response2 = httpx.get(f'https://api.procap.wtf/checkTask/{task_id}', headers=headers2)
                data = response2.json()
                if data["Message"] == "solved":
                    key = data['Results']['Pass']
                    return key
                elif data["Message"] == "failed":
                    return None
            except:
                return None
            time.sleep(1)
            
    def hcoptcha(self, rqdata=str):
        payload = {
            "task_type": "hcaptchaEnterprise",
            "api_key": api_key,
            "data": {
                "sitekey": sitekey,
                "url": url,
                "userAgent": user_agent,
                "proxy": self.update_proxy(),
                "rqdata": rqdata
            }
        }
        r = httpx.post("https://api.hcoptcha.com/api/createTask", json=payload)
        try:
            data = r.json()
            if data.get("task_id"):
                task_id = data.get("task_id")
            else:
                return None
        except:
            return None

        while True:
            payload2 = {
                "api_key": api_key,
                "task_id": task_id
            }
            r2 = httpx.post("https://api.hcoptcha.com/api/getTaskData", json=payload2)
            try:
                data2 = r2.json()
                if data2["task"]["state"] == "completed":
                    key2 = data2["task"]["captcha_key"]
                    return key2
                elif data2["task"]["state"] == "error":
                    return None
            except:
                return None
            time.sleep(1)

    def capsolver(self):
        payload = {
            "clientKey": api_key,
            "appid": "D802050C-BD9A-49D7-A73C-CE473E22B569",
            "task": {
                "type": "HCaptchaTaskProxyless",
                "websiteURL": url,
                "websiteKey": sitekey,
                "isInvisible": True,
                "userAgent": user_agent,
                "AppId": "D802050C-BD9A-49D7-A73C-CE473E22B569"
            }
        }

        r = httpx.post("https://api.capsolver.com/createTask", json=payload)
        try:
            data = r.json()
            if data.get("task_id"):
                task_id = data.get("task_id")
            else:
                return None
        except:
            return None

        while True:
            r2 = httpx.post("https://api.capsolver.com/getTaskResult", json={"clientKey": api_key, "taskId": task_id})
            try:
                data2 = r2.json()
                if "ready" in r2.text:
                    key2 = data2["solution"]["gRecaptchaResponse"]
                    return key2
                elif "processing" in r2.text:
                    time.sleep(1)
            except:
                return None
            time.sleep(1)

    def capmonster(self):
        payload = {
            "clientKey": api_key,
            "task": {
                "type": "HCaptchaTaskProxyless",
                "websiteURL": url,
                "websiteKey": sitekey,
                "userAgent": user_agent
            }
        }

        self.update_proxy()

        r = httpx.post("https://api.capmonster.cloud/createTask", json=payload)
        try:
            data = r.json()
            if data.get("taskId"):
                task_id = data.get("taskId")
            else:
                return None
        except:
            return None

        while True:
            r2 = httpx.post("https://api.capmonster.cloud/getTaskResult", json={"clientKey": api_key, "taskId": task_id})
            try:
                data2 = r2.json()
                if "ready" in data2["status"]:
                    key2 = data2["solution"]["gRecaptchaResponse"]
                    return key2
                elif "processing" in data2["status"]:
                    time.sleep(1)
                else:
                    return None
            except:
                return None
            time.sleep(1)