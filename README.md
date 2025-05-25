# exten.bot

exten.bot is a Django-based web interface for creating VoIP voice bots that can be connected to any software or hardware PBX supporting SIP.

The system is built on an OpenSIPS server and the [opensips-ai-voice-connector](https://github.com/OpenSIPS/opensips-ai-voice-connector-ce).

For AI, it uses the OpenAI real-time API.

The platform supports dify.ai workflows for designing bot logic and integrating with other systems via function calls.

You can test its features at [exten.bot](https://exten.bot).

## Installation 

### SIP Server OpenSIPS

+ You need to install the OpenSIPS 3.5 server; please use the [official documentation](https://www.opensips.org/Documentation/Manual-3-5) for this.
+ place the configuration files [opensips.cfg](examples/opensips-cli.cfg) and [opensips-cli.sfg](examples/opensips-cli.cfg) in the folder 
/etc/opensips and replace the database connection data with your own
+ add your sip exten.bot domain (exten.example.com) to opensips domains tables

### AI Voice Connector 
If you need dify.ai workflow support use my fork of the [voice connector](https://github.com/estvita/opensips-ai-voice-connector-ce), otherwise you can use the original

I haven't tested my connection with installing the openai voice connector in Docker, so for now we'll run it in a virtual python environment.

```
git clone https://github.com/estvita/opensips-ai-voice-connector-ce voice
cd voice 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp examples/config.ini config.ini
```

make changes to the config.ini

+ [rtp] SIP_SERVER_IP - your sip server address
+ [engine] api_url - your exten.bot/api/bots/

try running the voice connector

```
python src/main.py -c config.ini
```

in the console you should see something like this

```
2025-05-25 11:44:11,575 - tid: 139832749932608 - INFO - Starting server at 127.0.0.1:50060
```
After testing you can run voice connector as a [debian service](examples/connector.service)

+ Next install the exten_bot

```
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
```
## Settings

go to the admin panel at your_domain/admin and fill in the following data

+ /admin/bot/domain/ add the domain (exten.example.com), the same as in the opensips domain settings
+ /admin/bot/model/ add models [gpt-4o-realtime-preview](https://platform.openai.com/docs/models/gpt-4o-realtime-preview)
+ /admin/bot/voice/ add bot [voices](https://platform.openai.com/docs/guides/realtime-conversations#voice-options)

if you want to use [dify.ai workflows](https://dify.ai/blog/dify-ai-workflow) 
+ /admin/workflow/dify/ add api-key and url
+ /admin/bot/function/ add a [description of the function](https://platform.openai.com/docs/guides/function-calling?api-mode=responses#defining-functions) that the voice bot will call when necessary

Now you can create a voice bot
+ /admin/bot/bot/ add bot

Description of fields

+ Owner - the user to whom the bot will be linked
+ Username and Password - are generated automatically, you will use this data to connect to the SIP
+ Domain - your exten.bot SIP domain
+ Token - [openai token](https://platform.openai.com/api-keys)
+ Model - openai realtime model
+ Voice - openai voice
+ Dify - If you have created a dify.ai workflow, you can link it to a voice bot here
+ Instruction - text instruction for the bot
+ Welcome msg - the message that the bot will voice when connecting
+ Transfer uri - sip uri to which the voice bot will forward the call at the user's request (sip:operator@pbx.com)
+ Functions - Check the required functions that the voice bot will access based on the context of the conversation

After this, check that the account has been created in the opensips database (subscriber table).

if everything is ok, you can use the received credentials of the sip account on your softphone or PBX to call [openai@exten.example.com] and talk to your voice bot on the phone

To diagnose the SIP connection on your server, use the console utility [sngrep]
