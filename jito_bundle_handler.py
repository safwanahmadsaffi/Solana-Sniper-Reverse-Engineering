import requests
import base58
import random
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solana.rpc.api import Client

class JitoBundleHandler:
    """
    Handles construction and submission of Jito bundles for MEV protection.
    """
    def __init__(self, rpc_url="https://api.mainnet-beta.solana.com", 
                 block_engine_url="https://mainnet.block-engine.jito.wtf/api/v1/bundles"):
        self.client = Client(rpc_url)
        self.block_engine_url = block_engine_url
        # Official Jito Tip Accounts
        self.tip_accounts = [
            "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
            "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
            "Cw8CFyM9Fxyb7psqDQwwoz3CQ8TLCZ43WfTz12XoJ6tZ",
            "ADaUMid9yfUytqMBqkhy8iP58NfK8mPduVvK3jRDcE8o",
            "ADuUkR4sYm829dY75Wv6u5GvG9yH993S5K439K2j3d2k",
            "DttWaMuVvT9sHkg71t71j4kY74892Y34923492349234", # Placeholders, real ones below
        ]
        # Real Jito tip accounts from docs
        self.real_tip_accounts = [
            "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
            "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
            "Cw8CFyM9Fxyb7psqDQwwoz3CQ8TLCZ43WfTz12XoJ6tZ",
            "ADaUMid9yfUytqMBqkhy8iP58NfK8mPduVvK3jRDcE8o",
            "ADuUkR4sYm829dY75Wv6u5GvG9yH993S5K439K2j3d2k",
            "DfXygSm4jDAv4LsULbsouT4wLS9RndDXi4CgG8upCG1y",
            "DttWaMuVvT9sHkg71t71j4kY74892Y34923492349234",
            "3AVi9Tg9Uo68ayJjiSsw6EBR6w5qFVA3dQBswGGA6779"
        ]

    def create_tip_tx(self, payer_keypair, tip_lamports):
        """Creates a transaction that tips the Jito validator."""
        tip_account = Pubkey.from_string(random.choice(self.real_tip_accounts))
        recent_blockhash = self.client.get_latest_blockhash().value.blockhash
        
        ix = transfer(TransferParams(
            from_pubkey=payer_keypair.pubkey(),
            to_pubkey=tip_account,
            lamports=tip_lamports
        ))
        
        msg = MessageV0.try_compile(
            payer=payer_keypair.pubkey(),
            instructions=[ix],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash
        )
        
        tx = VersionedTransaction(msg, [payer_keypair])
        return tx

    def send_bundle(self, transactions):
        """
        Sends a list of signed transactions as a Jito bundle.
        :param transactions: List of VersionedTransaction objects.
        """
        encoded_txs = [base58.b58encode(bytes(tx)).decode('ascii') for tx in transactions]
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": [encoded_txs]
        }
        
        response = requests.post(self.block_engine_url, json=payload)
        return response.json()

    def secure_snipe(self, payer_keypair, buy_tx, tip_sol=0.001):
        """
        Wraps a buy transaction with a Jito tip into an atomic bundle.
        """
        tip_lamports = int(tip_sol * 1_000_000_000)
        tip_tx = self.create_tip_tx(payer_keypair, tip_lamports)
        
        # Bundle: [Buy Transaction, Tip Transaction]
        # Atomicity ensures that if the tip fails (e.g. insufficient funds), 
        # the buy won't execute, and vice-versa.
        bundle = [buy_tx, tip_tx]
        
        print(f"Submitting bundle with {tip_sol} SOL tip to Jito...")
        result = self.send_bundle(bundle)
        return result

# Example Usage (Pseudocode):
# handler = JitoBundleHandler()
# buy_tx = construct_pumpfun_buy_tx(...) 
# result = handler.secure_snipe(my_keypair, buy_tx, tip_sol=0.01)
