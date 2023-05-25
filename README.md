# wl-context-aware-sofi-chatbot-wlbot-rasa3
Rasa 3 needs python 3.7 and above.
```
sudo apt-get install python3.8 python3.8-venv
```
Create virtual env with python3.8
```
python3.8 -m venv rasa3    
```
activate the venv and upgrade pip to latest for installing rasa(specify version 3.2).
```
source rasa3/bin/activate
pip3 install -U --user pip && pip3 install rasa
```
install setup and build tools.
```
sudo apt-get install build-essential
pip3 install --upgrade setuptools
sudo apt-get install python3-dev
```
install dependencies from requirements.txt.
```
pip3 install -r requirements.txt
```
[Note: both wlbot and wlapp dependencies are present in the same venv for now]

Things to look at during code migration:
1. Domain file(all components)
2. Config file(Changes in pipeline and policies)