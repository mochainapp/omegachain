import hashlib
import time
import json
from flask import Flask, jsonify, request

# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(transactions="Genesis Block", previous_hash='0', fees=0)

    def create_block(self, transactions, previous_hash, fees):
        block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': transactions,
            'fees': fees,
            'previous_hash': previous_hash,
            'hash': ''
        }
        block['hash'] = self.hash_block(block)
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash_block(previous_block):
                return False
            previous_block = block
            block_index += 1
        return True

# Flask web app setup
app = Flask(__name__)

blockchain = Blockchain()

# Automatic mining every 6 seconds
def mine_automatically():
    while True:
        previous_block = blockchain.get_previous_block()
        previous_hash = previous_block['hash']
        new_block = blockchain.create_block(
            transactions="Automatic mining",
            previous_hash=previous_hash,
            fees=0.5 if len(blockchain.chain) % 2 == 0 else 0.75
        )
        print(f"Block mined: {new_block}")
        time.sleep(6)

# Route to get the blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# Route to manually mine a block (optional for testing)
@app.route('/mine_block', methods=['POST'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block['hash']
    new_block = blockchain.create_block(
        transactions=request.json['transactions'],
        previous_hash=previous_hash,
        fees=request.json['fees']
    )
    response = {
        'message': 'Block mined successfully',
        'block': new_block
    }
    return jsonify(response), 201

# Function to start the Flask server
if __name__ == '__main__':
    from threading import Thread
    miner_thread = Thread(target=mine_automatically)
    miner_thread.daemon = True
    miner_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
