# exten.bot

exten.bot is a Django-based web interface for creating VoIP voice bots that can be connected to any software or hardware PBX supporting SIP.

The system is built on an OpenSIPS server and the [opensips-ai-voice-connector](https://github.com/OpenSIPS/opensips-ai-voice-connector-ce).

For AI, it uses the OpenAI real-time API.

The platform supports custom functions and MCP servers for extending bot capabilities and integrating with external systems.

You can test its features at [exten.bot](https://exten.bot).

## Installation

OS: Debian 12
DB: MySQL

### SIP Server OpenSIPS

+ You need to install the OpenSIPS 3.6 server; please use the [official documentation](https://www.opensips.org/Documentation/Manual-3-6) for this.

+ Install [opensips-cli](https://github.com/OpenSIPS/opensips-cli/blob/master/docs/INSTALLATION.md)
+ Install opensips modules: opensips-mysql-module, opensips-mysql-dbschema, opensips-json-module, opensips-http-modules, opensips-restclient-module, opensips-auth-modules, opensips-dialplan-module
```
curl https://apt.opensips.org/opensips-org.gpg -o /usr/share/keyrings/opensips-org.gpg
echo "deb [signed-by=/usr/share/keyrings/opensips-org.gpg] https://apt.opensips.org bookworm 3.6-releases" >/etc/apt/sources.list.d/opensips.list
echo "deb [signed-by=/usr/share/keyrings/opensips-org.gpg] https://apt.opensips.org bookworm cli-nightly" >/etc/apt/sources.list.d/opensips-cli.list

apt update

apt install opensips opensips-cli opensips-mysql-module opensips-mysql-dbschema opensips-json-module opensips-http-modules opensips-restclient-module opensips-auth-modules opensips-dialplan-module
```
+ Optional: install [openssips-cp](https://github.com/OpenSIPS/opensips-cp)
+ place the configuration files [opensips.cfg](examples/opensips.cfg) and [opensips-cli.sfg](examples/opensips-cli.cfg) in the folder 
/etc/opensips and replace the database connection data with your own
+ create opensips db: opensips-cli -x database create
+ add your sip exten.bot domain (exten.example.com) to opensips domains tables

### Exten.bot Web App

```
sudo apt-get install build-essential libmysqlclient-dev python3-dev libssl-dev pkg-config
git clone https://github.com/estvita/exten_bot.git
cd exten_bot
cp examples/.env.example .env
Make the necessary changes to your .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/production.txt
```

After installing the required packages and dependencies, proceed with the basic configuration.

```
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

python manage.py runserver 0.0.0.0:8000
```

in the admin panel /admin/authtoken/ create and save user token

### AI Voice Connector 
Use my fork of the [voice connector](https://github.com/estvita/opensips-ai-voice-connector-ce) for enhanced functionality

I haven't tested my connection with installing the openai voice connector in Docker, so for now we'll run it in a virtual python environment.

```
git clone https://github.com/estvita/opensips-ai-voice-connector-ce connector
cd connector 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp docs/config.example config.ini
```

make changes to the config.ini

```
[opensips]
ip = 127.0.0.1
port = 8080

[rtp]
ip = 192.168.3.29 vyour Opensips server external address
min_port = 10000
max_port = 20000

[engine]
event_ip = 127.0.0.1
bind_ip = 0.0.0.0
event_port = 50060
api_url = http://127.0.0.1:8000/api/bots/ your exten.bot api url
api_key = XXXXXXXXXXXXX token generated in exten.bot Django admin
```

try running the voice connector


```
python src/main.py -c config.ini -l INFO
```

in the logs/app.log you should see something like this

```
2025-05-25 11:44:11,575 - tid: 139832749932608 - INFO - Starting server at 127.0.0.1:50060
```
After testing you can run voice connector as a [debian service](examples/connector.service)

## Settings

go to the admin panel at your_domain/admin and fill in the following data

+ /admin/bot/domain/ add the domain (exten.example.com), the same as in the opensips domain settings
+ /admin/bot/model/ add models [gpt-4o-realtime-preview](https://platform.openai.com/docs/models/gpt-4o-realtime-preview)
+ /admin/bot/voice/ add bot [voices](https://platform.openai.com/docs/guides/realtime-conversations#voice-options)

+ /admin/workflow/function/ add custom functions that the voice bot can call during conversations
+ /admin/workflow/mcp/ add MCP servers for extended bot capabilities

Now you can create a voice bot
+ /admin/bot/bot/ add bot

Description of fields

+ Owner - the user to whom the bot will be linked
+ Username and Password - are generated automatically, you will use this data to connect to the SIP
+ Domain - your exten.bot SIP domain
+ Token - [openai token](https://platform.openai.com/api-keys)
+ Model - openai realtime model
+ Voice - openai voice
+ Instruction - text instruction for the bot
+ Welcome msg - the message that the bot will voice when connecting
+ Transfer uri - sip uri to which the voice bot will forward the call at the user's request (sip:operator@pbx.com)
+ Functions - Select custom functions that the voice bot can access during conversations
+ MCP Servers - Select MCP servers for extended bot capabilities

After this, check that the account has been created in the opensips database (subscriber table).

if everything is ok, you can use the received credentials of the sip account on your softphone or PBX to call [openai@exten.example.com] and talk to your voice bot on the phone

To diagnose the SIP connection on your server, use the console utility [sngrep]

## Functions and MCP Servers

### Custom Functions
- Go to `/admin/workflow/function/` to create custom functions
- Each function requires: name, URL, JSON schema, and optional input schema
- Functions are linked to bots and can be called during conversations
- Only bot owners can link their own functions to their bots

### MCP Servers
- Go to `/admin/workflow/mcp/` to add MCP servers
- Each server requires: base URL, optional API key, and approval settings
- Server labels are auto-generated but can be edited
- MCP servers provide extended capabilities to voice bots
- Only bot owners can link their own MCP servers to their bots
