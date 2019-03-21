# autodoist

An automated system for managing my todos via the [Todoist API](https://developer.todoist.com/sync/v7/).

# Building the image

```bash
docker build -t autodoist .
```

# Running the container

First, set some environment variables in your shell with
```bash
export <variable name>=<variable value>
```
You'll need to set the TODOIST_API_TOKEN variable to your API token, found on
the Settings > Integrations page of the Todoist app.

You'll also need  to set EMAIL_ADDR and EMAIL_PW to the credentials for your
gmail account (see
[here](https://stackabuse.com/how-to-send-emails-with-gmail-using-python/) for
a tutorial that will get you started).


Then run the container, passing the environment variables and setting Docker's
restart policy to "always".
```bash
docker run -d -e TODOIST_API_TOKEN -e EMAIL_PW -e EMAIL_ADDR --restart always autodoist
```
