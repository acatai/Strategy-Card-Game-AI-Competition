import sys
import math

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


def read_input():
    players = []
    for i in range(2):
        player_health, player_mana, player_deck, player_rune, player_draw = [int(j) for j in input().split()]
        players.append({
            "hp":player_health,
            "mana":player_mana,
            "deck":player_deck,
            "rune":player_rune,
            "draw":player_draw
        })
    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    for i in range(opponent_actions):
        card_number_and_action = input()
    card_count = int(input())
    cards = []
    for i in range(card_count):
        inputs = input().split()
        card = Card(inputs)
        cards.append(card)
    return players, opponent_hand, cards


class Card:
    def __init__(self, inputs=None):
        if inputs == None:
            inputs = ["???"]*11
        self.id = inputs[0]
        self.instID = inputs[1]
        self.location = inputs[2]
        self.type = inputs[3] == "???" and -1 or inputs[3]
        self.cost = inputs[4]
        self.att = inputs[5]
        self.hp = inputs[6]
        self.keywords = inputs[7]
        self.my_hp = inputs[8]
        self.opp_hp = inputs[9]
        self.draw = inputs[10]
        self.choosed = (len(inputs) >= 12) and int(inputs[11]) or 0

    types = {
       -1 : "Unknown",
        0 : "Creature",
        1 : "Green item",
        2 : "Red item",
        3 : "Blue item",
    }
Card.blankCard = Card()


class CardUI(Gtk.Button):
    def __init__(self, card, drawPhase = False):
        super(CardUI, self).__init__()
        self.card = card
        self.init_ui(card, drawPhase)
        self.show_all()

    def init_ui(self, card, drawPhase):
        # self.box = Gtk.VBox(spacing=6)
        # self.add(self.box)

        self.id = Gtk.Label(label= "id: " + str(card.id))
        self.instID = Gtk.Label(label= "instID: " + str(card.instID))
        self.type = Gtk.Label(label= Card.types[int(card.type)])#"type: " + str(card.type))
        self.cost = Gtk.Label(label= str(card.cost))#"cost: " + str(card.cost))
        self.cost.set_name("mana")
        self.att = Gtk.Label(label= str(card.att))#"att: " + str(card.att))
        self.att.set_name("attack")
        self.hp = Gtk.Label(label= str(card.hp))#"hp: " + str(card.hp))
        self.hp.set_name("health")
        self.keywords = Gtk.Label(label= str(card.keywords))#"keywords: " + str(card.keywords))
        self.my_hp = Gtk.Label(label= "my_hp: " + str(card.my_hp))
        self.opp_hp = Gtk.Label(label= "opp_hp: " + str(card.opp_hp))
        self.draw = Gtk.Label(label= "draw: " + str(card.draw))

        if drawPhase:
            self.choosed = Gtk.Label(label= "x" + str(card.choosed))


        self.grid = Gtk.Grid()
        self.add(self.grid)

        if drawPhase:
            self.grid.attach(self.choosed, 0, -1, 2, 1)
        self.grid.attach(self.id, 2, -1, 4, 1)
        self.grid.attach(self.instID, 0, 0, 6, 1)

        self.grid.attach(self.type, 0, 1, 6, 1)

        self.grid.attach(self.hp, 4, 2, 2, 1)
        self.grid.attach(self.cost, 2, 2, 2, 1)
        self.grid.attach(self.att, 0, 2, 2, 1)

        self.grid.attach(self.keywords, 0, 3, 6, 1)

        self.grid.attach(self.my_hp, 0, 4, 6, 1)
        self.grid.attach(self.opp_hp, 0, 5, 6, 1)
        self.grid.attach(self.draw, 0, 6, 6, 1)




class Game(Gtk.Window):
    def __init__(self):
        super(Game, self).__init__()
        self.connect("destroy", self.end)

        self.set_title("Legends Of Code And Magic")
        self.resize(1400, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.turn = 0
        self.phase = "draw"
        self.commands = []
        self.init_ui()
        self.show_all()


    def end(self, widget):
        print("GIVE UP")
        Gtk.main_quit()

    def init_ui(self):
        screen = Gdk.Screen.get_default()
        cssProvider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        cssProvider.load_from_path('src/test/python/style.css')


        self.box = Gtk.HBox(spacing=6)
        self.add(self.box)


        self.stat_box = Gtk.VBox(spacing=6)
        self.box.pack_start(self.stat_box, False, False, 50)


        self.player0_box = Gtk.HBox(spacing=6)
        self.stat_box.pack_end(self.player0_box, True, True, 0)

        self.player0_avatar = Gtk.Button(label= "PLAYER")
        self.player0_avatar.set_sensitive(False);
        self.stat_box.pack_end(self.player0_avatar, True, True, 0)

        self.player0_ui = {}
        self.player0_ui["hp"] = Gtk.Label(label= "Health: "+"0")
        self.player0_ui["hp"].set_name("health")
        self.player0_box.pack_start(self.player0_ui["hp"], True, True, 0)
        self.player0_ui["mana"] = Gtk.Label(label= "Mana: "+"0")
        self.player0_ui["mana"].set_name("mana")
        self.player0_box.pack_start(self.player0_ui["mana"], True, True, 0)
        self.player0_ui["deck"] = Gtk.Label(label= "Cards: "+"0")
        self.player0_box.pack_start(self.player0_ui["deck"], True, True, 0)


        self.player1_avatar = Gtk.Button(label= "OPPONENT")
        self.player1_avatar.set_relief(Gtk.ReliefStyle.NORMAL)
        self.player1_avatar.connect("clicked", self.playerChoosen)
        self.stat_box.pack_start(self.player1_avatar, True, True, 0)

        self.player1_box = Gtk.HBox(spacing=6)
        self.stat_box.pack_start(self.player1_box, True, True, 0)

        self.player1_ui = {}
        self.player1_ui["hp"] = Gtk.Label(label= "Health: "+"0")
        self.player1_ui["hp"].set_name("health")
        self.player1_box.pack_start(self.player1_ui["hp"], True, True, 0)
        self.player1_ui["mana"] = Gtk.Label(label= "Mana: "+"0")
        self.player1_ui["mana"].set_name("mana")
        self.player1_box.pack_start(self.player1_ui["mana"], True, True, 0)
        self.player1_ui["deck"] = Gtk.Label(label= "Cards: "+"0")
        self.player1_box.pack_start(self.player1_ui["deck"], True, True, 0)


        self.turn_box = Gtk.VBox(spacing=6)
        self.stat_box.pack_start(self.turn_box, False, False, 10)
        self.turn_l = Gtk.Label(label= "Turn: " + str(self.turn))
        self.turn_box.pack_start(self.turn_l, False, False, 10)
        self.turn_button = Gtk.Button(label= "End turn")
        self.turn_button.connect("clicked", self.new_turn)
        self.turn_box.pack_start(self.turn_button, False, False, 10)


        self.playarea_box = Gtk.VBox(spacing=6)
        self.box.pack_end(self.playarea_box, True, True, 0)

        self.player0_ui["hand"] = Gtk.HBox(spacing=6)
        self.playarea_box.pack_end(self.player0_ui["hand"], False, False, 5)
        self.player0_ui["board"] = Gtk.HBox(spacing=6)
        self.playarea_box.pack_end(self.player0_ui["board"], False, False, 5)
        self.player1_ui["hand"] = Gtk.HBox(spacing=6)
        self.playarea_box.pack_start(self.player1_ui["hand"], False, False, 5)
        self.player1_ui["board"] = Gtk.HBox(spacing=6)
        self.playarea_box.pack_start(self.player1_ui["board"], False, False, 5)


        self.updateView()



    def sendCommands(self):
        if len(self.commands) > 0:
            print(';'.join(self.commands))
        else:
            print("PASS")
        self.commands = []


    def updatePlayers(self):
        players, opp_cards, cards = read_input()
        for (player, player_ui) in zip(players, [self.player0_ui, self.player1_ui]):
            for (key,label_core) in [("hp","Health"), ("mana","Mana"),("deck","cards")]:
                player_ui[key].set_label(label_core + ": " + str(player[key]))
        return opp_cards, cards

    def showCardsDraw(self, opp_cards, cards):
        countCards = len(cards)
        cardsPerRow = math.floor(countCards/4)
        for i,card in enumerate(cards):
            cardUI = CardUI(card, True)
            if i//cardsPerRow == 0:
                self.player1_ui["hand"].pack_start(cardUI, True, True, 5)
            if i//cardsPerRow == 1:
                self.player1_ui["board"].pack_start(cardUI, True, True, 5)
            if i//cardsPerRow == 2:
                self.player0_ui["board"].pack_start(cardUI, True, True, 5)
            if i//cardsPerRow == 3:
                self.player0_ui["hand"].pack_start(cardUI, True, True, 5)
            cardUI.connect("clicked", self.cardClicked)

    def showCardsBattle(self, opp_cards, cards):
        for card in cards:
            cardUI = CardUI(card)
            if card.location == "0":
                 self.player0_ui["hand"].pack_start(cardUI, True, False, 5)
            elif card.location == "1":
                 self.player0_ui["board"].pack_start(cardUI, True, False, 5)
            elif card.location == "-1":
                 self.player1_ui["board"].pack_start(cardUI, True, False, 5)
            else:
                print("ERROR - bad location", card.id, card.location, file=sys.stderr, flush=True)
            cardUI.connect("clicked", self.cardClicked)
        for _ in range(opp_cards):
            cardUI = CardUI(Card.blankCard)
            self.player1_ui["hand"].pack_start(cardUI, True, False, 5)

    def updateView(self):
        opp_cards, cards = self.updatePlayers()
        if self.phase == "draw":
            self.showCardsDraw(opp_cards, cards)
        elif self.phase == "battle":
            self.showCardsBattle(opp_cards, cards)
        self.show_all()


    def new_turn(self, _):
        for box in [self.player0_ui["hand"], self.player0_ui["board"], self.player1_ui["hand"], self.player1_ui["board"]]:
            for child in box.get_children():
                box.remove(child)

        if self.phase == "draw" and self.turn > -1:
            self.commands += ["PASS"]*(30-self.turn)
            self.phase = "battle"
            self.turn = 0
        self.sendCommands()

        self.turn += 1
        self.turn_l.set_label("Turn: " + str(self.turn))

        self.card1 = None
        self.card2 = None
        self.updateView()



    def cardClicked_draw(self, widget):
        card = widget.card
        self.commands.append("CHOOSE " + str(card.id))
        card.choosed += 1
        widget.choosed.set_label("x" + str(card.choosed))
        self.turn += 1
        self.turn_l.set_label("Card: " + str(self.turn))
        if len(self.commands) == 30:
            self.turn_button.emit("clicked")

    def cardClicked_battle(self, widget):
        card = widget.card
        logAct = ""
        logBefore = (
            createLog(card)+" "+
            createLog(self.card1)+" "+
            createLog(self.card2))
        if self.card1 == card:
            logAct = "A"
            self.card1 = None
        elif self.card1 == None:
            if card.location == "0" and card.type == "0":
                logAct = "B"
                self.commands.append("SUMMON " + str(card.instID))
            else:
                logAct = "C"
                self.card1 = card
        else:
            if card.location == "1" or card.location == "-1":
                self.card2 = card
                if self.card1.type == "0":
                    logAct = "D"
                    self.commands.append("ATTACK "+str(self.card1.instID)+" "+str(self.card2.instID))
                else:
                    logAct = "E"
                    self.commands.append("USE "+str(self.card1.instID)+" "+str(self.card2.instID))
                self.card1 = None
                self.card2 = None
            else:
                logAct = "F"
                self.card1 = card

        logAfter = (
            createLog(card)+" "+
            createLog(self.card1)+" "+
            createLog(self.card2))
        print(logAct, "==>", logBefore, "-----", logAfter, file=sys.stderr, flush=True)


    def cardClicked(self, widget):
        if self.phase == "draw":
            self.cardClicked_draw(widget)
        elif self.phase == "battle":
            self.cardClicked_battle(widget)
        else:
            print("ERRROOROROOROOR", self.phase, self.turn, widget, file=sys.stderr, flush=True)

    def playerChoosen(self, widget):
        if self.phase == "draw" or self.card1 == None:
            return
        card = self.card1
        logAct = "-"
        logCard = (
            createLog(card)+" "+
            createLog(self.card1)+" "+
            createLog(self.card2))
        if card.location == "1":
            logAct = "F"
            self.commands.append("ATTACK "+str(self.card1.instID)+" "+str(-1))
            self.card1 = None
        elif card.location == "0" and card.type != "0":
            logAct = "G"
            self.commands.append("USE "+str(self.card1.instID)+" "+str(-1))
            self.card1 = None

        print(logAct, "==>", logCard, file=sys.stderr, flush=True)


def createLog(card):
    return (card
        and "("+" ".join([str(card.instID), str(card.type), str(card.location)])+")"
        or "(_ _ _)")


r = Game()
Gtk.main()
