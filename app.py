from dotenv import load_dotenv

load_dotenv(verbose=True)
from dapr.ext.fastapi import DaprActor
from dapr.conf import settings
from fastapi import FastAPI
from service.init_blueprint import init_blueprint
from handel.fixed_rules_spider.fixed_rules_spider_actor import FixedRulesSpiderActor
import json
import uvicorn
import ujson


class UJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            return ujson.dumps(obj)
        except TypeError:
            return json.JSONEncoder.default(self, obj)

    def encode(self, obj):
        try:
            return ujson.dumps(obj)
        except TypeError:
            return json.dumps(obj, ensure_ascii=False)


json._default_encoder = UJSONEncoder(
    skipkeys=False,
    ensure_ascii=False,
    check_circular=True,
    allow_nan=True,
    indent=None,
    separators=None,
    default=None,
)

app = FastAPI(title=f'spider-actor-service')
init_blueprint(app)
app.debug = True
app.json_encoder = UJSONEncoder
settings.DAPR_RUNTIME_HOST = "192.168.1.10"
settings.DAPR_HTTP_PORT = 3501
# Add Dapr Actor Extension
actor = DaprActor(app)


@app.on_event("startup")
async def startup_event():
    # Register SpiderActor
    await actor.register_actor(FixedRulesSpiderActor)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3100)
