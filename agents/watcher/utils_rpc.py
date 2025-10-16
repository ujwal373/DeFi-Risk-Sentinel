from web3 import Web3
from dotenv import load_dotenv
import os, datetime

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_latest_tx(wallet):
    wallet = Web3.to_checksum_address(wallet)
    tx_count = web3.eth.get_transaction_count(wallet)
    
    if tx_count == 0:
        return None  # No transactions

    # Get latest tx by looking one back from current count
    latest_tx = web3.eth.get_transaction_by_block('latest', -1)
    return latest_tx

def get_contract_age(address):
    creation_block = web3.eth.get_transaction_receipt(address).blockNumber
    current_block = web3.eth.block_number
    block_age = current_block - creation_block
    days = block_age * 12 / 3600 / 24  # assume 12s/block
    return round(days, 2)
