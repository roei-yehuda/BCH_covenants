# covGen - Smart Contracts Generator for Bitcoin Cash
#### *covGen is a program for creation and management of smart contracts on Bitcoin Cash (BCH). Its command-line interface (CLI) allows the user to draft a smart contract, including covenants, compile it and then deploy it on the blockchain, as well as interact with it.*

![Teaser image](./pictures/logo-01.png)  

 **Dependencies:** 
![Python 3.6](https://img.shields.io/badge/python-3.6-green.svg?style=plastic)
![crypto_hashing 1.0.0](https://img.shields.io/badge/crypto_hashing-1.0.0-purple.svg?style=plastic)
![cashscript 0.4.0](https://img.shields.io/badge/cashscript-0.4.0-blue.svg?style=plastic)
![cashc_compiler ](https://img.shields.io/badge/cashc_compiler--blue.svg?style=plastic)
![TypeScript 9.0.0](https://img.shields.io/badge/TypeScript-9.0.0-blue.svg?style=plastic)
![node _](https://img.shields.io/badge/node--blue.svg?style=plastic)

## Introduction
Bitcoin contracts can restrict how much funds can be withdrawn from a contract, but as of today they cannot restrict who can withdraw those funds. Restricting what can be done with funds is what covenants are all about. A suggestion on how to implement covenants in bitcoin was presented in a paper titled ‘Bitcoin Covenants’ by Malte M¨oser, Ittay Eyal and Emin G¨un Sirer<sup>[1](https://maltemoeser.de/paper/covenants.pdf)</sup>. In order to make it work two new opcodes need to be added to the bitcoin operation codes.

In 2017 bitcoin cash (BCH) hard forked from bitcoin (BTC), the reason being opcodes. Two opcodes that enable covenants in bitcoin cash are OP_CHECKSIG and OP_CHECKDATASIG. The added expressiveness of these opcodes allow for more expressive smart contracts, including covenants, in the bitcoin cash blockchain. From now on everything we will be discussing will be in BTH.

Unlike with Ethereum contracts, in BTH contracts are not deployed on the blockchain but are defined by an cryptographed address unique to the contract. Funds can be sent to and received from the contract address. A contract contains functions with requirements, if all requirements are met, funds can be withdrawn from the contract.

BTH has two main high-level programming languages for smart contracts, Spedn and cashScript. This project compiles a users desired contract to cashScript and from cashScript to the opcodes. We chose to work with cashScript because it is closer in form to solidity and we have learnt to use solidity in class.

Our covGen offers an abstraction layer over cashScript and provides an easy interactive platform to create and deploy covenants on BTH. In addition, covGen hides away most of the necessary yet troublesome code in JavaScript used for deployment and interaction with BCH smart contracts.

## Description
The covGen is a command line interface run by python that generates covenants and smart contract for the bitcoin cash blockchain.
### Features:
 - **Smart contract creation:**\
 This aspect of the contract generator allows for a variety of restrictions 
   - **Operators:**\
   An *operator* of a function is someone who is allowed to use (call) it. 
   Their public key and signature will be verified upon calling the function.\
   If a function is composed solely of an operators restriction, then
   these operators may create a transaction that calls this function and spend the contract's funds freely.
   - **Recipients:**\
   A *recipient* of a function is someone that appears as one of the transaction's output.
   Recipients may be public keys (P2PKH) or a contract addresses (P2SH).
   If a PKH recipient is required to sign, it means that only a recipient can call this function.\
   If a function is composed solely of a recipients restriction, and without requiring their signatures, then anyone can create any transaction given that the output is (either one of, or all of) the pre-defined recipients.
     - Any or all: It is possible to allow any one of the recipients to get the funds, or demand that a withdrawal be divided equally between all recipients every time this function is called\
   - **Amount**\
   The amount of money in the transaction (in satoshis) can be restricted per transaction, per a recipient, or both.
   - **Time**\
    The time of the transaction can be restricted to be within a certain period
      - 'time' vs 'age':\
        It is possible to use either a relative time restriction (tx.age), or an absolute one (tx.time). 
        Note that due to limitations in the Bitcoin script time can only be used with the MIN option, age can be used with MIN or MAX.
        'time' and 'age' can be either a block number or a time stamp
      - 'min' vs 'max':\
        If min is defined, then the funds must be pulled after the TIME specified\
        If max is defined, the funds must be pulled before the TIME specified.

 - **Interaction with deployed contracts**

## Usage
After cloning this repo and installing all dependencies, run the covGen program through `python3 covGen.py`\
There are three global commands that can be called at any given moment for assistance:\
 - -h:\
 by calling '-h' you wil receive help on a global level, information about the global commands.
 - -i:\
 '-i' gives you information specific to the place in the code that it is called.
 - -exit:\
 '-exit' will exit the code and terminate the contract you are in the process of building.
 
## Examples
 **Example 1 - Joint account:**
 
 In this example our user will create a joint account where two public keys can have equal access to the funds in the contract.
 
 At first run you will encounter a bit of information as tips\
 ![Teaser image](./pictures/01_welcome_to_bch.png)

Then you will be asked to pick an option, would you like to create a new contract or make changes to an existing one.\
In this case we will pick 1 - ‘Create and compile a new smart contract’.\
![Teaser image](./pictures/02_first_thig_first.png)

Now you will be asked for four inputs to start the contract, all parameters have default values so you can just press ‘enter’.\
The parameters are:
 - A name for your contract, we will name our contract ‘JointSpending’, the default is ‘cov’.
 - cashScript pragma - From which cashScript version would you like your contract to run, we will just go with the default here by pressing ‘enter’.
 - Miner fee, in bitcoinCash the script will fail if the miner fee is too low. In optimised circumstances the miner fee would be calculated per byte,here we will go with the default.
 - A general comment about this function to assist in understanding what it is about.

![Teaser image](./pictures/03_first_thing_first.png)

The covenant contract is a combination of one or more functions. If the author of the transaction can fulfill all the requirements he or she can withdraw the requested amount.\
![Teaser image](./pictures/04_good_now.png)

For this particular covenant we would like to create one function that allows two different people to spend funds.\
![Teaser image](./pictures/05_new_func.png)

In order to achieve our goal we must add a restriction. In our case we would like to restrict the allowed operators of the spending function, there will be 2 in total.\
![Teaser image](./pictures/06_add_restriction.png)

We will now be asked if we’d like to add restrictions to this function. We do not. The program will now ask us if we’d like to add another function to this covenant. We do not.\
![Teaser image](./pictures/07_end_func.png)

We now have an option to compile the scripted to opcodes for further deployment in the bitcoin cash blockchain. For that we need to enter two file names, one for the cashScript file and one for the jason file.\
![Teaser image](./pictures/08_end_contract.png)

We get the output in both specified files ‘spendJcash.cash’ and ‘spendJjson.json’.\
The cash file looks as follows:
```
/*
This contract is an example of a joint spending account that can be placed on the Bitcoin Cash blockchain
*/

pragma cashscript ^0.4.0;

contract JointSpending(bytes20 operator_0_pkh_spend, bytes20 operator_1_pkh_spend){

	function spend(pubkey pk, sig s) {
		/*
		This function is a simple spending function that allows one of the two owners to withdraw funds
		*/
		// *** restrict operators
		require(hash160(pk) == operator_0_pkh_spend || hash160(pk) == operator_1_pkh_spend);
		require(checkSig(s, pk));
	}
}
```

And the json file looks like this:
```
{
  "contractName": "JointSpending",
  "constructorInputs": [
    {
      "name": "operator_0_pkh_spend",
      "type": "bytes20"
    },
    {
      "name": "operator_1_pkh_spend",
      "type": "bytes20"
    }
  ],
  "abi": [
    {
      "name": "spend",
      "covenant": false,
      "inputs": [
        {
          "name": "pk",
          "type": "pubkey"
        },
        {
          "name": "s",
          "type": "sig"
        }
      ]
    }
  ],
  "bytecode": "OP_2 OP_PICK OP_HASH160 OP_EQUAL OP_2 OP_PICK OP_HASH160 OP_ROT OP_EQUAL OP_BOOLOR OP_VERIFY OP_CHECKSIG",
  "source": "/*\r\nThis contract is an example of a joint spending account that can be placed on the Bitcoin Cash blockchain\r\n*/\r\n\r\npragma cashscript ^0.4.0;\r\n\r\ncontract JointSpending(bytes20 operator_0_pkh_spend, bytes20 operator_1_pkh_spend){\r\n\r\n\tfunction spend(pubkey pk, sig s) {\r\n\t\t/*\r\n\t\tThis function is a simple spending function that allows one of the two owners to withdraw funds\r\n\t\t*/\r\n\t\t// *** restrict operators\r\n\t\trequire(hash160(pk) == operator_0_pkh_spend || hash160(pk) == operator_1_pkh_spend);\r\n\t\trequire(checkSig(s, pk));\r\n\t}\r\n\r\n}\r\n",
  "networks": {},
  "compiler": {
    "name": "cashc",
    "version": "0.4.3"
  },
  "updatedAt": "2020-08-30T14:55:58.824Z"
}
```

You can see that the source contract (the cashScript contract) is very long were the bytecode is a short and exact script

**Example 2 - Joint account with amount limit:**\
In this example we will not go through all the steps.
We will create a similar contract to example 1 and add an additional function 'covenant' that limits the amount that the operator can withdraw and gives a time window in which the cold key operators can revoke the transaction.\
The new function is created in the in the interface as follows\
![Teaser image](./pictures/exp2_01_function2_Copy.png)

The contract generated in cashScript looks as follows with both function in place:
 ```
/*
This covenant is the second example, it has a cold function with no restriction and a hot function with time and amount restrictions
*/

pragma cashscript ^0.4.0;

contract Cold_w_Hot(bytes20 operator_0_pkh_JointSpend, bytes20 operator_1_pkh_JointSpend, bytes20 operator_0_pkh_covenant){

	function JointSpend(pubkey pk, sig s) {
		/*
		this is the joint account from example 1
		*/
		// *** restrict operators
		require(hash160(pk) == operator_0_pkh_JointSpend || hash160(pk) == operator_1_pkh_JointSpend);
		require(checkSig(s, pk));
	}

	function covenant(pubkey pk, sig s) {
		/*
		this is a hot key function that has limited spending and can be revoked by the cold key within the time window
		*/
		// *** restrict operators
		require(hash160(pk) == operator_0_pkh_covenant);
		require(checkSig(s, pk));
		// *** restrict amount
		int minerFee = 1000; // hardcoded fee
		int intTxVal = int(bytes(tx.value));
		// restrict amount per tx
		require(intTxVal <= 50000 + minerFee);
		// *** restrict time of tx
		require(tx.age >= weeks 1);
	}
}
```

And the json file looks like this:
```
{
  "contractName": "Cold_w_Hot",
  "constructorInputs": [
    {
      "name": "operator_0_pkh_JointSpend",
      "type": "bytes20"
    },
    {
      "name": "operator_1_pkh_JointSpend",
      "type": "bytes20"
    },
    {
      "name": "operator_0_pkh_covenant",
      "type": "bytes20"
    }
  ],
  "abi": [
    {
      "name": "JointSpend",
      "covenant": false,
      "inputs": [
        {
          "name": "pk",
          "type": "pubkey"
        },
        {
          "name": "s",
          "type": "sig"
        }
      ]
    },
    {
      "name": "covenant",
      "covenant": true,
      "inputs": [
        {
          "name": "pk",
          "type": "pubkey"
        },
        {
          "name": "s",
          "type": "sig"
        }
      ]
    }
  ],
  "bytecode": "OP_3 OP_PICK OP_0 OP_NUMEQUAL OP_IF OP_4 OP_PICK OP_HASH160 OP_EQUAL OP_4 OP_PICK OP_HASH160 OP_ROT OP_EQUAL OP_BOOLOR OP_VERIFY OP_2SWAP OP_CHECKSIG OP_NIP OP_NIP OP_ELSE OP_3 OP_ROLL OP_1 OP_NUMEQUALVERIFY OP_3 OP_PICK OP_SIZE 34 OP_SUB OP_SPLIT OP_NIP OP_8 OP_SPLIT OP_DROP OP_5 OP_PICK OP_HASH160 OP_4 OP_ROLL OP_EQUALVERIFY OP_2ROT OP_2DUP OP_SWAP OP_SIZE OP_1SUB OP_SPLIT OP_DROP OP_7 OP_ROLL OP_SHA256 OP_ROT OP_CHECKDATASIGVERIFY OP_CHECKSIGVERIFY e803 OP_SWAP OP_BIN2NUM 50c300 OP_ROT OP_ADD OP_LESSTHANOREQUAL OP_VERIFY OP_1 OP_CHECKSEQUENCEVERIFY OP_2DROP OP_DROP OP_1 OP_ENDIF",
  "source": "/*\r\nThis covenant is the second example, it has a cold function with no restriction and a hot function with time and amount restrictions\r\n*/\r\n\r\npragma cashscript ^0.4.0;\r\n\r\ncontract Cold_w_Hot(bytes20 operator_0_pkh_JointSpend, bytes20 operator_1_pkh_JointSpend, bytes20 operator_0_pkh_covenant){\r\n\r\n\tfunction JointSpend(pubkey pk, sig s) {\r\n\t\t/*\r\n\t\tthis is the joint account from example 1\r\n\t\t*/\r\n\t\t// *** restrict operators\r\n\t\trequire(hash160(pk) == operator_0_pkh_JointSpend || hash160(pk) == operator_1_pkh_JointSpend);\r\n\t\trequire(checkSig(s, pk));\r\n\t}\r\n\r\n\tfunction covenant(pubkey pk, sig s) {\r\n\t\t/*\r\n\t\tthis is a hot key function that has limited spending and can be revoked by the cold key within the time window\r\n\t\t*/\r\n\t\t// *** restrict operators\r\n\t\trequire(hash160(pk) == operator_0_pkh_covenant);\r\n\t\trequire(checkSig(s, pk));\r\n\t\t// *** restrict amount\r\n\t\tint minerFee = 1000; // hardcoded fee\r\n\t\tint intTxVal = int(bytes(tx.value));\r\n\t\t// restrict amount per tx\r\n\t\trequire(intTxVal <= 50000 + minerFee);\r\n\t\t// *** restrict time of tx\r\n\t\trequire(tx.age >= weeks 1);\r\n\t}\r\n\r\n}\r\n",
  "networks": {},
  "compiler": {
    "name": "cashc",
    "version": "0.4.3"
  },
  "updatedAt": "2020-08-31T08:56:30.416Z"
}
```
## References  
[‘Bitcoin Covenants’](https://maltemoeser.de/paper/covenants.pdf)\
[Smart contracts on Ethereum, Bitcoin and Bitcoin Cash](https://kalis.me/smart-contracts-eth-btc-bch/)\
[CashScript - Smart contracts for Bitcoin Cash](https://cashscript.org/)\
[BCH Covenants with Spedn](https://read.cash/@pein/bch-covenants-with-spedn-c1170a02)
## Disclaimer
This project is a school project at the ‘Hebrew University in Jerusalem’.
The authors do not take responsibility for any malfunction or damage that may occur from a covenant generated in this platform.
Be smart and be careful!
##### Contact us:
roei.yehuda@mail.huji.ac.il\
avigail.suna@mail.huji.ac.il




