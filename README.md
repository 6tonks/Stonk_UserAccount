# Stonk User Account Service

Webservice that manages users for Stonks application, including sign-up, sign-in, sign-out as well as address management.

## To Run
1. Upload project folder to an EC2 instance (ex: use WinSCP)
2. cd to the directory and run ```pip3 install -r requirements.txt``` to install dependancy
3. Copy ```db_config.py``` to ```/config``` folder, and ```local.py``` to root the folder (same directory as app.py)
4. run ```tmux``` (To keep server keep running even after terminal is closed)
5. run ```python3 app.py```
6. Close the terminal

***Important*** : Do not stop the EC2 instance, which will cause the hostname to be changed when next time started, and break the connection to the API gateway.

## To Test The API
Please use this Swagger Link to test the API. (This Swagger page will call the user service API through the CloudFront domain)
https://app.swaggerhub.com/apis-docs/pies2/stonk-user_service_api/1.0.0#/
### Notes:
1. The "/users/{userId}" is removed from the API swagger for now as it's having some issue
2. Google Login only work on local now, but as [this post]([https:/](https://edstem.org/us/courses/13500/discussion/851335)/) mentioned, testing it on EC2 isn't required.
If you want to test it locally, please refer to the ***Test Google Login Locally*** section below.

#### Test Google Login Locally:


1. Sync requirment.txt to install flask-dance
2. Set 2 environment variables:
`OAUTHLIB_INSECURE_TRANSPORT=1 `  
`OAUTHLIB_RELAX_TOKEN_SCOPE=1`
3. Run the app.py and go to: http://127.0.0.1:5000/google-auth
4. After successful log-in with Google, the server should return the user's userID and token

The result should be something like this:

<img src="https://user-images.githubusercontent.com/20402192/142379338-845ef43b-db9f-4631-abb0-74be3fddba7c.gif" alt="drawing" width="300"/>

## boto3 configuration
To run service with middleware configure boto3 as per 'https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html'


