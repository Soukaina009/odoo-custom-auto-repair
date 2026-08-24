// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title GarageRegistry
 * @notice Stocke une preuve d'immuabilité (hash) pour chaque réparation garage.
 * @dev Déployé sur Polygon Amoy Testnet.
 */
contract GarageRegistry {
    address public owner;

    /// @notice Mapping id_reparation => hash SHA-256 des données de la réparation
    mapping(uint256 => string) public reparations;

    event ReparationEnregistree(uint256 indexed idReparation, string hashDonnees, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Seul le proprietaire peut appeler cette fonction");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Enregistre le hash d'une réparation sur la blockchain.
     * @param _idReparation  Identifiant Odoo de la réparation (garage.reparation id)
     * @param _hashDonnees   Hash SHA-256 des données de la réparation
     */
    function enregistrerReparation(uint256 _idReparation, string calldata _hashDonnees) external onlyOwner {
        require(bytes(_hashDonnees).length > 0, "Le hash ne peut pas etre vide");
        require(bytes(reparations[_idReparation]).length == 0, "Reparation deja enregistree");

        reparations[_idReparation] = _hashDonnees;

        emit ReparationEnregistree(_idReparation, _hashDonnees, block.timestamp);
    }

    /**
     * @notice Vérifie le hash stocké pour une réparation donnée.
     * @param _idReparation  Identifiant Odoo de la réparation
     * @return Le hash stocké sur la blockchain
     */
    function getHashReparation(uint256 _idReparation) external view returns (string memory) {
        return reparations[_idReparation];
    }
}
