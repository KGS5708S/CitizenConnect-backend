from web3 import Web3
import hashlib
import json

# Connect to local Hardhat node
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Replace with your deployed contract address
contract_address = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"

# Paste ABI here
abi =  [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "string",
          "name": "complaintId",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "dataHash",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "ComplaintStored",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_complaintId",
          "type": "string"
        }
      ],
      "name": "getComplaint",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_complaintId",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_dataHash",
          "type": "string"
        }
      ],
      "name": "storeComplaint",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

contract = w3.eth.contract(address=contract_address, abi=abi)


def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()


def store_on_blockchain(complaint_id, data_hash):
    tx = contract.functions.storeComplaint(
        complaint_id,
        data_hash
    ).transact({
        'from': w3.eth.accounts[0]
    })

    return tx.hex()


def verify_complaint(complaint_id, original_data):
    local_hash = generate_hash(original_data)

    blockchain_data = contract.functions.getComplaint(complaint_id).call()
    blockchain_hash = blockchain_data[1]

    return local_hash == blockchain_hash