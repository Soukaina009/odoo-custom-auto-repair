# 🚗 Odoo Garage Blockchain

[![Odoo](https://img.shields.io/badge/Odoo-17.0-purple.svg)](https://www.odoo.com/)
[![Blockchain](https://img.shields.io/badge/Network-Ethereum_Sepolia-blue.svg)](https://sepolia.etherscan.io/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED)](https://www.docker.com/)

Module Odoo sur-mesure de gestion d'atelier automobile intégrant l'**ancrage et la certification immuable des réparations sur la blockchain Ethereum (Sepolia Testnet)**.

---

## ✨ Fonctionnalités Clés

* **Gestion d'Atelier** : Suivi complet des véhicules, affectation des mécaniciens et vue Kanban des réparations.
* **Certification Cryptographique** : Génération d'un hash d'intégrité SHA-256 pour chaque intervention.
* **Ancrage Ethereum** : Envoi de la transaction sur le réseau Sepolia pour garantir l'anti-falsification de l'historique d'entretien.
* **Traçabilité Publique** : Lien direct vers l'explorateur Etherscan depuis la fiche Odoo.

---

## 📸 Aperçu du Projet

<p align="center">
  <b>1. Vue Kanban des Réparations</b><br>
  <img width="1915" height="702" alt="kanban" src="https://github.com/user-attachments/assets/7141e20b-a2e9-4c30-acb1-843f82146dd2" />


<p align="center">
  <b>2. Fiche Réparation & Preuve Blockchain</b><br>
  <img width="1341" height="658" alt="form_blockchain" src="https://github.com/user-attachments/assets/09ccf7ab-206f-4223-95d1-9914b30c231d" />


<p align="center">
  <b>3. Validation sur Sepolia Etherscan</b><br>
  <img width="1333" height="607" alt="etherscan" src="https://github.com/user-attachments/assets/32891486-7ce0-4890-b405-65e89d63af82" />


---

## 🔗 Transaction Certifiée (Testnet)

* **Transaction Hash :** `0xb8125677a3f97553e8b6171f5547ef37f8fee0c85d67b60fb7187e39cb594c5`
* **Explorateur :**[Consulter la transaction sur Sepolia Etherscan](https://sepolia.etherscan.io/tx/b8125677a3f9f7553e8b6171f5547ef37f8fee0c85d67b60fb7187e39cb594c5)

---

## 🚀 Démarrage Rapide

```bash
# 1. Lancer l'environnement Docker
docker compose up -d

# 2. Installer / Mettre à jour le module Odoo
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d postgres -u garage_blockchain --stop-after-init

# 3. Redémarrer le service Odoo
docker compose restart odoo
