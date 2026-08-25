# Odoo Garage Blockchain

![Odoo](https://img.shields.io/badge/Odoo-17.0-purple.svg)
![Blockchain](https://img.shields.io/badge/Network-Ethereum_Sepolia-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)

A custom Odoo module for auto repair shops. It tracks mechanics, vehicles, and repair jobs, and it anchors every finished repair on the Ethereum blockchain (Sepolia testnet). This creates a tamper-proof record of each repair invoice.

## Why This Project

Garage records can get lost, edited, or disputed. A customer may question if a repair was done, or a shop may need proof of service history for a warranty claim. This module solves that problem. Once a repair is closed, the system creates a cryptographic fingerprint of the repair data and sends it to a public blockchain. Anyone can then check that the record has not changed.

## Key Features

- **Garage management**: register mechanics, vehicles, and repair orders in one place.
- **Kanban board**: view all repairs by status (new, in progress, done) at a glance.
- **Cryptographic proof**: each repair generates a SHA-256 hash from its data (car, mechanic, parts, cost, date).
- **Blockchain anchoring**: the hash is sent as a transaction on the Ethereum Sepolia testnet.
- **Public traceability**: each repair record links directly to its transaction on Etherscan, so anyone can verify it.

## How the Blockchain Anchoring Works

1. A mechanic closes a repair order in Odoo.
2. The module builds a SHA-256 hash from the repair details.
3. The module sends this hash to the Sepolia test network as a transaction.
4. Odoo stores the transaction hash and shows a link to Etherscan on the repair form.
5. Anyone with that link can confirm the repair data has not been altered, because changing even one character in the original data changes the hash completely.

This does not store the repair data itself on the blockchain. It stores proof that the data existed in that exact form at that exact time.

## Tech Stack

- **Odoo 17** – ERP framework for the garage management logic
- **Python** – custom module backend
- **Web3 / Ethereum Sepolia testnet** – blockchain anchoring
- **PostgreSQL** – Odoo's database
- **Docker & Docker Compose** – environment setup

## Example: Verified Transaction

A real repair record from this project was anchored here:

- **Transaction hash**: `0xb8125677a3f97553e8b6171f5547ef37f8fee0c85d67b60fb7187e39cb594c5`
- **View it on Etherscan**: [Sepolia Etherscan](https://sepolia.etherscan.io/tx/b8125677a3f9f7553e8b6171f5547ef37f8fee0c85d67b60fb7187e39cb594c5)

## Project Structure

```
odoo-custom-auto-repair/
└── auto_repair_blockchain/     # the custom Odoo module
    ├── models/                 # mechanic, vehicle, repair, blockchain logic
    ├── views/                  # forms, kanban board, menus
    └── __manifest__.py         # module definition and dependencies
```

## Installation

You need Docker and Docker Compose installed.

```bash
# 1. Clone the repository
git clone https://github.com/Soukaina009/odoo-custom-auto-repair.git
cd odoo-custom-auto-repair

# 2. Start the Odoo and PostgreSQL containers
docker compose up -d

# 3. Install or update the module
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d postgres -u garage_blockchain --stop-after-init

# 4. Restart the Odoo service
docker compose restart odoo
```

Odoo runs at `http://localhost:8069` once the containers are up.

## Usage

1. Log in to Odoo and open the **Garage** app.
2. Add a mechanic and a vehicle.
3. Create a repair order and link it to a mechanic and a vehicle.
4. Add the parts and labor cost, then mark the repair as **Done**.
5. Odoo generates the hash and sends the blockchain transaction automatically.
6. Open the repair form to see the transaction hash and the Etherscan link.

## Notes

This project uses the Sepolia testnet, which is free and made for testing. It does not use real funds. Moving this to Ethereum mainnet would need a funded wallet and small transaction fees.

## Author

Built by **Zemzam Soukaina**, Master's student in AI for the Digital Economy and Management.
[GitHub](https://github.com/Soukaina009) · [LinkedIn](https://www.linkedin.com/in/soukaina-zemzam-585b8a3aa/?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base%3BEMOBq%2F32RqGeLJ3s2tgDYQ%3D%3D) · [Email](https://accounts.google.com/SignOutOptions?hl=en&continue=https://mail.google.com/mail&service=mail&ec=GBRAFw)
