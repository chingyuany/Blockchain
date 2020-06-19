import hashlib
import json
import sys
import os
import ecdsa
import random
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from time import time

# *************Class Block related****************


class block:
    def __init__(self, transaction, prev_hash):
        self.MagicNumber = 0xD9B4BEF9
        self.version = 1
        self.previous_block_hash = prev_hash
        self.merkleRoot = self.generate_merkleRoot(transaction)
        self.timestamp = time()
        self.Difficulty_target = 1
        self.nonce = random.randint(0, 9999)
        self.block_size = self.calculate_blockSize()
        self.transaction_counter = 1
        self.transaction = transaction

    def printBlock(self):
        print("Magic Number:\t"+str(self.MagicNumber) +
              "\nBlock_size:\t" + str(self.block_size) +
              "\nVersion:\t"+str(self.version) +
              "\nPrevious block hash:\t" + str(self.previous_block_hash) +
              "\nMerkleRoot:\t" + str(self.merkleRoot) +
              "\nTimestamp:\t" + str(self.timestamp) +
              "\nDifficulty_target:\t" + str(self.Difficulty_target) +
              "\nNonce:\t" + str(self.nonce) +
              "\nTransaction_counter:\t" + str(self.transaction_counter) +
              "\n--------Transcation List:------"
              )
        self.transaction[0].print_trans()

    # 	Create a Merkle tree for the transactions
    def generate_merkleRoot(self, transaction):
        storeHash = []
        for k in range(len(transaction)):
            storeHash.append(self.hash(transaction[k].wholetrans()))
        if (len(storeHash) % 2 != 0):
            storeHash.append(storeHash[-1])
        while (len(storeHash) > 1):
            j = 0
            for i in range(0, len(storeHash) - 1, 2):
                storeHash[j] = self.hash(
                    str(storeHash[i]) + str(storeHash[i+1]))
                j += 1
            lastDelete = len(storeHash) / 2
            del storeHash[int(lastDelete):]
        return storeHash[0]

    def calculate_blockSize(self):
        return sys.getsizeof(self.version)+sys.getsizeof(self.previous_block_hash)+sys.getsizeof(self.merkleRoot)+sys.getsizeof(self.timestamp)+sys.getsizeof(self.Difficulty_target)+sys.getsizeof(self.nonce)

    def hash(self, data):
        string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(string).hexdigest()

    def hash_thisblock(self):
        block = str(self.version)+str(self.previous_block_hash) + \
            str(self.merkleRoot)+str(self.timestamp) + \
            str(self.Difficulty_target)+str(self.nonce)
        return self.hash(block)

    def get_prevhash(self):
        return self.previous_block_hash

    def changeblock(self, data):
        self.merkleRoot = data


class Blockchain:
    def __init__(self, genesis_transaction):
        self.blockchain = []
        self.genesisblock(genesis_transaction)

    def genesisblock(self, genesis_transaction):
        self.addBlock(block(genesis_transaction, -1))

    def addBlock(self, block):
        self.blockchain.append(block)

    def validation(self):
        for i in range(len(self.blockchain)):
            current_block = self.get_block(i)
            previous_block = self.get_block(i-1)
            # validate previous hash
            if(i != 0 and current_block.previous_block_hash != previous_block.hash_thisblock()):
                return "validation false! Block "+str(i)+" previous hash is"+current_block.get_prevhash()+" Block "+str(i-1)+" 's hash is"+previous_block.hash_thisblock()
            # validate merkleroot and transactions
            if(current_block.generate_merkleRoot(current_block.transaction) != current_block.merkleRoot):
                return "validation false! Block "+str(i)+" recaluate transactions' merkleRoot is "+str(current_block.generate_merkleRoot(current_block.transaction))+" Block "+str(i)+" 's merkleRoot is "+str(current_block.merkleRoot)
        return "\nAll the blocks validate successfully"

    def last_block(self):
        return self.blockchain[-1]

    def get_block(self, num):
        return self.blockchain[num]

# *************Class Transaction related****************


class transaction:
    def __init__(self):
        self.version = 1
        self.locktime = 0

    def genernate_input(self, inputs):
        vin = []
        for i in range(len(inputs)):
            txid = inputs[i]['txid']
            vout = inputs[i]['vout']
            signature = inputs[i]['signature']
            publickey = inputs[i]['publickey']
            vin.append({'txid': txid, 'vout': vout, 'ScriptSigsize': sys.getsizeof(signature)+sys.getsizeof(publickey),
                        'ScriptSig': {'signature:': signature, 'public_key': publickey},
                        'Sequenceno': 'FFFFFFFF'})
        self.vin = vin
        self.input_count = len(vin)

    def genernate_output(self, outputs):
        vout = []

        for i in range(len(outputs)):
            value = outputs[i]['value']
            ScriptPubKey = outputs[i]['ScriptPubKey']
            vout.append({'value': value, 'ScriptPubKey_Size': 32,
                         'ScriptPubKey': ScriptPubKey})
        self.vout = vout
        self.output_count = len(vout)

    def hash(self, data):
        string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(string).hexdigest()

    def wholetrans(self):
        return str(self.version)+str(self.locktime) + \
            str(self.vin)+str(self.input_count) + \
            str(self.vout)+str(self.output_count)

    def hashthistrans(self):
        this_transaction = self.wholetrans()
        this_transaction = self.hash(self.hash(this_transaction))
        this_transaction_byte = bytes.fromhex(this_transaction)
        bytearray(this_transaction_byte).reverse()
        return this_transaction_byte

    def print_trans(self):
        print("version:\t"+str(self.version) +
              "\nlocktime:\t" + str(self.locktime) +
              "\nvin:\t" + str(self.vin) +
              "\ninput_count:\t" + str(self.input_count) +
              "\nvout:\t" + str(self.vout) +
              "\noutput_count:\t" + str(self.output_count)
              )
        print("-----end of transaction list-----")

    def validationofTXID(self, prev_trans):
        prev_transaction = self.hash(self.hash(prev_trans))
        prev_transaction_byte = bytes.fromhex(prev_transaction)
        bytearray(prev_transaction_byte).reverse()
        return self.vin[0]['txid'] == prev_transaction_byte

    def verify_pubkey_address(self, prev_vout_pubkey):
        this_vin_pubkey = self.hash_pub_key(
            self.vin[0]['ScriptSig']['public_key'])
        return this_vin_pubkey == prev_vout_pubkey

    def hash_pub_key(self, pubkey):
        publickeyhash = self.hash(self.hash(pubkey))
        publickeyhash_byte = bytes.fromhex(publickeyhash)
        bytearray(publickeyhash_byte).reverse()
        return publickeyhash_byte


class keypair:
    def __init__(self, user):
        self.user = str(user)
        fileName = "user"+self.user+"_private.pem"
        self.privatekeyfile = fileName
        file = open(fileName, 'r')
        privatekey = file.read().split("\n")
        privatekey = privatekey[1]+privatekey[2]+privatekey[3]
        self.privatekey = privatekey
        file.close()
        fileName = "user"+self.user+"_public.pem"
        self.publickeyfile = fileName
        file = open(fileName, 'r')
        publickey = file.read().split("\n")
        publickey = publickey[1]+publickey[2]
        self.publickey = publickey
        file.close()

    def hash_pub_key(self):
        publickeyhash = self.hash(self.hash(self.publickey))
        publickeyhash_byte = bytes.fromhex(publickeyhash)
        bytearray(publickeyhash_byte).reverse()
        return publickeyhash_byte

    def hash(self, data):
        string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(string).hexdigest()

    def signature(self, data):
        data = str.encode(data)
        with open(self.privatekeyfile) as f:
            sk = SigningKey.from_pem(f.read(), hashlib.sha256)
        new_signature = sk.sign_deterministic(data, sigencode=sigencode_der)

        self.signaturefilename = "user"+self.user+"_signature.sig2"
        with open(self.signaturefilename, "wb") as f:
            f.write(new_signature)
            f.close()
        return new_signature

    def verify_signature(self, data):
        data = str.encode(data)
        with open(self.publickeyfile) as f:
            vk = VerifyingKey.from_pem(f.read())
            f.close()
        with open(self.signaturefilename, "rb") as f:
            signature = f.read()
            f.close()
        return vk.verify(signature, data, hashlib.sha256, sigdecode=sigdecode_der)


# generates 6 keypairs/Users
print("Generating 6 keypairs/Users ...")
for i in range(1, 7):
    user = 'user'+str(i)
    os.system('openssl ecparam -genkey -name secp256k1 -noout -out ' +
              user+'_private.pem')
    os.system('openssl ec -in '+user +
              '_private.pem -pubout -out '+user+'_public.pem')

# read key pair list and generate pubkey hash list
userkeypair_list = []
user_pubkey_hash_list = []
for i in range(6):
    userkeypair_list.append(keypair(i+1))
    user_pubkey_hash_list.append(userkeypair_list[i].hash_pub_key())

# create genesis_transaction
transaction_pool = []
transaction1 = transaction()
inputs = [{'txid': -1, 'vout': -1, 'signature': 0, 'publickey': 0}]
transaction1.genernate_input(inputs)

outputs = [{'value': 10, 'ScriptPubKey': user_pubkey_hash_list[0]},
           {'value': 90, 'ScriptPubKey': user_pubkey_hash_list[1]}]
transaction1.genernate_output(outputs)
# print('This is genesis transaction 1')
# transaction1.print_trans()
transaction_pool.append(transaction1)
# UTXO pool : unspent transaction outputs
UTXO_pool = []
UTXO_pool.append(outputs)

# Create genesis block
transactions = []
transactions.append(transaction_pool[0])
blockchain = Blockchain(transactions)

print("\nFinished genesis transaction 1 and added to Genesis Block 1")

n = 6
print("\nVerifying other new Transactions...")
for m in range(1, n):
    # traverse transaction pool to find pre_trans's output address match current user address
    current_address = user_pubkey_hash_list[m]
    for u in range(len(transaction_pool)):
        for r in range(len(transaction_pool[u].vout)):
            if transaction_pool[u].vout[r]['ScriptPubKey'] == current_address:
                txid = transaction_pool[u].hashthistrans()
                prev_transaction = transaction_pool[u].wholetrans()
    # generate new transaction
    transaction_pool.append(transaction())
    # put input to transaction
    inputs = [{'txid': txid, 'vout': 1, 'signature': userkeypair_list[m].signature(prev_transaction),
               'publickey': userkeypair_list[m].publickey}]
    transaction_pool[m].genernate_input(inputs)
    print('\nThis is transaction ', m+1, 'verifying..')
    # Provide within the program verification that each cryptographic primitive is being done correctly
    # verify transaction's input is correct, you can try below comment out command to check the validation function is work or not
    # prev_transaction = "wrong trans"
    if (userkeypair_list[m].verify_signature(prev_transaction)):
        print('signautre is vailed')
    else:
        print('signature invailed')
    # prev_transaction = "wrong trans"
    if (transaction_pool[m].validationofTXID(prev_transaction)):
        print('verify txid successful')
    else:
        print('verify txid failed')
    # transaction_pool[m].verify_pubkey_address("wrong public key address")
    if (transaction_pool[m].verify_pubkey_address(transaction_pool[m-1].vout[1]['ScriptPubKey'])):
        print('verify public key address successful')
    else:
        print('verify public key address failed')

    curr_address = transaction_pool[m].hash_pub_key(
        transaction_pool[m].vin[0]['ScriptSig']['public_key'])
    wallet = 0
    # traverse UTXO pool to calculate how much money I have
    for i in range(len(UTXO_pool)):
        for j in range(len(UTXO_pool[i])):
            if (UTXO_pool[i][j]['ScriptPubKey'] == curr_address):
                wallet += UTXO_pool[i][j]['value']
    send_other_money = 90 - (10 * m)
    send_myself_money = 10
    # print("send out money",send_other_money + send_myself_money)
    # check if Current user have enough money from the pool
    if wallet >= send_other_money + send_myself_money:
        # remove input from UTXO_pool : unspent transaction outputs
        for i in range(len(UTXO_pool)):
            for j in range(len(UTXO_pool[i])):
                if (UTXO_pool[i][j]['ScriptPubKey'] == curr_address):
                    del UTXO_pool[i][j]
        # if not final transaction
        if m != n-1:
            # generate output to transaction
            outputs = [{'value': send_myself_money, 'ScriptPubKey': user_pubkey_hash_list[m]},
                       {'value': send_other_money, 'ScriptPubKey': user_pubkey_hash_list[m+1]}]
            transaction_pool[m].genernate_output(outputs)
            UTXO_pool.append(outputs)
        # if this is final transaction, send money to user1
        else:
            outputs = [{'value': send_myself_money, 'ScriptPubKey': user_pubkey_hash_list[m]},
                       {'value': send_other_money, 'ScriptPubKey': user_pubkey_hash_list[0]}]
            transaction_pool[m].genernate_output(outputs)
            UTXO_pool.append(outputs)
    else:
        print('You donot have enough money to send')

    # transaction_pool[m].print_trans()


# Add set of five blocks to the genesis block
    transactions = []
    transactions.append(transaction_pool[m])
    previouse_hash = blockchain.last_block().hash_thisblock()
    blockchain.addBlock(block(transactions, previouse_hash))
    print("finished transaction ", m+1, " and added to Block ", m+1)
# print all the blocks
print("\nBelow are all the Blocks infomation")
for k in range(n):
    print("\nBlock "+str(k+1))
    blockchain.get_block(k).printBlock()

# Provide within the program verification that each cryptographic primitive is being done correctly
# blockchain.blockchain[1].timestamp = time()
# blockchain.blockchain[0].transaction = 'wrong transaction'
print(blockchain.validation())


# check every user's money
wallet_list = [0]*n
print("\nBelow is every users' money after all the transactions records to the block chain")
for m in range(n):
    curr_address = user_pubkey_hash_list[m]
    for i in range(len(UTXO_pool)):
        for j in range(len(UTXO_pool[i])):
            if (UTXO_pool[i][j]['ScriptPubKey'] == curr_address):
                wallet_list[m] += UTXO_pool[i][j]['value']
    print("user ", m, "'s money = ", wallet_list[m])
# print('utxo pool = ', UTXO_pool)
