import fastapi
import uvicorn
import ssl

app = fastapi.FastAPI()


@app.get('/', response_class=fastapi.responses.HTMLResponse)
async def GET_root():
    return '''
    <body>
        <b style="color: sandybrown">HELLO WORLD!</b>
    </body>
    '''


# these cert files are generated from openssl
# openssl req -new -x509 -nodes -newkey rsa:1024 -keyout server.key -out server.crt -days 3650
# i used openssl from cygwin myself, since i am on windows
# it is self signed, so browsers dont like it, but it works for my testing purposes
# this is where services like free ssl sources like LetsEncrypt come in, but thats overkill for testing environments
uvicorn.run(app, ssl_certfile='certs/server.crt', ssl_keyfile='certs/server.key')

# uvicorn.run(app) # non-ssl version
