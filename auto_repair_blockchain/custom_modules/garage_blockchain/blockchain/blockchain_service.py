import hashlib
import json
import logging
import os
from pathlib import Path

_logger = logging.getLogger(__name__)

try:
    from web3 import Web3
except ImportError:
    Web3 = None
    _logger.warning("web3 n'est pas installé. pip install web3")

try:
    from dotenv import load_dotenv
    # Charger le .env situé dans le dossier blockchain/ du module
    _env_path = Path(__file__).resolve().parent / '.env'
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    _logger.warning("python-dotenv n'est pas installé. pip install python-dotenv")


def _get_env(key: str) -> str:
    """Récupère une variable d'environnement ou lève une erreur claire."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"La variable d'environnement '{key}' est manquante. "
            f"Vérifiez votre fichier .env dans le dossier blockchain/ du module."
        )
    return value


def get_web3() -> "Web3":
    """Retourne une instance Web3 connectée au provider RPC."""
    if Web3 is None:
        raise ImportError("La bibliothèque web3 n'est pas installée : pip install web3")

    rpc_url = _get_env('BLOCKCHAIN_RPC_URL')
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise ConnectionError(f"Impossible de se connecter au provider RPC : {rpc_url}")

    _logger.info("Connecté au réseau Blockchain (chainId=%s)", w3.eth.chain_id)
    return w3


def get_contract(w3: "Web3"):
    """Charge le contrat GarageRegistry à partir de l'ABI et de l'adresse."""
    contract_address = _get_env('BLOCKCHAIN_CONTRACT_ADDRESS')
    abi_path = Path(__file__).resolve().parent / 'GarageRegistry_abi.json'

    if not abi_path.exists():
        raise FileNotFoundError(f"Fichier ABI introuvable : {abi_path}")

    with open(abi_path, 'r') as f:
        abi = json.load(f)

    return w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=abi,
    )


def compute_reparation_hash(record) -> str:
    """
    Calcule un hash SHA-256 déterministe des données clés de la réparation.
    Le hash servira de preuve d'immuabilité sur la blockchain.
    """
    data = {
        'id': record.id,
        'voiture': record.voiture_id.name or '',
        'mecanicien': record.mecanicien_id.name or '',
        'type_reparation': record.type_reparation or '',
        'description': record.description or '',
        'date_debut': str(record.date_debut) if record.date_debut else '',
        'date_fin': str(record.date_fin) if record.date_fin else '',
        'cout_total': str(record.cout_total),
        'pieces_utilisees': record.pieces_utilisees or '',
        'state': record.state or '',
    }
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def enregistrer_sur_blockchain(record_id: int, data_hash: str) -> str:
    """
    Envoie une transaction au smart contract pour enregistrer le hash.

    :param record_id: ID Odoo de la réparation
    :param data_hash: Hash SHA-256 des données
    :return: Transaction hash (hex string)
    """
    w3 = get_web3()
    contract = get_contract(w3)

    private_key = _get_env('BLOCKCHAIN_PRIVATE_KEY')
    chain_id = int(_get_env('BLOCKCHAIN_CHAIN_ID'))
    account = w3.eth.account.from_key(private_key)

    # Construire la transaction
    tx = contract.functions.enregistrerReparation(
        record_id,
        data_hash,
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gasPrice': w3.eth.gas_price,
        'chainId': chain_id,
    })

    # Signer et envoyer
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    _logger.info(
        "Transaction blockchain envoyée — reparation_id=%s, tx_hash=%s",
        record_id, tx_hash.hex(),
    )

    # Attendre la confirmation (timeout 120s)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    _logger.info(
        "Transaction confirmée — block=%s, status=%s",
        receipt.blockNumber, receipt.status,
    )

    if receipt.status != 1:
        raise RuntimeError("La transaction blockchain a échoué (status=0).")

    return tx_hash.hex()
