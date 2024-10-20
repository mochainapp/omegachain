import hashlib
import time
import json
import requests
from flask import Flask, jsonify, request
from threading import Thread

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.peers = set()
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

    def add_peer(self, peer):
        self.peers.add(peer)

    def sync_chain(self):
        for peer in self.peers:
            try:
                response = requests.get(f'http://{peer}/chain')
                if response.status_code == 200:
                    peer_chain = response.json()['chain']
                    if len(peer_chain) > len(self.chain) and self.is_chain_valid(peer_chain):
                        self.chain = peer_chain
            except requests.exceptions.RequestException as e:
                print(f"Failed to connect to peer {peer}: {e}")

blockchain = Blockchain()

app = Flask(__name__)

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

# Routes
@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/mine_block', methods=['POST'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block['hash']
    data = request.get_json()
    new_block = blockchain.create_block(
        transactions=data['transactions'],
        previous_hash=previous_hash,
        fees=data['fees']
    )
    response = {
        'message': 'Block mined successfully',
        'block': new_block
    }
    return jsonify(response), 201

@app.route('/add_peer', methods=['POST'])
def add_peer():
    data = request.get_json()
    peer = data['peer']
    blockchain.add_peer(peer)
    blockchain.sync_chain()
    response = {
        'message': f'Peer {peer} added successfully!',
        'peers': list(blockchain.peers)
    }
    return jsonify(response), 201

@app.route('/peers', methods=['GET'])
def get_peers():
    response = {
        'peers': list(blockchain.peers)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    miner_thread = Thread(target=mine_automatically)
    miner_thread.daemon = True
    miner_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
