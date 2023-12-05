---
title: Autogen Template
emoji: 🔥
colorFrom: indigo
colorTo: green
sdk: docker
pinned: false
license: apache-2.0
---

# Installation and Setup
You will need Python, Conda, Docker (Optional for code-execution), Git, and a text editor installed.

First install python=3.11 and other 3rd party dependencies. If you have conda installed, you can run the following commands:

```shell
conda create --name demo python=3.11 -y
conda activate demo

pip install -r requirements.txt
```

If you do not have conda installed but have virtualenv installed, you can run the following commands:
```shell
pip install virtualenv
virtualenv demo -p python3.

# on windows
demo\Scripts\activate
# on mac/linux
source demo/bin/activate

pip install -r requirements.txt
```

# Configure the environment variables
Notion webpage for instructions:
https://lopsided-zipper-e29.notion.site/ReviewGPT-57444b82eac643539e393b8fc34d2f38?pvs=4

# Usage
Run the following command to start the chat interface. Change the logo files on the /public folder to change the logo.

```shell
chainlit run app.py
```

# File Structure

This is an example of using the chainlit chat interface with multi-agent conversation between agents to complete a tasks.

The tool was developed to grab SAP data online and then process it to easily digestible human language.      
 
`app.py` - Starts the chat interface.

