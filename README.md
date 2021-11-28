# Stonk User Account Service

Webservice that manages users for Stonks application, including sign-up, sign-in, sign-out as well as address management.

## boto3 configuration
To run service with middleware configure boto3 as per 'https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html'

## To Run Google Login:
## ![google_login2](https://user-images.githubusercontent.com/20402192/142379338-845ef43b-db9f-4631-abb0-74be3fddba7c.gif)

1. Sync requirment.txt to install flask-dance
2. Set 2 environment variables:
`OAUTHLIB_INSECURE_TRANSPORT=1 `  
`OAUTHLIB_RELAX_TOKEN_SCOPE=1`
3. Run the app.py and go to: http://127.0.0.1:5000/google-auth
4. After successful log-in with Google, the server should return the user's userID and token
