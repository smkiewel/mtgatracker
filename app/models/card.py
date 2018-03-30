import util

COLORMAP = {
    "R": "Red",
    "W": "White",
    "B": "Black",
    "U": "Blue",
    "G": "Green"
}


class Card(object):

    def __init__(self, name, pretty_name, cost, color_identity, card_type, sub_types, set_id, set_number, mtga_id):
        self.name = name
        self.set = set_id
        self.pretty_name = pretty_name
        self.cost = cost
        self.color_identity = color_identity
        self.card_type = card_type
        self.sub_types = sub_types
        self.set_number = set_number
        self.mtga_id = mtga_id

    @property
    def colors(self):
        colors = []
        for color_key in COLORMAP.keys():
            if color_key in self.cost or color_key in self.color_identity:
                colors.append(COLORMAP[color_key])
        if not colors:
            if self.card_type == "Basic Land":
                if "Plains" in self.pretty_name:
                    colors = ["White"]
                if "Swamp" in self.pretty_name:
                    colors = ["Black"]
                if "Forest" in self.pretty_name:
                    colors = ["Green"]
                if "Mountain" in self.pretty_name:
                    colors = ["Red"]
                if "Island" in self.pretty_name:
                    colors = ["Blue"]
            if not colors:
                colors = ["Colorless"]
        return colors

    def to_serializable(self):
        return {
            "name": self.name,
            "set": self.set,
            "colors": self.colors,
            "pretty_name": self.pretty_name,
            "cost": self.cost,
            "color_identity": self.color_identity,
            "card_type": self.card_type,
            "sub_types": self.sub_types,
            "set_number": self.set_number,
            "mtga_id": self.mtga_id
        }

    @classmethod
    def from_dict(cls, obj):
        try:
            return util.all_mtga_cards.find_one(obj["mtga_id"])
        except ValueError:
            new_unknown_card = cls("unknown_{}".format(obj["mtga_id"]), "{}: Unknown MTGA ID".format(obj["mtga_id"]), [], [], "unknown", "unknown", "unknown", -1, obj["mtga_id"])
            util.all_mtga_cards.cards.append(new_unknown_card)
            return new_unknown_card

    def is_basic(self):
        import app.set_data.weird
        return self.mtga_id in [card.mtga_id for card in app.set_data.weird.BasicLands.cards]

    def __repr__(self):
        return "<Card: '{}' {} {} {}>".format(self.pretty_name, self.colors, self.set, self.mtga_id)

    def __str__(self):
        return self.__repr__()


class GameCard(Card):

    def __init__(self, name, pretty_name, cost, color_identity, card_type, sub_types, set_id, set_number, mtga_id, owner_seat_id, game_id=-1):
        super().__init__(name, pretty_name, cost, color_identity, card_type, sub_types, set_id, set_number, mtga_id)
        self.game_id = game_id
        self.previous_iids = []
        self.owner_seat_id = owner_seat_id

    def to_serializable(self):
        serial = super(GameCard, self).to_serializable()
        serial["iid"] = self.game_id
        serial["owner_seat_id"] = self.owner_seat_id
        return serial

    def __repr__(self):
        if self.mtga_id != -1:
            return "<GameCard: {} {} iid={}>".format(self.name, self.mtga_id, self.game_id)
        else:
            return "<UnknownCard: iid={}>".format(self.game_id)

    def transform_to(self, card_id):
        new_card = util.all_mtga_cards.find_one(card_id)
        self.name = new_card.name
        self.pretty_name = new_card.pretty_name
        self.cost = new_card.cost
        self.card_type = new_card.card_type
        self.sub_types = new_card.sub_types
        self.set = new_card.set
        self.set_number = new_card.set_number
        self.mtga_id = new_card.mtga_id