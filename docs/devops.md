## Devops - Chatbot

### Env hosts machines.
```
ssh -i /path/to/Chatbot.pem ubuntu@44.230.177.187 #qa
ssh -i /path/to/Chatbot.pem ubuntu@54.190.26.156 #prod
```

### Directory structure on servers.
```
$ ls ~/
build.sh  chatbot  get_convo.sh  pull_and_build.sh  query_output  update.sh
```

The chatbot source code is at ~/chatbot directory. The other bash files are utilities to run the deployment commands.

Contents of the files are as follows.

#### build.sh
```
cd ~/chatbot
docker compose build
docker compose up -d
```

#### update.sh
```
cd ~/chatbot
git pull
docker compose down
docker compose build
docker compose up -d rasa-actions
docker exec -it chat_rasa_actions /bin/bash
```

#### pull_and_build.sh
```
cd ~/chatbot
git pull
docker compose build
docker compose up -d
```

### Deployment when training is required.
#### Train the RASA model
Run `bash update.sh` to pull the latest version and enter the chat_rasa_actions container.

Inside the container, run following commands:

```
# remove current model
rm models/default.tar.gz -f 

# train model with latest code
rasa train --fixed-model-name default --data data --domain data --force

#copy model to disk for building rasa_core container.
docker cp chat_rasa_actions:/app/models/default.tar.gz ~/chatbot/app/rasa/models/
```

#### Build all containers
After training has been done, run `bash build.sh` to build the remaining containers and start all chatbot services.


### Deployment when training is NOT required.
Assumptions:

- This step assumes that a trained model is already present at the location `~/chatbot/app/rasa/models/default.tar.gx`
- There are no code changes in the latest version which require re-training of the RASA model.

Run `bash pull_and_build.sh` to pull the latest version, build the containers and start all chatbot services.

