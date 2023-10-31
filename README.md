# Autogen-UI
This is a User Interface built for Autogen using ChainLit. 

# Installation and Setup
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

After installing the requirements:
1. Visit https://platform.openai.com/account/api-keys and create an API key.
2. Create a file called `.env` in the root directory of this project.
3. Add your API key to the `.env` file, with similar format to the `.env.example` file. 
4. Add your API key to the 'OAI_CONFIG_LIST' file in the root directory of this project.

# Usage
Run the following command to start the chat interface.

```shell
chainlit run app.py
```

# File Structure

This is an example of using the chainlit chat interface with multi-agent conversation between agents to complete a tasks.

The tool was developed to grab data online and then process it to easily digestible human language.      
 
`app.py` - Is an implementation of the groupchats of AutoGen. 

