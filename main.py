import os
import time

from dotenv import load_dotenv
from web3 import Web3


# Load environment variables
load_dotenv()
ETH_NODE_URL = os.getenv("ETH_NODE_URL")

# Create connection to Ethereum node
web3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))


def main():
    if not web3.is_connected():
        print("\nFailed to connect to the Ethereum node.")
        return
    
    print("\nConnected to the Ethereum node.")
    print("Node version:", web3.client_version)

    # Fetch pending block
    pending_block = web3.eth.get_block('pending')
    pending_block_number = pending_block.number

    # Retry fetching the finalized block with the same block number as the pending block
    finalized_block = None
    start_time = time.time()
    while True:
        try:
            finalized_block = web3.eth.get_block(pending_block_number, full_transactions=True)
            break
        except Exception as e:
            if time.time() - start_time > 60:
                print(f"Failed to fetch the finalized block within 60 seconds: {e}")
                return
        time.sleep(2)

    # Compare transactions in the pending block and finalized block
    print(f"\nComparing transactions in pending block and finalized block (block number: {pending_block_number}):")
    pending_block_tx_hashes = {tx.hex() for tx in pending_block.transactions}
    finalized_block_tx_hashes = {tx['hash'].hex() for tx in finalized_block.transactions}

    common_txs = pending_block_tx_hashes.intersection(finalized_block_tx_hashes)
    pending_only_txs = pending_block_tx_hashes - finalized_block_tx_hashes
    finalized_only_txs = finalized_block_tx_hashes - pending_block_tx_hashes

    print(f"Common transactions: {len(common_txs)}")
    print(f"Transactions only in pending block: {len(pending_only_txs)}")
    print(f"Transactions only in finalized block: {len(finalized_only_txs)}")


if __name__ == "__main__":
    main()