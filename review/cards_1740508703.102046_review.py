import random
from typing import Dict, List, Optional, Tuple

"""A module for simulating card games."""


class Deck:
    """Represents a deck of playing cards.

    Attributes:
        cards: A list of tuples, where each tuple represents a card (rank, suit).
    """

    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, cards: Optional[List[Tuple[str, str]]] = None):
        """Initializes a Deck object.

        Args:
            cards: An optional list of cards to initialize the deck with. If None, a standard 52-card deck is created.
        """
        if cards is None:
            self.cards = self._create_deck()
        else:
            self.cards = cards

    def _create_deck(self) -> List[Tuple[str, str]]:
        """Creates a standard 52-card deck.

        Returns:
            A list of tuples, where each tuple represents a card (rank, suit).
        """
        return [(rank, suit) for suit in self.SUITS for rank in self.RANKS]

    def shuffle(self) -> None:
        """Shuffles the deck of cards in place."""
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Tuple[str, str]]:
        """Deals a specified number of cards from the deck.

        Args:
            num_cards: The number of cards to deal.

        Returns:
            A list of tuples representing the dealt cards.

        Raises:
            ValueError: If there are not enough cards in the deck to deal.
        """
        if num_cards > len(self.cards):
            raise ValueError("Not enough cards in the deck to deal.")
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards

    def __len__(self) -> int:
        """Returns the number of cards remaining in the deck."""
        return len(self.cards)

    def __str__(self) -> str:
        """Returns a string representation of the deck."""
        return f"Deck with {len(self)} cards remaining."


class Player:
    """Represents a player in a card game.

    Attributes:
        name: The player's name.
        hand: A list of tuples representing the player's hand.
    """

    def __init__(self, name: str):
        """Initializes a Player object.

        Args:
            name: The player's name.
        """
        self.name = name
        self.hand: List[Tuple[str, str]] = []

    def receive_card(self, card: Tuple[str, str]) -> None:
        """Adds a card to the player's hand.

        Args:
            card: The card to add.
        """
        self.hand.append(card)

    def show_hand(self) -> str:
        """Returns a string representation of the player's hand."""
        return ", ".join(f"{rank} of {suit}" for rank, suit in self.hand)

    def discard_hand(self) -> None:
        """Discards all cards from the player's hand."""
        self.hand = []

    def __str__(self) -> str:
        """Returns a string representation of the player."""
        return f"Player {self.name} with hand: {self.show_hand()}"


def play_card_game(
    num_players: int, cards_per_player: int = 5
) -> Dict[str, List[Tuple[str, str]]]:
    """Plays a simple card game.

    Args:
        num_players: The number of players in the game.
        cards_per_player: The number of cards each player receives.

    Returns:
        A dictionary where keys are player names and values are their hands.

    Raises:
        ValueError: If there are not enough cards in the deck for the specified number of players and cards per player.
    """
    if num_players * cards_per_player > 52:
        raise ValueError(
            "Not enough cards in a standard deck for this many players and cards per player."
        )

    deck = Deck()
    deck.shuffle()
    players = {f"Player {i+1}": Player(f"Player {i+1}") for i in range(num_players)}

    for _ in range(cards_per_player):
        for player in players.values():
            try:
                card = deck.deal(1)[0]
                player.receive_card(card)
            except ValueError:
                return {player.name: player.hand for player in players.values()}
    return {player.name: player.hand for player in players.values()}


if __name__ == "__main__":
    game_results = play_card_game(3, 7)
    for player_name, hand in game_results.items():
        print(f"{player_name}: {", ".join(f'{rank} of {suit}' for rank, suit in hand)}")

    custom_deck = Deck([("A", "Spades"), ("K", "Spades"), ("Q", "Spades")])
    print(custom_deck)