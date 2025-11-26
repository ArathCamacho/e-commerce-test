import { useState } from 'react'

/**
 * Custom hook for managing payment methods
 * Handles all CRUD operations and state management for payment cards
 */
export function usePaymentManagement(initialCards = []) {
    const [cards, setCards] = useState(initialCards)

    /**
     * Add a new payment card
     */
    const addCard = (cardData) => {
        const newId = Math.max(...cards.map(c => c.id), 0) + 1
        const newCard = {
            ...cardData,
            id: newId,
            isDefault: cards.length === 0 // First card is default
        }
        setCards(prev => [...prev, newCard])
        return newCard
    }

    /**
     * Update an existing payment card
     */
    const updateCard = (id, cardData) => {
        setCards(prev => prev.map(card =>
            card.id === id ? { ...card, ...cardData } : card
        ))
    }

    /**
     * Delete a payment card
     */
    /**
     * Delete a payment card
     */
    const deleteCard = (id) => {
        setCards(prev => prev.filter(card => card.id !== id))
    }

    /**
     * Set a card as default
     * If id is null, unsets all defaults
     */
    const setDefaultCard = (id) => {
        setCards(prev => prev.map(card => ({
            ...card,
            isDefault: card.id === id
        })))
    }

    /**
     * Unset default card
     */
    const unsetDefaultCard = () => {
        setCards(prev => prev.map(card => ({
            ...card,
            isDefault: false
        })))
    }

    /**
     * Get card by ID
     */
    const getCardById = (id) => {
        return cards.find(card => card.id === id)
    }

    /**
     * Get default card
     */
    const getDefaultCard = () => {
        return cards.find(card => card.isDefault)
    }

    return {
        cards,
        addCard,
        updateCard,
        deleteCard,
        setDefaultCard,
        getCardById,
        getDefaultCard,
        unsetDefaultCard
    }
}
