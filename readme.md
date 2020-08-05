# Blockchain_Bitcoin
BlockChain.py is to simulate the BlockChain and Bitcoin transaction for different users.  

•	The program will creating elliptic curve (EC) public key pairs for six different users first.  
•	Create transactions for the 6 users.  
•	Create a Merkle tree for the transactions.  
•	Create genesis block.  
•	Add set of five blocks to the genesis block.  
•	Provide within the program verification that each cryptographic primitive is being done correctly.  

Instruction for the installation  
step1 install OpenSSL  
step2 chmod a+x install.sh  
step3 ./install.sh  
step4 python3.6 BlockChain.py  

PoS.py is a “modified” PoS-based voting algorithm
•	There are 10 validators in the system
•	The checkpoint tree is a full binary tree
•	 Each node/checkpoint in the checkpoint tree has a number associated with it. Given a
node of number 𝑛, its left child is 2𝑛 + 1, and its right child is 2𝑛 + 2. The root node is
labeled 0.
•	The length of the link contained in each vote is always 1. This means a validator cannot
skip any checkpoint in its vote, i.e., the target of the link is either the left child or the
right child of the source. (Note: in the real Casper FFG, a vote can skip some
checkpoints. An example is given on page 27 of the slides, where link 𝑏! → 𝑏" skips two
checkpoints.)
•	For each vote, the probability of selecting the left child as the target is the same as the
probability of selecting the right child.
•	If the sum of the deposits of the nodes voting for a link L exceeds 1/2 of the total deposit,
L is the supermajority link. (Note: this is different from the 2/3 rule used in real Casper
FFG.)