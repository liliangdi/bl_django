import jwt
payload = {'username':'ybh'}
key = "123456"
token = jwt.encode(payload=payload,key=key,algorithm='HS256')
print(token)
#eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InliaCJ9.1ZQNvfi-eND6uUTPXwMYxjntwv-bjMjq0p_XrSU1WEQ'

#
s = jwt.decode(jwt=token,key=key,algorithms=['HS256'])
print(s)
