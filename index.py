import requests, json, random, time, msvcrt, ctypes, threading
import concurrent.futures
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List
from curl_cffi import requests as request
from data.solver import Solver
from data.logger import NovaLogger
from colorama import init, Fore, Style

banner = f"""
{Fore.CYAN}
                        █████▒██▓ ██▓     ██▓   ▓██   ██▓
                        ▓██   ▒▓██▒▓██▒    ▓██▒    ▒██  ██▒
                        ▒████ ░▒██▒▒██░    ▒██░     ▒██ ██░
                        ░▓█▒  ░░██░▒██░    ▒██░     ░ ▐██▓░
                        ░▒█░   ░██░░██████▒░██████▒ ░ ██▒▓░
                        ▒ ░   ░▓  ░ ▒░▓  ░░ ▒░▓  ░  ██▒▒▒ 
                        ░      ▒ ░░ ░ ▒  ░░ ░ ▒  ░▓██ ░▒░ 
                        ░ ░    ▒ ░  ░ ░     ░ ░   ▒ ▒ ░░  
                                ░      ░  ░    ░  ░░ ░     
                                                ░ ░     

                        {Fore.LIGHTCYAN_EX}https://discord.gg/api{Style.RESET_ALL}
"""

chrome_version = 133
sec_ch_ua = f'"Google Chrome";v="{chrome_version}", "Chromium";v="{chrome_version}", "Not;A=Brand";v="8"' # chrome_131
user_agent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36'

@dataclass
class JoinerConfig:
    delay: int
    proxyless: bool
    threads: int
    max_joins: int
    captcha: Dict
    # license_key: str 

@dataclass
class JoinerStats:
    total: int = 0
    joined: int = 0
    captcha: int = 0
    captcha_solved: int = 0
    failed: int = 0
    locked: int = 0
    invalid: int = 0
    current: int = 0

class TokenManager:
    def __init__(self, tokens_file: str):
        self.tokens_file = Path(tokens_file)
        self.tokens = self._load_tokens()
        self.token_joins: Dict[str, int] = {}
    
    def _load_tokens(self) -> List[str]:
        return list(set(self.tokens_file.read_text().splitlines()))
    
    def remove_token(self, token: str) -> None:
        self.tokens = [t for t in self.tokens if t.strip() != token]
        self.tokens_file.write_text('\n'.join(self.tokens) + '\n')

    def increment_joins(self, token: str) -> int:
        self.token_joins[token] = self.token_joins.get(token, 0) + 1
        return self.token_joins[token]

class DiscordJoiner:
    def __init__(self, thread_number: int, config: JoinerConfig, stats: JoinerStats):
        self.thread_number = thread_number
        self.config = config
        self.stats = stats
        self.session, self.client = self._get_session()
        self._setup_session()

    def _get_session(self):
        try:
            return request.Session(impersonate="chrome"), request.Session(impersonate="chrome")
        except Exception:
            return self._get_session()

    def _setup_session(self):
        if not self.config.proxyless:
            proxies = Path('input/proxies.txt').read_text().splitlines()
            self.proxy = f"http://{random.choice(proxies)}".replace(
                'sessionid', str(random.randint(1327390889, 1399999999))
            )
            self.session.proxies = {"http": self.proxy, "https": self.proxy}

        self.session.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'priority': 'u=1, i',
            'referer': 'https://discord.com/channels/@me/1338000752110600309',
            "sec-ch-ua": sec_ch_ua,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Asia/Calcutta',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZSwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTMzLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM2Njk1NSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        }
        
        self.client.headers = self.session.headers

    def _get_cookies(self):
        response = requests.get("https://discord.com/channels/@me")
        cookies = {k: v for k, v in response.cookies.items() if k in ('__dcfduid', '__sdcfduid', '__cfruid', '_cfuvid')}
        return '; '.join(f"{k}={v}" for k, v in cookies.items())

    def _handle_captcha(self, rqdata: str, rqtoken: str) -> Optional[str]:
        solver = Solver()
        solver_map = {
            "razorcap": lambda: solver.razorcap(rqdata=rqdata),
            "aisolver": lambda: solver.aisolver2(proxy=self.proxy, rqdata=rqdata),
            "hcoptcha": lambda: solver.hcoptcha(rqdata),
            "csolver": lambda: solver.csolver(rqdata),
            "capmonster": lambda: solver.capmonster(rqdata)
        }
        if solver_func := solver_map.get(self.config.captcha["service"]):
            solution = solver_func()
            if solution:
                self.stats.captcha_solved += 1
                NovaLogger.win("Captcha Solved Successfully")
            return solution
        return None

    def _append_to_file(self, filename: str, content: str):
        with open(f"output/{filename}", "a") as f:
            f.write(f"{content}\n")

    def _handle_response(self, response, token: str, masked_token: str) -> None:
        self.stats.current += 1

        if response.status_code == 429:
            NovaLogger.fail("Rate Limited", token=masked_token, thread=self.thread_number)
            return

        if response.status_code == 200:
            NovaLogger.win("Successfully Joined Server", token=masked_token, thread=self.thread_number)
            self._append_to_file("joined.txt", token)
            self.stats.joined += 1
            return

        if response.status_code == 401:
            NovaLogger.fail("Invalid Token", token=masked_token, thread=self.thread_number)
            self._append_to_file("invalid.txt", token)
            token_manager.remove_token(token)
            self.stats.invalid += 1
            return

        if response.status_code == 403:
            NovaLogger.fail("Locked Token", token=masked_token, thread=self.thread_number)
            self._append_to_file("locked.txt", token)
            token_manager.remove_token(token)
            self.stats.locked += 1
            return

        if "Unknown Message" in response.text:
            NovaLogger.fail("Failed Due To Token Issue", token=masked_token, error="Unknown Message", thread=self.thread_number)
            self._append_to_file("failed_token.txt", token)
            self.stats.failed += 1
            return

        if "captcha_key" in response.text:
            NovaLogger.fail("Failed Due To Solver Issue", token=masked_token, error=response.json()['captcha_key'], thread=self.thread_number)
            self._append_to_file("failed_captcha.txt", token)
            self.stats.failed += 1
            return

        NovaLogger.fail(f"Failed To Join Server", token=masked_token, error=response.text, thread=self.thread_number)
        self._append_to_file("failed.txt", token)
        self.stats.failed += 1

    def join_server(self, token: str, invite: str) -> None:
        try:
            token_only = token.split(":")[-1]
            masked_token = f"{token_only.split('.')[0]}.*****"
            
            self.session.headers["authorization"] = token_only
            response = self.session.post(f"https://discord.com/api/v9/invites/{invite}", json={})

            if "captcha_sitekey" in response.text and self.config.captcha["solve_captcha"]:
                NovaLogger.alert("Captcha Detected", token=masked_token)
                self._append_to_file("captcha.txt", token)
                self.stats.captcha += 1

                solution = self._handle_captcha(
                    response.json()['captcha_rqdata'],
                    response.json()['captcha_rqtoken']
                )

                if solution:
                    self.client.headers.update({
                        "authorization": token_only,
                        "x-captcha-key": solution,
                        "x-captcha-rqtoken": response.json()['captcha_rqtoken']
                    })
                    response = self.client.post(
                        f"https://discord.com/api/v9/invites/{invite}",
                        json={},
                        proxy=None if self.config.proxyless else self.proxy
                    )

            self._handle_response(response, token, masked_token)

        except Exception as e:
            NovaLogger.fail("Error", error=e, thread=self.thread_number)
        finally:
            self.session.close()
            self.client.close()
            
            if self.config.delay > 0:
                NovaLogger.note(f"Sleeping for {self.config.delay} seconds")
                time.sleep(self.config.delay)

def update_title(stats: JoinerStats, done: threading.Event, total_invites: int):
    """Updates the console title with current joining statistics."""
    while not done.is_set():
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(
                f"Filly | "
                f"Total: {total_invites} | "
                f"Joined: {stats.joined} | "
                f"Failed: {stats.failed} | "
                f"Captcha: {stats.captcha} ({stats.captcha_solved} solved) | "
                f"Invalid: {stats.invalid} | "
                f"Locked: {stats.locked}"
            )
            time.sleep(0.1)
        except Exception as e:
            NovaLogger.fail(f"Title Update Error: {str(e)}")
            break
def main():
    init()
    try:
        config = JoinerConfig(**json.loads(Path('input/config.json').read_text()))
        stats = JoinerStats()
        done = threading.Event()

        invites = list(set(Path('input/invites.txt').read_text().splitlines()))
        max_joins = min(config.max_joins, len(invites))
        max_threads = min(len(token_manager.tokens), config.threads)

        print(banner)
        
        # Start title update thread
        title_thread = threading.Thread(
            target=update_title, 
            args=(stats, done, len(invites))
        )
        title_thread.daemon = True  # Make thread daemon so it exits with main program
        title_thread.start()

        start_time = time.time()

        try:
            for invite in invites[:max_joins]:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                    for tokenz, token in enumerate(token_manager.tokens):
                        joins = token_manager.increment_joins(token)
                        
                        if joins >= config.max_joins:
                            with open("output/filled_tokens.txt", "a") as f:
                                f.write(f"{token}\n")
                            continue

                        if stats.invalid > 0 or stats.locked > 0:
                            break

                        thread_number = (tokenz % max_threads) + 1
                        joiner = DiscordJoiner(thread_number, config, stats)
                        executor.submit(joiner.join_server, token.strip(), invite)

        finally:
            # Signal title thread to stop and wait for it
            done.set()
            title_thread.join(timeout=1.0)  # Add timeout to prevent hanging
            
            # Calculate and display statistics
            elapsed = time.time() - start_time
            minutes, seconds = divmod(int(elapsed), 60)
            
            sep_line = "=" * 50
            print(f"\n{sep_line}")
            print(f"{Fore.CYAN}Final Statistics:{Style.RESET_ALL}")
            print(f"Joined {stats.current} Tokens in {minutes} Minutes and {seconds} Seconds")
            print("\nSummary:")
            print(f"- Total Processed: {Fore.CYAN}{stats.current}{Style.RESET_ALL}")
            print(f"- Successfully Joined: {Fore.GREEN}{stats.joined}{Style.RESET_ALL}")
            print(f"- Captcha Encountered: {Fore.YELLOW}{stats.captcha} {Fore.CYAN}({stats.captcha_solved} solved){Style.RESET_ALL}")
            print(f"- Failed: {Fore.RED}{stats.failed}{Style.RESET_ALL}")
            print(f"- Invalid Tokens: {Fore.RED}{stats.invalid}{Style.RESET_ALL}")
            print(f"- Locked Tokens: {Fore.RED}{stats.locked}{Style.RESET_ALL}")
            print(f"\n{sep_line}")
            
            print(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
            while True:
                if msvcrt.kbhit():
                    if msvcrt.getch() == b'\r':
                        break
                time.sleep(0.1)
            
            print(f"{Fore.CYAN}Exiting in 3 seconds...{Style.RESET_ALL}")
            time.sleep(3)


    except Exception as e:
        print(f"{Fore.RED}Critical Error: {str(e)}{Style.RESET_ALL}")
    finally:
        try:
            NovaLogger.close()
        except:
            pass

if __name__ == "__main__":
    token_manager = TokenManager("input/tokens.txt")
    main()