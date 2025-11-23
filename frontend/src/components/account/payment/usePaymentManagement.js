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
    const deleteCard = (id) => {
        setCards(prev => {
            const filtered = prev.filter(card => card.id !== id)

            // If we deleted the default card and there are others, make the first one default
            const deletedWasDefault = prev.find(card => card.id === id)?.isDefault
            if (deletedWasDefault && filtered.length > 0) {
                filtered[0].isDefault = true
            }

            return filtered
        })
    }

    /**
     * Set a card as default
     */
    const setDefaultCard = (id) => {
        setCards(prev => prev.map(card => ({
            ...card,
            isDefault: card.id === id
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
        getDefaultCard
    }
}
