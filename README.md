# autodoist

An automated system for managing my todos via the [Todoist API](https://developer.todoist.com/sync/v7/).

# Building the image

```bash
docker build -t autodoist .
```

# Running the container

First, set the TODOIST_API_TOKEN environment variable in your shell with
```bash
export TODOIST_API_TOKEN=<token>
```
replacing `<token>` with your token.


Then run the container.
```bash
docker run -it -e TODOIST_API_TOKEN autodoist
```
