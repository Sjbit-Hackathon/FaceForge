import urllib.request as r, json, urllib.error as e
req=r.Request('http://127.0.0.1:8000/auth/register', data=json.dumps({'email':'test@example.com','password':'password','full_name':'Test User','badge_id':'999','role':'detective'}).encode(), headers={'Content-Type':'application/json'})
try:
    print(r.urlopen(req).read())
except e.HTTPError as ex:
    print(ex.read())