import os,sys
from web3 import Web3
import json
import pandas as pd
from dotenv import load_dotenv
import uuid
import logger, logging
import log_filters
import numpy as np
import hashlib
import uuid
import log_decoder
from datetime import datetime
logger.setup_logging()
logger = logging.getLogger()

# for system scripts
os.chdir('/home/ubuntu/evm-bridge/oracle')


# get env vars
load_dotenv('.env')

# global vars
REQ_SIZE=10000 # number of blocks to request at once for log fetching
CONV_RATE=0.1 # change this line to implement different conversion rates (from chain -> receiving chain)


# establish w3 conn (for websocket supporting chain, you could consider using websocket)
w3_pow = Web3(Web3.HTTPProvider(os.getenv('POW_RPC_ENDPOINT')))
w3_pos = Web3(Web3.HTTPProvider(os.getenv('POS_RPC_ENDPOINT')))
print(f'PoW chain connected?: {w3_pow.is_connected()}')
print(f'PoS chain connected?: {w3_pos.is_connected()}')


# get history csv
history_path = './history/history.csv' 
if not os.path.exists(f'{history_path}'):
    logger.info(f'no previous history file exists')
    fromblock = 6654121
    history=pd.DataFrame()
else:
    logger.info(f'history file exists')
    history = pd.read_csv(f'{history_path}')
    fromblock = history.iloc[-1]['blockNumber']+1

# some functions 
# @log_filters.retry_on_error(max_retries=MAX_TRIES, delay=TIME_DELAY)
def get_logs_try(w3,filter_params):
    logs = w3.eth.get_logs(filter_params)
    return logs
    

def generate_hash_nonce():
    # Generate a random UUID first
    unique_data = uuid.uuid4().hex
    
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256(unique_data.encode())
    
    # Return the hex digest of the hash
    nonce = hash_object.hexdigest()
    return nonce[:64]  # Truncate to fit 32 bytes since Solidity bytes32 type is 32 bytes long


# listen to event 
# get recent block
recent_block = w3_pow.eth.block_number

# prep log decoding 
contract_abi =  os.getenv('ABI_JSON_PATH')
f = open(contract_abi)
contract_abi = json.load(f)['abi']
contract = w3_pow.eth.contract(address=os.getenv('POW_CONTRACT_ADDR'), abi=contract_abi)
event_abi_map = log_decoder.generate_event_abi_map(contract_abi)

# get management account for pos
private_key_pos = os.getenv('POS_PRIVATE_KEY')
account_pos = w3_pos.eth.account.from_key(private_key_pos)



for ii, step in enumerate(np.arange(fromblock,recent_block,REQ_SIZE)):

    toblock = min(step + REQ_SIZE, recent_block)
    #get logs
    args = {}
    args['fromBlock'] = step 
    args['toBlock'] = toblock 
    args['address'] = os.getenv('POW_CONTRACT_ADDR')
    args['topics'] = [Web3.keccak(text='EtherLocked(address,uint256,address)').hex()]
    filter_params = log_filters.make_filter(args)

    # fetching logs
    logs = get_logs_try(w3_pow, filter_params)

    if(len(logs)>0):
        logger.info(f'found {len(logs)} events. Processing...')

        # process each log      
        for log in logs:
            decoded_log = log_decoder.decode_log(log, event_abi_map, contract)
            # generate nonce as an identifier
            
            work={}
            work['job_time']=datetime.now()
            work['uuid']=generate_hash_nonce()
            work['blockNumber']=decoded_log['blockNumber']
            work['from']=decoded_log['args']['from']
            work['value']=decoded_log['args']['amount'] # in wei
            
            # ensure that the management address has enough ether

            balance = w3_pos.eth.get_balance(account_pos.address)
            assert balance > work['value']*CONV_RATE, "Insufficient balance"
            logger.info(f'management account balance : {balance/10**18}')

            # transfer the locked amout to the target chain
            # Transaction settings
            nonce = w3_pos.eth.get_transaction_count(account_pos.address)
            tx = {
                'chainId': int(os.getenv('CHAIN_ID_POS')),
                'nonce': nonce,
                'to': work['from'],
                'value': int(work['value']*CONV_RATE),  
                'gas': 2000000,
                'gasPrice': w3_pos.to_wei('1', 'gwei')
            }

            # Sign the transaction
            signed_tx = account_pos.sign_transaction(tx)

            # Send the transaction
            tx_hash = w3_pos.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Get the transaction hash
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Optionally, you can check the transaction receipt to confirm it has been mined
            tx_receipt = w3_pos.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Transaction receipt: {tx_receipt}")
            
            if(tx_receipt['status']==1):
                logger.info(f"Transfer was successful")
                work['tx_hash'] = tx_hash.hex()
                success_row = pd.DataFrame.from_dict(work, orient='index').T
                history = pd.concat([history, success_row])
                #save
                history.to_csv('./history/history.csv', index=False)


            else:
                logger.error(f"There was a problem with the transfer step.")

logger.info(f'Oracle job finished.')


        