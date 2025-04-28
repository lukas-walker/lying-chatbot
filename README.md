---
title: The Lying Chatbot
emoji: 🌖
colorFrom: red
colorTo: purple
sdk: gradio
sdk_version: 5.17.1
app_file: app.py
pinned: false
license: mit
short_description: Classic riddle where only one of the two tells the truth.
---


When cloning this app and running it in a Docker container, you'll have to manually add a docker-compose.yml file and adapt the ports the container is supposed to listen to. 

Example yaml:

```
version: '3'
services:
  chatbot:
    build: .
    ports:
      - "7860:7860"
    restart: always
```

