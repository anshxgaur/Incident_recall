import importlib, json
candidates=['hindsight','hindsight_client','hindsight_client_sdk','hindsight_sdk','hindsightclient']
out={}
for name in candidates:
    try:
        m=importlib.import_module(name)
        out[name]={'found':True,'attrs':sorted([a for a in dir(m) if not a.startswith('_')])}
    except Exception as e:
        out[name]={'found':False,'error':str(e)}
print(json.dumps(out))
