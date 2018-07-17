import json


def hello(event, context):
    try:
        raise Exception("Oh no it broke")
        return dict(
            statusCode=200,
            body=json.dumps(event)
        )
    except Exception as e:
        return dict(
            statusCode=500,
            body=str(e)
        )
