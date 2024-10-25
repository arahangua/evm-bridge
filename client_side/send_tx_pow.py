import os, sys
from web3 import Web3
import json
from dotenv import load_dotenv

# get env vars
load_dotenv('.env')

# deployed contract address
pow_bridge_addr = os.getenv('POW_CONTRACT_ADDR')
pow_bridge_abi = '../contract/ignition/deployments/chain-702/artifacts/UZHETH_BridgeModule#CombinedBridge.json'

# for reading abi
def get_abi(abi_path):
    f = open(abi_path)
    abi = json.load(f)['abi']
    return abi

# setup web3 connection 
CHAIN_ID_POW = int(os.getenv('CHAIN_ID_POW'))
w3_pow = Web3(Web3.HTTPProvider(os.getenv('POW_RPC_ENDPOINT')))
print(f'PoW chain connected?: {w3_pow.is_connected()}')


# make a contract var
pow_abi = get_abi(pow_bridge_abi)
pow_contract = w3_pow.eth.contract(address=pow_bridge_addr, abi=pow_abi)

# set your account 
private_key_pow = os.getenv('POW_PRIVATE_KEY')
account_pow = w3_pow.eth.account.from_key(private_key_pow)

# prep transaction (calling lockether function)(for uzheth, we use conventions before eip-1559)
def prep_tx_lockEther(w3, contract, account, chain_id_for_oracle, amount_to_lock):
    transaction = contract.functions.lockEther(chain_id_for_oracle).build_transaction({
        'chainId': CHAIN_ID_POW, # chain id
        'gas': 2000000, # Gas limit, adjust based on needs
        'gasPrice': w3.to_wei(50, 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
        'value': w3.to_wei(amount_to_lock, 'ether')  # Sending 1 Ether; adjust as needed
    })
    return transaction

# prep tx
lockEther_pow_tx = prep_tx_lockEther(w3_pow, pow_contract, account_pow, pow_bridge_addr, amount_to_lock=1) # the oracle uses deployed contract addr as a chain alias

# Sign transaction
signed_txn = account_pow.sign_transaction(lockEther_pow_tx)

# Send transaction
txn_hash = w3_pow.eth.send_raw_transaction(signed_txn.rawTransaction)

# Get transaction receipt to confirm success
txn_receipt = w3_pow.eth.wait_for_transaction_receipt(txn_hash)
print(f"Transaction successful with hash: {txn_receipt.transactionHash.hex()}")