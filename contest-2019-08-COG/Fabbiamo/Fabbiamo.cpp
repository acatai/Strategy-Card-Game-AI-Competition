#include <algorithm>
#include <cassert>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

static const int VALUE_WIN = 100000;
static const int SEARCH_DEPTH = 4;

#include <immintrin.h>
#define POPCNT32(a) _mm_popcnt_u32(a)
#define PEXT(x) _pext_u32(x)
#define BLSR(x) _blsr_u32(x)
#define ASSERT(X) (assert(X))

inline int LSB32(uint32_t x)
{
        ASSERT(x != 0);
        return __builtin_ctzll(x);
}

inline int pop_lsb(uint32_t &x)
{
        int index = LSB32(x);
        x = BLSR(x);
        return index;
}

// -----------------------------
//            enum
// -----------------------------

enum Color : int
{
        SELF,
        OPPONENT,
        COLOR_NB,
        COLOR_ZERO = 0,
};

inline Color operator~(Color c) { return (Color)(c ^ 1); }

inline bool is_ok(Color c) { return COLOR_ZERO <= c && c < COLOR_NB; }

// -----------------------------
//            File
// -----------------------------

// instead of Lane
enum File
{
        FILE_1, // Left(0)
        FILE_2, // Right(1)
        FILE_3, // Hand(2)
        FILE_NB,
        FILE_ZERO = 0,
};

// -----------------------------
//            Rank
// -----------------------------

// instead of Location
enum Rank
{
        RANK_1, // Hand(0)
        RANK_2, // selfField(1)
        RANK_3, // opponent Field(2)
        RANK_NB,
        RANK_ZERO = 0,
};

enum Square
{
        // SQ_[File][Rank]
        SQ_31a,
        SQ_31b,
        SQ_31c,
        SQ_31d,
        SQ_31e,
        SQ_31f,
        SQ_31g,
        SQ_31h,
        SQ_12a,
        SQ_12b,
        SQ_12c,
        SQ_22a,
        SQ_22b,
        SQ_22c,
        SQ_13a,
        SQ_13b,
        SQ_13c,
        SQ_23a,
        SQ_23b,
        SQ_23c,
        SQ_NB,
        SQ_ZERO = 0,

        SQ_PLAYER = SQ_NB,
        SQ_NB_PLUS,
};

const Color squareToColor[SQ_NB] = {
    SELF, SELF, SELF, SELF, SELF, SELF, SELF, SELF,             // SQ_31a - SQ_31h
    SELF, SELF, SELF, SELF, SELF, SELF,                         // SQ_12a - SQ_22c
    OPPONENT, OPPONENT, OPPONENT, OPPONENT, OPPONENT, OPPONENT, // SQ_13a - SQ_23c
};

const File squareToFile[SQ_NB] = {
    FILE_3, FILE_3, FILE_3, FILE_3, FILE_3, FILE_3, FILE_3, FILE_3, // SQ_31a - SQ_31h
    FILE_1, FILE_1, FILE_1, FILE_2, FILE_2, FILE_2,                 // SQ_12a - SQ_22c
    FILE_1, FILE_1, FILE_1, FILE_2, FILE_2, FILE_2,                 // SQ_13a - SQ_23c
};

const Rank squareToRank[SQ_NB] = {
    RANK_1, RANK_1, RANK_1, RANK_1, RANK_1, RANK_1, RANK_1, RANK_1, // SQ_31a - SQ_31h
    RANK_2, RANK_2, RANK_2, RANK_2, RANK_2, RANK_2,                 // SQ_12a - SQ_22c
    RANK_3, RANK_3, RANK_3, RANK_3, RANK_3, RANK_3,                 // SQ_13a - SQ_23c
};

const Square ostreamSQ[SQ_NB] =
    {SQ_13a, SQ_13b, SQ_13c, SQ_23a, SQ_23b, SQ_23c,
     SQ_12a, SQ_12b, SQ_12c, SQ_22a, SQ_22b, SQ_22c,
     SQ_31a, SQ_31b, SQ_31c, SQ_31d, SQ_31e, SQ_31f, SQ_31g, SQ_31h};

inline Color color_of(Square sq) { return squareToColor[sq]; }
inline File file_of(Square sq) { return squareToFile[sq]; }
inline File file_of(int lane) { return lane == -1 ? FILE_3 : (File)lane; }
inline Rank rank_of(Square sq) { return squareToRank[sq]; }
inline Rank rank_of(int location) { return location == -1 ? RANK_3 : (Rank)location; }

enum CardId : int
{
        CARD_ID_ZERO,
        CARD_ID_NB = 160 + 1,
        NONE_CARD_ID = -1,
};

inline bool is_ok(CardId ci) { return CARD_ID_ZERO <= ci && ci < CARD_ID_NB; }

std::ostream &operator<<(std::ostream &os, const CardId &ci)
{
        ASSERT(is_ok(ci));
        os << '#' << int(ci);
        return os;
}

enum CardType : int
{
        CREATURE,
        GREEN_ITEM,
        RED_ITEM,
        BLUE_ITEM,
        CARD_TYPE_NB,
        ALL_CARDS,
        CARD_TYPE_BB_NB,
        CARD_TYPE_ZERO = 0,
        NULL_TYPE = -1,
};

inline bool is_ok(CardType ct) { return CARD_TYPE_ZERO <= ct && ct < CARD_TYPE_NB; }

std::ostream &operator<<(std::ostream &os, const CardType &ct)
{
        std::string str[] = {"c", "g", "r", "b"};
        ASSERT(is_ok(ct));
        os << str[ct];
        return os;
}

enum AbilityType : int
{
        Breakthrough,
        Charge,
        Drain,
        Guard,
        Lethal,
        Ward,
        ABILITY_NB,
        NONE_ABILITY,
        ALL_ABILITY,
        ABILITY_BB_NB,
        ABILITY_ZERO = 0,
};

inline bool is_ok(AbilityType at) { return ABILITY_ZERO <= at && at < ABILITY_NB; }

inline uint16_t shiftAbility(AbilityType at) { return uint16_t(1 << (int)(at)); }

// -----------------------------
//            Move
// -----------------------------

enum Move : uint16_t
{
        MOVE_PASS = 1 << 11,
        MOVE_SUMMON = 1 << 12,
        MOVE_ATTACK = 1 << 13,
        MOVE_USE = 1 << 14,
};

// Return Move 0-5 bit
inline Square move_to(Move m) { return (Square)(m & 0x1f); }

// Return Move 6-10 bit
inline Square move_from(Move m) { return (Square)((m >> 6) & 0x1f); }

inline bool is_pass(Move m) { return (m & MOVE_PASS) != 0; }
inline bool is_summon(Move m) { return (m & MOVE_SUMMON) != 0; }
inline bool is_attack(Move m) { return (m & MOVE_ATTACK) != 0; }
inline bool is_use(Move m) { return (m & MOVE_USE) != 0; }

std::ostream &operator<<(std::ostream &os, const Move &m)
{
        if (is_pass(m))
        {
                os << "pass";
                return os;
        }
        else if (is_summon(m))
                os << "summon ";
        else if (is_attack(m))
                os << "attack ";
        else if (is_use(m))
                os << "use ";
        os << move_from(m) << ' ' << move_to(m);

        return os;
}

struct ExtMove
{
        Move move;
        double value;

        operator Move() const { return move; }
        void operator=(Move m) { move = m; }
};

inline bool operator<(const ExtMove &first, const ExtMove &second) { return first.value < second.value; }

enum MOVE_GEN_TYPE
{
        SUMMON,
        ATTACK,
        USE,

        PASS,
        LEGAL,
        NON_ATTACK,

        USE_GREEN,
        USE_RED,
        USE_BLUE,
};

// -----------------------------
//            Macro
// -----------------------------

#define ENABLE_OPERATORS_ON(T)                                                         \
        constexpr T operator+(const T d1, const T d2) { return T(int(d1) + int(d2)); } \
        inline T &operator+=(T &d1, const T d2) { return d1 = d1 + d2; }               \
        inline T &operator++(T &d) { return d = T(int(d) + 1); }                       \
        inline T operator++(T &d, int)                                                 \
        {                                                                              \
                T prev = d;                                                            \
                d = T(int(d) + 1);                                                     \
                return prev;                                                           \
        }                                                                              \
        inline std::istream &operator>>(std::istream &in, T &d)                        \
        {                                                                              \
                int n;                                                                 \
                in >> n;                                                               \
                d = T(n);                                                              \
                return in;                                                             \
        }

ENABLE_OPERATORS_ON(Color)
ENABLE_OPERATORS_ON(File)
ENABLE_OPERATORS_ON(Rank)
ENABLE_OPERATORS_ON(Square)
ENABLE_OPERATORS_ON(CardId)
ENABLE_OPERATORS_ON(CardType)
ENABLE_OPERATORS_ON(AbilityType)
ENABLE_OPERATORS_ON(Move)

#define ENABLE_RANGE_OPERATORRS_ON(X, ZERO, NB) \
        inline X operator*(X x) { return x; }   \
        inline X begin(X) { return ZERO; }      \
        inline X end(X) { return NB; }

ENABLE_RANGE_OPERATORRS_ON(Color, COLOR_ZERO, COLOR_NB)
ENABLE_RANGE_OPERATORRS_ON(File, FILE_ZERO, FILE_NB)
ENABLE_RANGE_OPERATORRS_ON(Rank, RANK_ZERO, RANK_NB)
ENABLE_RANGE_OPERATORRS_ON(Square, SQ_ZERO, SQ_NB)
ENABLE_RANGE_OPERATORRS_ON(AbilityType, ABILITY_ZERO, ABILITY_NB)

#define SQ Square()
#define COLOR Color()
#define ABILITY AbilityType()

#define FOREACH_BB(BB_, SQ_, Statement_)              \
        do                                            \
        {                                             \
                while (BB_.p)                         \
                {                                     \
                        SQ_ = (Square)pop_lsb(BB_.p); \
                        Statement_;                   \
                }                                     \
        } while (false)

// -----------------------------
//           Player
// -----------------------------

struct Player
{
        int health; // playerHealth
        int mana;   // playerMana
        int deck;   // playerDeck
        int rune;   //playerRune
        int draw;   //playerDraw
};

std::istream &operator>>(std::istream &in, Player &p)
{
        in >> p.health >> p.mana >> p.deck >> p.rune >> p.draw;
        in.ignore();
        return in;
}

// -----------------------------
//            Card
// -----------------------------

struct Card
{
        CardId id;
        CardType type;
        int intanceId;
        int cost;
        int attack;
        int defense;
        int health_change[COLOR_NB];
        int add_draw;

        // 0bit...B, 1bit...C, 2bit...D, 3bit...G, 4bit...L, 5bit...W.
        int abilities;

        bool canAttack;
};

inline Card NoneCard()
{
        Card card;
        card.id = NONE_CARD_ID;
        card.intanceId = -1;
        return card;
}
#define NONE_CARD (NoneCard())

inline bool isExist(Card card)
{
        return card.id != NONE_CARD_ID;
}

inline bool isAbility(Card card, AbilityType at)
{
        return card.abilities & shiftAbility(at);
}

// -----------------------------
//          Bitboard
// -----------------------------

struct alignas(16) Bitboard
{
        uint32_t p;

        Bitboard() {}
        Bitboard(uint32_t p) { this->p = p; }
        Bitboard(const Bitboard &bb) { this->p = bb.p; }
        Bitboard(Square sq);

        inline operator bool() const { return POPCNT32(p) > 0; }

        inline Square pop() { return Square(pop_lsb(p)); }
        inline Square pop_c() const { return Square(LSB32(p)); }
        int pop_count() const { return (int)(POPCNT32(p)); }

        Bitboard &operator=(const Bitboard &bb)
        {
                this->p = bb.p;
                return *this;
        }

        Bitboard &operator|=(const Bitboard &bb)
        {
                this->p |= bb.p;
                return *this;
        }
        Bitboard &operator&=(const Bitboard &bb)
        {
                this->p &= bb.p;
                return *this;
        }
        Bitboard &operator^=(const Bitboard &bb)
        {
                this->p ^= bb.p;
                return *this;
        }

        Bitboard &operator<<=(int shift)
        {
                p = p << shift;
                return *this;
        }
        Bitboard &operator>>=(int shift)
        {
                p = p >> shift;
                return *this;
        }

        Bitboard operator&(const Bitboard &rhs) const { return Bitboard(*this) &= rhs; }
        Bitboard operator|(const Bitboard &rhs) const { return Bitboard(*this) |= rhs; }
        Bitboard operator^(const Bitboard &rhs) const { return Bitboard(*this) ^= rhs; }
        Bitboard operator<<(const int i) const { return Bitboard(*this) <<= i; }
        Bitboard operator>>(const int i) const { return Bitboard(*this) >>= i; }
};

Bitboard SquareBB[SQ_NB];
Bitboard::Bitboard(Square sq) { *this = SquareBB[sq]; }

Bitboard SummonBB[64];
inline const Bitboard summon_bb(uint32_t p) { return SummonBB[p >> 8 & 0x3f]; }

inline Bitboard operator|(const Bitboard &b, Square sq) { return b | SquareBB[sq]; }
inline Bitboard operator&(const Bitboard &b, Square sq) { return b & SquareBB[sq]; }
inline Bitboard operator^(const Bitboard &b, Square sq) { return b ^ SquareBB[sq]; }

const Bitboard ALL_BB = Bitboard(0xfffff);
const Bitboard ZERO_BB = Bitboard(0);

const Bitboard FILE1_BB = Bitboard(0x1c7 << 8);
const Bitboard FILE2_BB = Bitboard(0x1c7 << 11);
const Bitboard FILE3_BB = Bitboard(0xff);

const Bitboard RANK1_BB = FILE3_BB;
const Bitboard RANK2_BB = Bitboard(0x3f << 8);
const Bitboard RANK3_BB = Bitboard(0x3f << 14);

const Bitboard FILE_BB[FILE_NB] = {FILE1_BB, FILE2_BB, FILE3_BB};
const Bitboard RANK_BB[RANK_NB] = {RANK1_BB, RANK2_BB, RANK3_BB};

const Bitboard HAND_BB = RANK1_BB;
const Bitboard FIELD_BB = RANK2_BB | RANK3_BB;

std::ostream &operator<<(std::ostream &os, const Bitboard &bb)
{
        for (Square sq : ostreamSQ)
        {
                os << ((bb & sq) ? '*' : '.');

                if (sq == SQ_22c || sq == SQ_23c)
                        os << std::endl;
        }
        os << std::endl;
        return os;
}

// -----------------------------
//            Input
// -----------------------------

struct input_t
{
        Card cards[SQ_NB];
        Player players[COLOR_NB];
        int cardCount;
};

std::istream &operator>>(std::istream &in, input_t &t)
{
        int boardIndex[FILE_NB][RANK_NB] = {{-1, 8, 14}, {-1, 11, 17}, {-1, -1, -1}};
        // boardIndex[FILE_1][RANK_2] = 8;
        // boardIndex[FILE_2][RANK_2] = 11;
        // boardIndex[FILE_1][RANK_3] = 14;
        // boardIndex[FILE_2][RANK_3] = 17;

        for (Color c : COLOR)
                in >> t.players[c];

        int white_hand, white_actions;
        in >> white_hand >> white_actions;
        in.ignore();

        for (int i = 0; i < white_actions; ++i)
        {
                std::string cardNumberAndAction;
                getline(in, cardNumberAndAction);
        }

        in >> t.cardCount;
        in.ignore();

        char str[6];
        int handIndex = 0;
        int lane, location;

        for (Square sq : SQ)
                t.cards[sq] = NONE_CARD;
        for (int i = 0; i < t.cardCount; ++i)
        {
                Card card;
                in >> card.id >> card.intanceId >> location >> card.type >> card.cost >> card.attack >> card.defense >> str >> card.health_change[SELF] >> card.health_change[OPPONENT] >> card.add_draw >> lane;
                in.ignore();

                File file = file_of(lane);
                Rank rank = rank_of(location);

                card.abilities = 0;
                for (int i = 0; i < 6; ++i)
                        if (str[i] != '-')
                                card.abilities |= 1 << i;

                card.canAttack = rank != RANK_1 || isAbility(card, Charge);

                if (rank == RANK_1)
                        t.cards[handIndex++] = card;
                else
                        t.cards[boardIndex[file][rank]++] = card;
        }

        return in;
}

// -----------------------------
//           Output
// -----------------------------

struct output_t
{
        MOVE_GEN_TYPE gentype;

        // board[from].intanceId
        int id1;

        // board[to].intanceId or "-1"
        int id2;
};

std::ostream &operator<<(std::ostream &os, const output_t &output)
{
        std::string str[] = {"SUMMON ", "ATTACK ", "USE "};

        MOVE_GEN_TYPE GenType = output.gentype;
        ASSERT(SUMMON <= GenType && GenType <= USE);

        os << str[GenType] << output.id1 << ' ' << output.id2;

        return os;
}

typedef std::vector<output_t> OutputList;

std::ostream &operator<<(std::ostream &os, const OutputList &ol)
{
        if (ol.empty())
                os << "PASS";
        else
        {
                for (auto itr = ol.begin(); itr != ol.end(); ++itr)
                {
                        if (itr != ol.begin())
                                os << ';';
                        os << (*itr);
                }
        }

        return os;
}

// -----------------------------
//          State Info
// -----------------------------

struct StateInfo
{
        bool isLostWard[COLOR_NB];
        bool isRemoveCard[COLOR_NB];
        Card turnCard[COLOR_NB];

        friend struct Position;
        StateInfo *previous;

        void *operator new(std::size_t s);
        void operator delete(void *p) noexcept;
};

// -----------------------------
//             Position
// -----------------------------

struct Position
{
        void set_turn(input_t input);

        Position() {}
        Position(const Position &) = delete;
        Position &operator=(const Position &) = delete;

        Color side_to_move() const { return sideToMove; }

        void flip_turn() { sideToMove = ~sideToMove; }

        int playerHealth(Color Us) const { return players[Us].health; }
        int playerMana(Color Us) const { return players[Us].mana; }

        Card board_on(Square sq) const { return board[sq]; }

        int cardCost(Square sq) const { return board[sq].cost; }
        bool cardCanAttack(Square sq) const { return board[sq].canAttack; }

        Bitboard empties() const { return cards() ^ ALL_BB; }
        Bitboard cards() const { return byTypeBB[ALL_CARDS]; }
        Bitboard cards(Color c) const { return byColorBB[c]; }
        Bitboard cards(CardType ct) const { return byTypeBB[ct]; }
        Bitboard cards(Color c, CardType ct) const { return cards(c) & cards(ct); }

        void do_move(Move m, StateInfo &new_st);
        void undo_move(Move m);

        output_t make_output(Move m);

        friend std::ostream &operator<<(std::ostream &os, const Position &pos);

private:
        template <Color Us>
        void do_move_impl(Move m, StateInfo &new_st);

        template <Color Us>
        void undo_move_impl(Move m);

        template <Color Us>
        void update_player(Square from);

        template <Color Us>
        void update_player_reverse(Square from);

        void xor_card(Square sq, Card card);
        void put_card(Square sq, Card card);
        void remove_card(Square sq);

        void update_card(Square sq, Card card);

        // Bitboards

        Bitboard byColorBB[COLOR_NB];
        Bitboard byTypeBB[CARD_TYPE_BB_NB];

        Player players[COLOR_NB];

        Card board[SQ_NB];

        Color sideToMove;

        StateInfo *st;
};

std::ostream &operator<<(std::ostream &os, const Position &pos)
{
        for (Square sq : ostreamSQ)
        {
                if (isExist(pos.board[sq]))
                {
                        os << pos.board[sq].type;
                        os << (pos.board[sq].canAttack ? '*' : ' ');
                        //os << (isAbility(pos.board[sq], Guard) ? '*' : ' ');
                }
                else
                        os << ". ";

                if (sq == SQ_22c || sq == SQ_23c)
                        os << std::endl;
        }
        os << std::endl;
        return os;
}

void Position::set_turn(input_t input)
{
        std::memset(this, 0, sizeof(Position));

        for (Color c : COLOR)
                players[c] = input.players[c];

        for (Square sq : SQ)
        {
                board[sq] = input.cards[sq];
                if (isExist(board[sq]))
                        xor_card(sq, board[sq]);
        }
}

output_t Position::make_output(Move m)
{
        output_t ret;
        if (is_pass(m))
        {
                ret.gentype = PASS;
                ret.id1 = ret.id2 = 0;
        }
        else if (is_summon(m))
        {
                ret.gentype = SUMMON;
                ret.id1 = board[move_from(m)].intanceId;
                ret.id2 = file_of(move_to(m));
        }
        else if (is_attack(m))
        {
                ret.gentype = ATTACK;
                ret.id1 = board[move_from(m)].intanceId;

                Square to = move_to(m);
                ret.id2 = (to == SQ_PLAYER) ? -1 : board[to].intanceId;
        }
        else if (is_use(m))
        {
                ret.gentype = USE;
                ret.id1 = board[move_from(m)].intanceId;

                Square to = move_to(m);
                ret.id2 = (to == SQ_PLAYER) ? -1 : board[to].intanceId;
        }
        return ret;
}

template <Color Us>
void Position::do_move_impl(Move m, StateInfo &new_st)
{
        Square from = move_from(m);
        Square to = move_to(m);

        StateInfo *prev;
        new_st.previous = prev = st;
        st = &new_st;

        st->isLostWard[Us] = st->isLostWard[~Us] = false;
        st->isRemoveCard[Us] = st->isRemoveCard[~Us] = false;

        st->turnCard[Us] = board[from];
        st->turnCard[~Us] = (is_summon(m) || to == SQ_PLAYER) ? NONE_CARD : board[to];

        if (is_summon(m))
        {
                ASSERT(!isExist(board[to]));
                update_player<Us>(from);
                put_card(to, board[from]);
                st->isRemoveCard[Us] = true;
        }
        else if (is_attack(m))
        {
                board[from].canAttack = false;

                if (to == SQ_PLAYER)
                {
                        players[~Us].health -= board[from].attack;

                        if (isAbility(board[from], Drain))
                                players[Us].health += board[from].attack;
                }
                else
                {
                        // from(Us) ---> to(~Us)
                        {
                                if (isAbility(board[to], Ward))
                                {
                                        board[to].abilities ^= shiftAbility(Ward);
                                        st->isLostWard[~Us] = true;
                                }
                                else
                                {
                                        board[to].defense -= board[from].attack;

                                        if (isAbility(board[from], Drain))
                                                players[Us].health += board[to].attack;

                                        if (isAbility(board[from], Lethal))
                                                st->isRemoveCard[~Us] = true;

                                        if (board[to].defense <= 0)
                                        {
                                                if (isAbility(board[from], Breakthrough))
                                                        players[~Us].health += board[to].defense;
                                                st->isRemoveCard[~Us] = true;
                                        }
                                }
                        }

                        // from(Us) <--- to(~Us)
                        {
                                if (isAbility(board[from], Ward))
                                {
                                        board[to].abilities ^= shiftAbility(Ward);
                                        st->isLostWard[Us] = true;
                                }
                                else
                                {
                                        board[from].defense -= board[to].attack;

                                        if (isAbility(board[to], Lethal))
                                                st->isRemoveCard[Us] = true;

                                        if (board[from].defense <= 0)
                                        {
                                                if (isAbility(board[to], Breakthrough))
                                                        players[Us].health += board[from].defense;
                                                st->isRemoveCard[Us] = true;
                                        }
                                }
                        }
                }
        }
        else if (is_use(m))
        {
                if (board[from].type == GREEN_ITEM)
                {
                        update_player<Us>(from);
                        board[to].attack += board[from].attack;
                        board[to].defense += board[from].defense;
                        board[to].abilities |= board[from].abilities;
                }
                if (board[from].type == RED_ITEM)
                {
                        board[to].attack += board[from].attack;
                        board[to].defense += board[from].defense;
                        board[to].abilities ^= board[from].abilities;
                }
                if (board[from].type == BLUE_ITEM)
                {
                        if (to == SQ_PLAYER)
                                update_player<Us>(from);
                        else
                        {
                                board[to].attack += board[from].attack;
                                board[to].defense += board[from].defense;
                        }
                }

                st->isRemoveCard[Us] = true;

                if (to != SQ_PLAYER && board[to].defense <= 0)
                        st->isRemoveCard[color_of(to)] = true;
        }

        if (st->isRemoveCard[Us])
                remove_card(from);
        if (st->isRemoveCard[~Us])
                remove_card(to);
}

template <Color Us>
void Position::undo_move_impl(Move m)
{
        Square from = move_from(m);
        Square to = move_to(m);

        if (is_summon(m))
        {
                auto card = board[to];
                put_card(from, card);
                update_player_reverse<Us>(from);
                remove_card(to);
        }
        else if (is_attack(m))
        {
                if (st->isRemoveCard[Us])
                        put_card(from, st->turnCard[Us]);
                else
                        board[from] = st->turnCard[Us];

                if (to == SQ_PLAYER)
                {
                        // ASSERT(board[from].canAttack == false);
                        board[from].canAttack = true;

                        players[~Us].health += board[from].attack;

                        if (isAbility(board[from], Drain))
                                players[Us].health -= board[to].attack;
                }
                else
                {
                        if (st->isRemoveCard[~Us])
                                put_card(to, st->turnCard[~Us]);
                        else
                                board[to] = st->turnCard[~Us];

                        // from(Us) ---> to(~Us)
                        {

                                if (isAbility(board[from], Drain))
                                        players[Us].health -= board[from].attack;

                                if (st->isRemoveCard[~Us] && isAbility(board[from], Breakthrough))
                                {
                                        // board[to].defense - board[from].attack < 0
                                        players[~Us].health += board[from].attack - board[to].defense;
                                }
                        }

                        // from(Us) <--- to(~Us)
                        {
                                if (isAbility(board[from], Drain))
                                        players[~Us].health -= board[to].attack;

                                if (st->isRemoveCard[Us] && isAbility(board[from], Breakthrough))
                                {
                                        // board[from].defense - board[to].attack < 0
                                        players[Us].health += board[to].attack - board[from].defense;
                                }
                        }
                }
        }
        else if (is_use(m))
        {
                put_card(from, st->turnCard[Us]);

                if (st->isRemoveCard[~Us])
                        put_card(to, st->turnCard[~Us]);
                else if (to != SQ_PLAYER)
                        board[to] = st->turnCard[~Us];

                if (board[from].type == GREEN_ITEM || (board[from].type == BLUE_ITEM && to == SQ_PLAYER))
                        update_player_reverse<Us>(from);
        }

        st = st->previous;
}

void Position::do_move(Move m, StateInfo &new_st)
{
        if (sideToMove == SELF)
                do_move_impl<SELF>(m, new_st);
        else
                do_move_impl<OPPONENT>(m, new_st);
}

void Position::undo_move(Move m)
{
        if (sideToMove == SELF)
                undo_move_impl<SELF>(m);
        else
                undo_move_impl<OPPONENT>(m);
}

template <Color Us>
void Position::update_player(Square from)
{
        players[Us].health += board[from].health_change[Us];
        players[~Us].health += board[from].health_change[~Us];

        players[Us].mana -= board[from].cost;
        players[Us].draw += board[from].add_draw;
        --players[Us].deck;
}

template <Color Us>
void Position::update_player_reverse(Square from)
{
        players[Us].health -= board[from].health_change[Us];
        players[~Us].health -= board[from].health_change[~Us];

        players[Us].mana += board[from].cost;
        players[Us].draw -= board[from].add_draw;
        ++players[Us].deck;
}

void Position::xor_card(Square sq, Card card)
{
        byColorBB[color_of(sq)] ^= sq;
        byTypeBB[ALL_CARDS] ^= sq;
        byTypeBB[card.type] ^= sq;
}

inline void Position::put_card(Square sq, Card card)
{
        ASSERT(!isExist(board[sq]));
        board[sq] = card;
        xor_card(sq, card);
}

inline void Position::remove_card(Square sq)
{
        ASSERT(0 <= sq && sq < 20);
        Card card = board[sq];
        board[sq] = NONE_CARD;
        //std::cerr << sq << ' ' << card.id << endl;
        ASSERT(isExist(card));
        xor_card(sq, card);
}

#define MAKE_MOVE_TARGET(from, to, moveType) ((Move)(to + (from << 6) + moveType))

template <Color Us, Move m, bool OpponentDamage>
struct make_move_target
{
        inline ExtMove *operator()(Square from, const Bitboard &target_, ExtMove *mlist)
        {
                Square to;
                Bitboard target = target_;

                FOREACH_BB(target, to, {
                        mlist++->move = MAKE_MOVE_TARGET(from, to, m);
                });

                if (OpponentDamage)
                        mlist++->move = MAKE_MOVE_TARGET(from, SQ_PLAYER, m);

                return mlist;
        }
};

template <MOVE_GEN_TYPE GenType, Color Us>
struct GenerateSummonMoves
{
        inline ExtMove *operator()(const Position &pos, ExtMove *mlist)
        {
                auto cards = pos.cards(Us, CREATURE) & HAND_BB;
                auto occ = pos.cards();

                auto target = summon_bb(occ.p);

                while (cards)
                {
                        auto from = cards.pop();

                        if (pos.playerMana(Us) < pos.cardCost(from))
                                continue;

                        mlist = make_move_target<Us, MOVE_SUMMON, false>()(from, target, mlist);
                }

                return mlist;
        }
};

template <MOVE_GEN_TYPE GenType, Color Us>
struct GenerateAttackMoves
{
        inline ExtMove *operator()(const Position &pos, ExtMove *mlist)
        {
                for (File f : {FILE_1, FILE_2})
                {
                        auto cards = pos.cards(Us) & FILE_BB[f];

                        Bitboard bb, occ;
                        bb = occ = pos.cards(~Us) & FILE_BB[f];

                        while (bb)
                        {
                                auto to = bb.pop();
                                if (isAbility(pos.board_on(to), Guard))
                                        ;
                                else
                                        occ ^= to;
                        }

                        auto enemy = occ ? occ : (pos.cards(~Us) & FILE_BB[f]);

                        while (cards)
                        {
                                auto from = cards.pop();

                                if (!pos.cardCanAttack(from))
                                        continue;

                                auto target = enemy & FILE_BB[file_of(from)];

                                if (occ)
                                        mlist = make_move_target<Us, MOVE_ATTACK, false>()(from, target, mlist);
                                else
                                        mlist = make_move_target<Us, MOVE_ATTACK, true>()(from, target, mlist);
                        }
                }

                return mlist;
        }
};

template <MOVE_GEN_TYPE GenType, Color Us, CardType itemType, bool OpponentDamage>
struct GenerateUseMoves
{
        inline ExtMove *operator()(const Position &pos, ExtMove *mlist, const Bitboard &target)
        {
                auto cards = pos.cards(Us, itemType);

                while (cards)
                {
                        auto from = cards.pop();

                        if (pos.playerMana(Us) < pos.cardCost(from))
                                continue;

                        mlist = make_move_target<Us, MOVE_USE, OpponentDamage>()(from, target, mlist);
                }

                return mlist;
        }
};

template <MOVE_GEN_TYPE GenType, Color Us>
ExtMove *generate_general(const Position &pos, ExtMove *mlist, Square recapSq = SQ_NB)
{
        if (GenType == LEGAL || GenType == SUMMON || GenType == NON_ATTACK)
                mlist = GenerateSummonMoves<GenType, Us>()(pos, mlist);

        if (GenType == LEGAL || GenType == ATTACK)
                mlist = GenerateAttackMoves<GenType, Us>()(pos, mlist);

        if (GenType == LEGAL || GenType == NON_ATTACK || GenType == USE_GREEN)
                mlist = GenerateUseMoves<GenType, Us, GREEN_ITEM, false>()(pos, mlist, pos.cards(Us) & FIELD_BB);

        if (GenType == LEGAL || GenType == NON_ATTACK || GenType == USE_RED)
                mlist = GenerateUseMoves<GenType, Us, RED_ITEM, false>()(pos, mlist, pos.cards(~Us) & FIELD_BB);

        if (GenType == LEGAL || GenType == NON_ATTACK || GenType == USE_BLUE)
                mlist = GenerateUseMoves<GenType, Us, BLUE_ITEM, true>()(pos, mlist, pos.cards(~Us) & FIELD_BB);

        return mlist;
}

template <MOVE_GEN_TYPE GenType>
ExtMove *generateMoves(const Position &pos, ExtMove *mlist, Square sq = SQ_NB)
{
        return pos.side_to_move() == SELF ? generate_general<GenType, SELF>(pos, mlist, sq) : generate_general<GenType, OPPONENT>(pos, mlist, sq);
}

template <MOVE_GEN_TYPE GenType>
struct MoveList
{
        MoveList(const Position &pos) : last(generateMoves<GenType>(pos, mlist)) {}

        const ExtMove *begin() const { return mlist; }

        const ExtMove *end() const { return last; }

        std::size_t size() const { return last - mlist; }

        const ExtMove at(std::size_t i) const { return begin()[i]; }

private:
        ExtMove mlist[256], *last;
};

namespace Bitboards
{
void init();
}

void Bitboards::init()
{
        for (Square sq : SQ)
                SquareBB[sq] = 1 << (int)sq;

        int p[] = {0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111};
        int q[] = {0b001, 0b010, 0b001, 0b100, 0b001, 0b010, 0b001, 0b000};
        for (int j = 0; j < 8; ++j)
                for (int i = 0; i < 8; ++i)
                {
                        uint32_t index = p[i] << 3 | p[j];
                        uint32_t value = q[i] << 3 | q[j];
                        SummonBB[index] = Bitboard(value << 8);
                }
}

// -----------------------------
//           Search
// -----------------------------

// 1. search_self_node
// 2. search_opponent_node(depth 1)
// 3. evaluate(Position)

namespace Search
{
int evaluate(const Card card);
int evaluate(const Position &pos);

int search_self_node(Position &pos, Move &best, int depth, int alpha);
int search_opponent_node(Position &pos, Move &best, int alpha);

void search_battle(Position &pos);
void search_draft(input_t input, int *Hand);

bool check_mate(const Position &pos);

} // namespace Search

int Search::evaluate(const Card card)
{
        if (card.type == CREATURE)
                return 3 * card.attack + 2 * card.defense + card.attack * isAbility(card, Ward) + 25 * isAbility(card, Guard) + 30 * isAbility(card, Lethal);

        if (card.type == GREEN_ITEM)
                return 4 * card.attack + 3 * card.defense + 20 * isAbility(card, Guard) + 20 * isAbility(card, Lethal);

        if (card.type == RED_ITEM)
                return 3 * std::abs(card.attack) + 5 * std::abs(card.defense);

        // ASSERT(card.type == BLUE_ITEM)
        return 4 * std::abs(card.attack) + 6 * std::abs(card.defense);
}

int Search::evaluate(const Position &pos)
{
        if (pos.playerHealth(SELF) <= 0)
                return -90000;

        if (pos.playerHealth(OPPONENT) <= 0)
                return +90000;

        int score = 0;

        score += 5 * (pos.playerHealth(SELF) - pos.playerHealth(OPPONENT));

        Square self[] = {SQ_12a, SQ_12b, SQ_12c, SQ_22a, SQ_22b, SQ_22c};
        Square oppo[] = {SQ_13a, SQ_13b, SQ_13c, SQ_23a, SQ_23b, SQ_23c};

        const int cV[] = {0, 15, 15, 20};
        const int gV[] = {0, 15, 20, 25};

        int creatureCnt[COLOR_NB][2] = {};
        int guardCnt[COLOR_NB][2] = {};

        for (auto sq : self)
        {
                auto card = pos.board_on(sq);
                if (isExist(card))
                {
                        ++creatureCnt[SELF][file_of(sq)];
                        if (isAbility(card, Guard))
                                ++guardCnt[SELF][file_of(sq)];

                        score += evaluate(card);
                }
        }

        score += cV[creatureCnt[SELF][FILE_1]] + cV[creatureCnt[SELF][FILE_2]];
        score += gV[guardCnt[SELF][FILE_1]] + gV[guardCnt[SELF][FILE_2]];

        for (auto sq : oppo)
        {
                auto card = pos.board_on(sq);
                if (isExist(card))
                {
                        ++creatureCnt[OPPONENT][file_of(sq)];
                        if (isAbility(card, Guard))
                                ++guardCnt[OPPONENT][file_of(sq)];

                        score -= evaluate(card);
                }
        }

        score -= cV[creatureCnt[OPPONENT][FILE_1]] + cV[creatureCnt[OPPONENT][FILE_2]];
        score -= gV[guardCnt[OPPONENT][FILE_1]] + gV[guardCnt[OPPONENT][FILE_2]];

        return score;
}

void Search::search_draft(input_t input, int *Hand)
{
        const int Goal[8] = {4, 4, 8, 3, 3, 2, 1, 1};

        ASSERT(input.cardCount == 3);

        int select = 0, max = -1e+05;

        for (int i = 0; i < 3; ++i)
        {
                int index = std::min(input.cards[i].cost, 7);
                int w1 = evaluate(input.cards[i]);
                int w2 = 4 * (Goal[index] - Hand[index]);
                int w3 = 3 * std::max(10 - input.cards[i].cost, 0);

                std::cerr << w1 + w2 + w3 << " (" << w1 << " + " << w2 << " + " << w3 << ")" << std::endl;

                if (max < w1 + w2 + w3)
                {
                        select = i,
                        max = w1 + w2 + w3;
                }
        }

        int index = std::min(input.cards[select].cost, 7);
        ++Hand[index];

        std::cout << "PICK " << select << std::endl;
}

int Search::search_self_node(Position &pos, Move &best, int depth, int alpha)
{
        if (depth <= 0)
                return search_opponent_node(pos, best, alpha);

        MoveList<LEGAL> ml(pos);

        if (ml.size() == 0)
                return search_opponent_node(pos, best, alpha);

        //std::cerr << ml.size() << endl;

        int max = -VALUE_WIN;
        for (auto m : ml)
        {
                StateInfo si;

                if (!isExist(pos.board_on(move_from(m))))
                        continue;

                pos.do_move(m, si);

                Move move;
                int value = search_self_node(pos, move, depth - 1, alpha);

                if (value > alpha)
                        alpha = value;
                if (max < value)
                {
                        max = value;
                        best = m;
                }
                pos.undo_move(m);
        }

        return max;
}

int Search::search_opponent_node(Position &pos, Move &best, int alpha)
{
        // --- opponent search
        // depth == 1

        ASSERT(pos.side_to_move() == SELF);

        pos.flip_turn();

        int min = VALUE_WIN;
        MoveList<ATTACK> ml(pos);

        for (auto m : ml)
        {
                StateInfo si;
                pos.do_move(m, si);

                int value = evaluate(pos);
                if (value < min)
                        min = value;

                pos.undo_move(m);

                if (alpha >= value)
                {
                        pos.flip_turn();
                        return alpha;
                }
        }

        pos.flip_turn();
        return min;
}

bool Search::check_mate(const Position &pos)
{
        bool attack[2];
        attack[FILE_1] = attack[FILE_2] = true;

        Square sq;
        auto enemy = pos.cards(OPPONENT);
        FOREACH_BB(enemy, sq, {
                Card card = pos.board_on(sq);
                if (isAbility(card, Guard))
                        attack[file_of(sq)] = false;
        });

        int sum = 0;
        auto occ = pos.cards(SELF) & FIELD_BB;
        FOREACH_BB(occ, sq, {
                if (attack[file_of(sq)])
                {
                        Card card = pos.board_on(sq);
                        sum += card.attack;
                }
        });

        return sum >= pos.playerHealth(OPPONENT);
}

void Search::search_battle(Position &pos)
{
        OutputList output;

        if (check_mate(pos))
        {
                MoveList<ATTACK> ml(pos);
                for (auto m : ml)
                {
                        if (move_to(m) == SQ_PLAYER)
                                output.push_back(pos.make_output(m));
                }
                std::cout << output << std::endl;
                return;
        }

        while (true)
        {
                int alpha = -VALUE_WIN;
                Move best = MOVE_PASS;
                search_self_node(pos, best, SEARCH_DEPTH, alpha);

                //std::cerr << "bestMove = " << best << std::endl;
                if (best == MOVE_PASS)
                        break;

                output.push_back(pos.make_output(best));

                //std::cerr << "<------" << std::endl;
                //std::cerr << pos;
                StateInfo si;
                pos.do_move(best, si);
                //std::cerr << "------>" << std::endl;
                //std::cerr << pos << std::endl;
        }

        std::cerr << evaluate(pos) << std::endl;

        std::cout << output << std::endl;
}

int main()
{
        input_t input;
        Bitboards::init();

        int Hand[8] = {};

        // Draft
        for (int i = 0; i < 30; ++i)
        {
                std::cin >> input;
                Search::search_draft(input, Hand);
        }

        // Battle
        Position pos;
        while (true)
        {
                std::cin >> input;
                pos.set_turn(input);
                Search::search_battle(pos);
        }
}