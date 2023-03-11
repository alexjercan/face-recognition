# Face Recognition

Websocket and Docker server for Face Recognition.

## Quickstart

Create a folder named `whitelist` in the repo directory and add one folder for
each person that you want to be recognized. In each folder add at least one image.
The folder structure should look something like this:

```
whitelist
└── alex
    └── 1.png
```

Build the docker image for the server and deploy it

```console
make server
```

Create a venv and deploy the client

```console
python3 -m venv .venv
source .venv/bin/activate
make install-client
make client
```

## Server

The server listens on port `8765` and expects a message with the following structure:

- 4 bytes for height
- 4 bytes for width
- `height` * `width` * 3 bytes for the RGB image

The server responds with a JSON object with the following keys:

- `face_locations`: list of tuples containing `(top, right, bottom, left)` locations of the bounding box
- `face_names`: list of names for each bounding box; uses names from the whitelist folder or `Unknown` for unknown persons.

