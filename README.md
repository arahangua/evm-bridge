# evm-bridge
Barebone, NOT production ready implementation of bridge/oracle implementation for educational purpose

This is an all-in-one repo for deploying a bridge contract/oracle (centralized oracle) between two EVM chains. 
Currently, the Oracle implements one-directional logic (i.e., sending PoW-mined ether to PoS-mined ether). You can easily make it bidirectional by modifying the below implementation. 

## Project structure

```
├── README.md
├── client_side
├── contract
├── frontend
├── oracle
├── static
└── systemctl
```
### client_side
Under 'client_side' folder, there are example codes ('send_tx_pos.py', 'send_tx_pow.py') to interact with the deployed bridge contract. 

### contract 
Under 'contract' folder, we have a full working files and scripts (Hardhat) for a bridge contract deployment. 

### oracle
Under 'oracle' folder, we have a python script that is supposed to run using system daemon (systemctl) that will listen and execute necessary actions. Therefore, you need to make sure that the server for running these scripts should have access (i.e., can make rpc requests) to both chains. 

### static
All visuals for this readme is here.  

### systemctl
You can find a template ('oracle.service') to run a system daemon job.

### frontend
The frontend folder contains the web interface for interacting with the bridge contract. It includes:
- `app.py`: A Flask application serving as the backend for the web interface.
- `templates/index.html`: The HTML template for the web page.
- `static/js/script.js`: The JavaScript file handling client-side logic and MetaMask interactions.

## Getting started
Here is a walkthrough to follow if you are starting from scratch. Please note the following reflects the project contributor's preference.

## [contract] 1. Setting up an environment for a bridge contract deployment/development 

You can use either truffle or hardhat. In this project we use hardhat

1. configure nvm
```
    sudo apt update
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
```
After installing nvm as above, you might need to restart your terminal

2. Install nodejs 
```
nvm install node
```
As a side note, any nodejs version that is LTS should do the job but you can install different versions of node js using the following command

```
nvm install <version number>
```

3. Install Hardhat 

let's move to the contract directory (make one if you don't have it already.) and install hardhat (for npm 7+)

```
cd contract
npm install --save-dev hardhat # this sets hardhat in your current projet directory (package.json)
# normally you should initializa the project using "npx hardhat init" like commands but you don't need to do it if you pulled this repo.
```

4. Write bridge contracts 

If you've followed the instruction until now (as of 18.06.2024), you should see 'Lock.sol' under contracts directory. Let's rename it and change the contents inside. <br>
In this readme, we only consider one-sided workflow in which we deploy the contract to one chain. It is a matter of changing just one network flag argument during the deployment step to deploy it to the other chain. (it will be covered later) <br>
For the actual bridge contract content, please note that there is a lot more to consider than what is implemented here. Here we use bare minimum. Please check combinedBridge.sol.

5. Deploy the contract

We need to first set network setting and private key to deploy the contract(s).
Please refer to hardhat.config.js for network configuration.

You need to install dotenv for environment variable handling, if you don't have it already.

```
npm i dotenv
```

In hardhat, you can compile and deploy the contract using the following lines
(we are using ignition module of hardhat to deploy the contract(s))
```
npx hardhat compile
npx hardhat ignition deploy ignition/modules/CombinedBridge_to_pow.js --network pow_chain # for pow
npx hardhat ignition deploy ignition/modules/CombinedBridge_to_pos.js --network pos_chain # for pos
```

6. Use the bridge contract to lock Ether 

Please see 'send_tx_pos.py' and 'send_tx_pow.py' files under 'client_side' directory to see the usage. For library requirements, please see pyproject.toml file. A requirement file is also exported for your convenience (requirements.txt)

Please make sure you've configured .env file properly. 'env_example' is provided for your reference.

For bi-directional implementation in the future, you might want to perform unlocking operations. For this, you need to call "queue_unlockEther" function given the current bridge contract implementation.

## [oracle] Running the oracle
Below we consider only PoW --> PoS ether transfer case.

1. Install python requirements / configure few paths

Please use pyproject.toml to configure/install environment. A requirement file is also exported for your convenience (requirements.txt)

Please make sure you've configured .env file properly. 'env_example' is provided for your reference.

2. Configure system daemon 

copy 'oracle.service' under systemctl folder to systemd location
```
cp oracle.service /etc/systemd/system/oracle.service
```
then activate the system daemon
```
sudo systemctl start oracle.service
```
you can check the workings of the job using journalctl
```
sudo journalctl -u oracle.service
```

3. Explanation on what the oracle script does (listener.py)

After calling 'lockEther' function from PoW, event log is broadcasted. 'listener.py' then listens and capture this event and sends the corresponding ether to the same address in PoS. If the transfer of ether was succesful then each processed instance is saved/appended to 'history.csv' file under ./oracle/history folder. 

## [frontend] Setting up and running the web interface

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - Copy the `.env.example` file to `.env`
   - Fill in the required values in the `.env` file

4. Run the Flask application:
   ```
   python app.py
   ```

5. Open a web browser and navigate to `http://localhost:5000` to access the web interface.

The web interface allows users to:
- Connect to MetaMask
- Lock Ether from the sending chain (the script assumes that we are sending Ether from POW to POS)
- View transaction status and results

Make sure MetaMask is installed in your browser and configured to connect to the correct PoW network before using the interface.

