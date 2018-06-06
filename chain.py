import hashlib
import json
from time import time
from urllib.parse import urlparse

import requests


class BlockChain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        # Create new chain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transaction': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        return block
    
    def new_transaction(self, sender, recipient, amount):
        # Add new transaction to the list
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1
    
    def register_node(self, address):
        # Add the IP of new node to the list of nodes
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    @property
    def last_block(self):
        # Return the last block of the chain
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Make the Dict orderable
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        # Give the previous POW
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        # Check if the proof is right
        guess = '{}{}'.format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'
    
    def valid_chain(self, chain):
        # Determine if a given blockchain is valid
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print('{}'.format(last_block))
            print({}.format(block))
            print('\n'+ '-'*10 + '\n')
            # Check the hash if the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # Check the Proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # Only looking for chains longer than ours
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get('http://{}/chain'.format(node))

            if requests.status_codes == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discoverd a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        
        return False
