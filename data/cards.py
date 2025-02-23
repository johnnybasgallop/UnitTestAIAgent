import random
from typing import Dict, List, Optional, Tuple


class Deck:

    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, cards: Optional[List[Tuple[str, str]]] = None):
        if cards is None:
            self.cards = self._create_deck()
        else:
            self.cards = cards

    def _create_deck(self) -> List[Tuple[str, str]]:
        return [(rank, suit) for suit in self.SUITS for rank in self.RANKS]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Tuple[str, str]]:
        if num_cards > len(self.cards):
            raise ValueError("Not enough cards in the deck to deal.")
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        return f"Deck with {len(self)} cards remaining."


class Player:

    def __init__(self, name: str):
        self.name = name
        self.hand: List[Tuple[str, str]] = []

    def receive_card(self, card: Tuple[str, str]) -> None:
        self.hand.append(card)

    def show_hand(self) -> str:
        return ", ".join(f"{rank} of {suit}" for rank, suit in self.hand)

    def discard_hand(self) -> None:
        self.hand = []

    def __str__(self) -> str:
        return f"Player {self.name} with hand: {self.show_hand()}"


def play_card_game(
    num_players: int, cards_per_player: int = 5
) -> Dict[str, List[Tuple[str, str]]]:
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
        print(f"{player_name}: {', '.join(f'{rank} of {suit}' for rank, suit in hand)}")

    custom_deck = Deck([("A", "Spades"), ("K", "Spades"), ("Q", "Spades")])
    print(custom_deck)
