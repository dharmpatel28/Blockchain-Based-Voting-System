from web3 import Web3

# Connect to local Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Contract Details
contract_address = web3.toChecksumAddress('0x7C1E970A0057ae893adF8BfF1deFdf8eaF754891')
with open('contract/Election_abi.json') as f:
    contract_abi = f.read()

contract = web3.eth.contract(address=contract_address, abi=contract_abi)