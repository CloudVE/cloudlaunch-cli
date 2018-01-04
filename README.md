# cloudlaunch-cli
CLI client for CloudLaunch

# Quickstart

1. Create a virtual environment and activate it
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
2. Install `cloudlaunch-cli` from GitHub
    ```
    pip install git+https://github.com/CloudVE/cloudlaunch-cli.git#egg=cloudlaunch-cli
    ```
3. The CloudLaunch CLI requires two config settings. First is the URL of the API root:
    ```
    cloudlaunch config set url https://beta.launch.usegalaxy.org/cloudlaunch/api/v1
    ```
4. Second config setting is an auth token. To get an auth token, first log into
CloudLaunch, for example, by going to https://beta.launch.usegalaxy.org/login.
Then navigate to the `/api/v1/auth/api-auth-token` API endpoint, for example,
https://beta.launch.usegalaxy.org/cloudlaunch/api/v1/auth/api-token-auth/. Copy
the token out of the JSON response and then run the following (substituting your
own token instead):
    ```
    cloudlaunch config set token b38faadf2ef6d59ce46711ed73e99d6...
    ```
5. Now you should be able to list your deployments
    ```
    cloudlaunch deployments list
    ```
6. You can create a deployment as well
    ```
    cloudlaunch deployments create my-ubuntu-test ubuntu \
        amazon-us-east-n-virginia --application-version 16.04
    ```

# Installing for development

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `python setup.py develop`

Now you can run `cloudlaunch`.
