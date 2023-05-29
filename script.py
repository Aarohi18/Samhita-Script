from datetime import datetime
from datetime import timedelta
import json
from unittest import result

# from sqlalchemy import true
from web3 import Web3
import asyncio
import time
import schedule
import os
from dotenv import load_dotenv

load_dotenv()

provider_url = os.getenv("PROVIDER_URL")
my_address = os.getenv("PUBLIC_ADDRESS")
key = os.getenv("KEY")

web3 = Web3(Web3.HTTPProvider(provider_url))
samhita_address = "0x16ebae0D7673b9e3De6D21C38237708a0Af610Ee"
language_factory_address = "0x49cB4F263F16e09A84e95Ad608CF5b7f86d00fB8"
template_address = "0xe1C507d7b47b0D5446991a97CC98a124156F83Ca"

# samhita config
samhita_file = open("artifacts/contracts/Samhita.sol/Samhita.json")
samhita_data = json.load(samhita_file)
samhita_contract = web3.eth.contract(address=samhita_address, abi=samhita_data)

# language factory config
language_factory_file = open(
    "artifacts/contracts/LanguageDAOFactory.sol/LanguageDAOFactory.json"
)
language_factory_data = json.load(language_factory_file)
language_factory_contract = web3.eth.contract(
    address=language_factory_address, abi=language_factory_data
)

# language config
language_file = open("artifacts/contracts/LanguageDAO.sol/LanguageDAO.json")
language_data = json.load(language_file)

# template nft
template_file = open("artifacts/contracts/TemplateNFT.sol/TemplateNFT.json")
template_data = json.load(template_file)
template_contract = web3.eth.contract(address=template_address, abi=template_data)

chain_id = 199
nonce = web3.eth.get_transaction_count(my_address)


# this function is for the voting functionality of the samhita DAO
def samhita_voting():
    # get all the proposals of samhita DAO
    all_proposals = samhita_contract.functions.gateAllProposals().call()
    # print(all_proposals)
    for i in range(len(all_proposals)):
        # print(all_proposals[i])
        print(all_proposals[i])
        # print(time.time() > all_proposals[i][8])
        if all_proposals[i][9] == "pending":
            if time.time() > all_proposals[i][8]:
                samhita_get_decision(all_proposals[i][0])


# call the contract function for voting result
def samhita_get_decision(id):
    nonce = web3.eth.get_transaction_count(my_address)
    store_transaction = samhita_contract.functions.votingResult(id).build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gasPrice": web3.eth.gas_price,
        }
    )
    # sign txn.
    signed_store_txn = web3.eth.account.sign_transaction(
        store_transaction, private_key=key
    )
    # send txn.
    send_store_tx = web3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
    print(send_store_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(send_store_tx)
    print(tx_receipt)
    return


# this function is for the voting functionality of the language DAO
def language_voting():
    all_language_DAOs = language_factory_contract.functions.getAllDataDaos().call()
    # print(all_language_DAOs)
    for i in range(len(all_language_DAOs)):
        print(all_language_DAOs[i][3])

        # create the instance of the language DAO
        language_contract = web3.eth.contract(
            address=all_language_DAOs[i][3], abi=language_data
        )

        # get all the proposals of language DAO
        all_proposals = language_contract.functions.getAllProposals().call()
        # print(i)
        # print(all_proposals)
        for j in range(len(all_proposals)):
            print(all_proposals[j])
            if all_proposals[j][10] == "pending":
                if time.time() > all_proposals[j][8]:
                    t_id = template_contract.functions.proposalIdToTempId(
                        all_proposals[j][0]
                    ).call()
                    language_get_decision(
                        all_proposals[j][0],
                        t_id,
                        # all_proposals[j][9],
                        all_language_DAOs[i][3],
                    )


# call the contract function for voting result
def language_get_decision(id, template_id, address):
    language_contract = web3.eth.contract(address=address, abi=language_data)
    # print(contract)
    print(my_address)
    nonce = web3.eth.get_transaction_count(my_address)
    print(chain_id, nonce, my_address, web3.eth.gas_price)
    store_transaction = language_contract.functions.votingResult(
        id, template_id
    ).build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gasPrice": web3.eth.gas_price,
        }
    )

    # sign txn.
    signed_store_txn = web3.eth.account.sign_transaction(
        store_transaction, private_key=key
    )
    # send txn.
    send_store_tx = web3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
    print(send_store_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(send_store_tx)
    print(tx_receipt)
    return


samhita_voting()
language_voting()


# def sayHello():
#     print("Hello")
#     print(time.time())

schedule.every(60).minutes.do(samhita_voting)
schedule.every(60).minutes.do(language_voting)
while True:
    schedule.run_pending()
    time.sleep(1)
