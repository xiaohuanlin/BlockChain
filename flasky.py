from flask import Flask, jsonify, request
from uuid import uuid4
from chain import BlockChain

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

blockchain = BlockChain()

@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof of work algo to get next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Give the reward
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    block = blockchain.new_block(proof)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transactions():

    values = request.form

    # Check the required fields data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    # Create new transaction
    index = blockchain.new_transaction(**values)

    response = {
        'message': 'Transaction will be added to Block {}'.format(index),
    }
    return jsonify(response), 201


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form

    nodes = values.get('nodes').split(',')

    if not nodes:
        return 'Error: Please supply a valid list of nodes', 400

    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authritative',
            'new_chain': blockchain.chain
        }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)