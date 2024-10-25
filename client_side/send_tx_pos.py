import os, sys
from web3 import Web3
import json
from dotenv import load_dotenv

# get env vars
load_dotenv('.env')

# deployed contract address
pos_bridge_addr = os.getenv('POS_CONTRACT_ADDR')
pos_bridge_abi = '../contract/ignition/deployments/chain-8888/artifacts/UZHETH_BridgeModule#CombinedBridge.json'

# for reading abi
def get_abi(abi_path):
    f = open(abi_path)
    abi = json.load(f)['abi']
    return abi

# setup web3 connection 
CHAIN_ID_POS = int(os.getenv('CHAIN_ID_POS'))
w3_pos = Web3(Web3.HTTPProvider(os.getenv('POS_RPC_ENDPOINT')))
print(f'PoS chain connected?: {w3_pos.is_connected()}')


# make a contract var
pos_abi = get_abi(pos_bridge_abi)
pos_contract = w3_pos.eth.contract(address=pos_bridge_addr, abi=pos_abi)

# set your account 
private_key_pos = os.getenv('POS_PRIVATE_KEY')
account_pos = w3_pos.eth.account.from_key(private_key_pos)


# prep transaction (calling lockether function)(for uzheth, we use conventions before eip-1559)
def prep_tx_lockEther(w3, contract, account, chain_id_for_oracle, amount_to_lock):
    transaction = contract.functions.lockEther(chain_id_for_oracle).build_transaction({
        'chainId': CHAIN_ID_POS, # chain id
        'gas': 2000000, # Gas limit, adjust based on needs
        'gasPrice': w3.to_wei(50, 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
        'value': w3.to_wei(amount_to_lock, 'ether')  # Sending 1 Ether; adjust as needed
    })
    return transaction


# prep tx 
lockEther_pos_tx = prep_tx_lockEther(w3_pos, pos_contract, account_pos, pos_bridge_addr, amount_to_lock=0.01) # the oracle uses deployed contract addr as a chain alias
# Sign transaction
signed_txn = account_pos.sign_transaction(lockEther_pos_tx)

# Send transaction
txn_hash = w3_pos.eth.send_raw_transaction(signed_txn.rawTransaction)

# Get transaction receipt to confirm success
txn_receipt = w3_pos.eth.wait_for_transaction_receipt(txn_hash)
print(f"Transaction successful with hash: {txn_receipt.transactionHash.hex()}")