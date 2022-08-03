import httpx, threading, requests, time, re, user_agent, base64, json, colorama, random; from anticaptchaofficial.hcaptchaproxyless import *
import os

class Soft:
      JSON = json.load(open('data/config.json', 'r'))
      INVITE_CODE = JSON['inviteCode']
      CAPTCHA_KEY = JSON['captchaKey']

class Discord:
      def __init__(self):
          self.build_number = None 
          self

      def get_invite_data(self, invite_code):
          return httpx.get('https://discord.com/api/v9/invites/%s' % (invite_code)).json()
        
      def get_cookies(self):
          return httpx.get('https://discord.com/register').headers['Set-Cookie']
        
      def get_fingerprint(self):
          return httpx.get('https://discord.com/api/v9/experiments', timeout = 10).json()['fingerprint'] or None
        
      def get_x_track(
          self,
          user_agent_string
      ):
          return base64.b64encode(
                        json.dumps(
                             {
                                 'os'                 : user_agent_string['appCodeName'],
                                 'browser'            : user_agent_string['platform'],
                                 'device'             : "",
                                 'system_locale'      : "en-US",
                                 'browser_user_agent' : "%s" % (user_agent_string['userAgent']),
                                 'browser_version'    : "%s" % (user_agent_string['appVersion'].split(" ")[0]),
                                 'os_version'         : "%s" % (user_agent_string['userAgent'].split("/")[1].split(" ")[0]),
                                 'referrer'           : "",
                                 'referring_domain'   : "",
                                 'referrer_current'   : "",
                                 'referring_domain_current'  : "",
                                 'release_channel'           : "stable",
                                 'client_build_number'       :  9999,
                                 'client_event_source'       :  None
                             }, separators = (',', ':')
                        ).encode()
          ).decode()    
        
      def get_super_properties(
          self,
          user_agent_string
      ):
          return base64.b64encode(
                        json.dumps(
                             {
                                 'os'                 : user_agent_string['appCodeName'],
                                 'browser'            : user_agent_string['platform'],
                                 'device'             : "",
                                 'system_locale'      : "en-US",
                                 'browser_user_agent' : "%s" % (user_agent_string['userAgent']),
                                 'browser_version'    : "%s" % (user_agent_string['appVersion'].split(" ")[0]),
                                 'os_version'         : "%s" % (user_agent_string['userAgent'].split("/")[1].split(" ")[0]),
                                 'referrer'           : "",
                                 'referring_domain'   : "",
                                 'referrer_current'   : "",
                                 'referring_domain_current'  : "",
                                 'release_channel'           : "stable",
                                 'client_build_number'       :  self.build_number,
                                 'client_event_source'       :  None
                             }, separators = (',', ':')
                        ).encode()
          ).decode() 
        
      def get_build_number(self):
          asset = re.compile(r'([a-zA-z0-9]+)\.js', re.I).findall(self.client.get(f'https://discord.com/app', headers={'User-Agent': 'Mozilla/5.0'}).read().decode('utf-8'))[-1]
          fr = self.client.get(f'https://discord.com/assets/{asset}.js', headers={'User-Agent': 'Mozilla/5.0'}).read().decode('utf-8')
          self.build_number = str(re.compile('Build Number: [0-9]+, Version Hash: [A-Za-z0-9]+').findall(fr)[0].replace(' ', '').split(',')[0].split(':')[-1]).replace(' ', '')
        
class Joiner:
      def __init__(self, captcha_key = None):
          self.discord     = Discord()
          self.site_key    = 'a9b5fb07-92ff-493f-86fe-352a2803b3df'
          self.site_url    = 'https://discord.com/'
          self.solver      = hCaptchaProxyless()
          self.solver.set_verbose(1)
          self.user_agent  = user_agent.generate_navigator_js()
          self.cookies     = self.discord.get_cookies()
          self.headers     = {
                           'x-debug-options'    : 'bugReporterEnabled',
                           'x-discord-locale'   : 'en-US',            
                           'sec-ch-ua'          : '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
                           'sec-ch-ua-mobile'   : "?0",
                           'sec-ch-ua-platform' : '"Windows"',
                           'sec-fetch-dest'     : 'empty',
                           'sec-fetch-mode'     : 'cors',
                           'sec-fetch-site'     : 'same-origin"',            
                           'User-Agent'         : self.user_agent['userAgent'],
                           'X-Super-Properties' : self.discord.get_super_properties(self.user_agent),
                           'Cookie'             : '__dcfduid=%s; __sdcfduid=%s;' % (
                                                   self.cookies.split('__dcfduid=')[1].split(';')[0], 
                                                   self.cookies.split('__sdcfduid=')[1].split(';')[0],
                           )
          }

      def join_server(self, token, invite_code, proxy = None):
          self.headers['Authorization'] = f'{token}' 
          self.invite_data              =    self.discord.get_invite_data(invite_code = invite_code)
          self.headers['Referer']       =    'https://discord.com/channels/@me'
          self.headers['Origin']        =    'discord.com/channels/@me'
          self.headers['X-Content-Properties'] = base64.b64encode(
                                                 json.dumps(
                                                      {
                                                         'location_guild_id'     : str(self.invite_data['guild']['id']),
                                                         'location_channel_id'   : str(self.invite_data['channel']['id']),
                                                         'location_channel_type' : str(self.invite_data['channel']['type']),
                                                      }, separators = (',', ':')
                                                 ).encode()
          ).decode()
        
          test_request = requests.post(
                         f'https://discord.com/api/v9/invites/{invite_code}',
                           headers = self.headers,
                           proxies = {
                                   'http'   : 'http://%s' % (proxy),
                                   'https'  : 'http://%s' % (proxy),
                           }
          )

          if 'captcha_key' in test_request.text:
              self.solver.set_key(Soft.CAPTCHA_KEY)
              self.solver.set_website_key(self.site_key)
              self.solver.set_website_url(self.site_url)
              self.solver.set_enterprise_payload(
                   {
                       'rqdata'           : test_request.json()['captcha_rqdata'],
                       'sentry'           : True,
                   }
              )

              response     = self.solver.solve_and_return_solution()

              if response != 0:
                 main_request = requests.post(
                                f'https://discord.com/api/v9/invites/{invite_code}',
                                  headers = self.headers,
                                  json    = {'captcha_key': response, 'captcha_rqtoken': test_request.json()['captcha_rqtoken']},
                                  proxies = {
                                          'http'   : 'http://%s' % (proxy),
                                          'https'  : 'http://%s' % (proxy),
                                  }                
                 )

                 return main_request.json(), 'Solve Success'
              else:
                 if response == 0:
                    return response, 'Solve Failure'
          else:
             return test_request, 'Captcha Undetected'

print (
    f'Soft {colorama.Fore.RED}Joiner{colorama.Fore.RESET} \n',
    f'    [Token Stock: {colorama.Fore.LIGHTRED_EX}%s{colorama.Fore.RESET}]\n' % (len(open('data/tokens.txt', 'r').readlines())),
    f'    [Proxy Stock: {colorama.Fore.LIGHTRED_EX}%s{colorama.Fore.RESET}]\n' % (len(open('data/proxies.txt', 'r').readlines())),
)
input('[ PRESS ENTER TO START ]\n')

if Soft.CAPTCHA_KEY == '':
   exit(print('[SOFT ERROR] | Missing Captcha Key'))
   exit
else:
   if Soft.INVITE_CODE == '':
      exit(print('[SOFT ERROR] | Missing Invite Code'))
      exit

for token in open('data/tokens.txt', 'r').readlines():
    joiner = Joiner(captcha_key = Soft.CAPTCHA_KEY)
    proxy  = random.choice(open('data/proxies.txt', 'r').readlines()).strip()

    print('[SOFT DATA] | Joining Server | Token: %s | Proxy: %s' % (token.strip()[:45], proxy))
    print 
  
    x = joiner.join_server(
           token       = token.strip(),
           invite_code = Soft.INVITE_CODE,
           proxy       = proxy,
    )

    if True:
       print(x)
