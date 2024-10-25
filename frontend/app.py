import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from web3 import Web3
import json
from dotenv import load_dotenv

app = Flask(__name__, static_url_path='/static')
CORS(app) # for testing

# Load environment variables
load_dotenv('../client_side/.env')

# Setup Web3 connection
CHAIN_ID_POW = int(os.getenv('CHAIN_ID_POW'))
w3_pow = Web3(Web3.HTTPProvider(os.getenv('POW_RPC_ENDPOINT')))

# Contract setup
pow_bridge_addr = os.getenv('POW_CONTRACT_ADDR')
if not pow_bridge_addr:
    raise ValueError("POW_CONTRACT_ADDR not set in environment variables")

pow_bridge_abi_path = '../contract/ignition/deployments/chain-702/artifacts/UZHETH_BridgeModule#CombinedBridge.json'

def get_abi(abi_path):
    with open(abi_path) as f:
        data = json.load(f)
        return data['abi']

pow_abi = get_abi(pow_bridge_abi_path)
pow_contract = w3_pow.eth.contract(address=Web3.to_checksum_address(pow_bridge_addr), abi=pow_abi)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lock_ether', methods=['GET', 'POST'])
@cross_origin()
def lock_ether():
    if request.method == 'GET':
        return jsonify({"message": "GET request received. Use POST to lock Ether."}), 200
    try:
        amount = float(request.json['amount'])
        from_address = request.json.get('from')  # Get the 'from' address from the request

        if not from_address:
            return jsonify({'error': 'From address not provided'}), 400

        transaction = pow_contract.functions.lockEther(pow_bridge_addr).build_transaction({
            'chainId': CHAIN_ID_POW,
            'gas': 2000000,
            'gasPrice': w3_pow.to_wei(50, 'gwei'),
            'nonce': w3_pow.eth.get_transaction_count(Web3.to_checksum_address(from_address)),
            'from': Web3.to_checksum_address(from_address),
            'value': w3_pow.to_wei(amount, 'ether')
        })

        return jsonify({
            'to': transaction['to'],
            'from': transaction['from'],
            'value': transaction['value'],
            'data': transaction['data'],
            'gas': transaction['gas'],
            'gasPrice': transaction['gasPrice'],
            'chainId': transaction['chainId']
        })
    except Exception as e:
        app.logger.error(f"Error in lock_ether: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_abi', methods=['GET'])
def get_contract_abi():
    return jsonify(pow_abi)

@app.route('/get_contract_address', methods=['GET'])
def get_contract_address():
    return os.getenv('POW_CONTRACT_ADDR')

if __name__ == '__main__':
    app.run(debug=True)
