namespace LOCM
{
    using System;
    using System.Diagnostics;

    internal class Program
    {
        // TODO: high value on drain when summoning without attack -- waste! https://www.codingame.com/share-replay/572771593
        // TODO: two-turn lethal: https://www.codingame.com/share-replay/572227621
        // TODO: two-turn lethal, play a bit defensively: https://www.codingame.com/share-replay/572756457
        // TODO: implement player lethal detection: https://www.codingame.com/share-replay/572165591 | https://www.codingame.com/share-replay/572187916
        // TODO: consider 4/4 boar play: https://www.codingame.com/replay/572539227
        // TODO: fix error: https://www.codingame.com/replay/572539915 (playing shield when guaranteed to lose it)
        // TODO: add dynamic card value

        // TODO: verify all weights! MAJOR
        // TODO: implement card value: https://www.codingame.com/share-replay/572190180
        // TODO: consider mana cost >= 9 useless?
        // TODO: write more tests for breakthrough / available damage
        private static void Main(string[] args)
        {
            var agentStrategy = args.Length == 0 || args[0].ToLower() != "aggresive" ? AgentFactory.AgentStrategy.Default : AgentFactory.AgentStrategy.Aggresive;
            Console.Error.WriteLine($"using strategy: {agentStrategy}");
            var agent = AgentFactory.GetAgent(agentStrategy);
            var gameInputReader = new GameInputReader();
            while (true)
            {
                gameInputReader.ReadTurnInput();
                var stopwatch = Stopwatch.StartNew();
                var result = agent.Think(gameInputReader.GetGameState());
                stopwatch.Stop();
                Console.Error.WriteLine($"time: {stopwatch.ElapsedMilliseconds}ms");
                Console.WriteLine(result);
            }
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Linq;

    public class Agent
    {
        private readonly List<AgentModule> _agentModules;

        public Agent(List<AgentModule> modules)
        {
            _agentModules = modules;
        }

        public string Think(GameState gameState)
        {
            var actions = new List<string>();
            foreach (var module in _agentModules)
            {
                var moduleResult = module.Execute(gameState);
                actions.AddRange(moduleResult);
                if (module.IsFinalResult && moduleResult.Any())
                {
                    break;
                }
            }
            if (!actions.Any()) actions.Add("PASS");
            return string.Join(";", actions);
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;

    public class GameInputReader
    {
        public static IReadOnlyDictionary<int, CardType> CardTypeMapping = new Dictionary<int, CardType>
        {
            [0] = CardType.Creature,
            [1] = CardType.Green,
            [2] = CardType.Red,
            [3] = CardType.Blue,
        };

        private int Turn = 0;
        private bool? IsPlayerSecond;
        private GameState GameState;

        public void ReadTurnInput()
        {
            Turn++;
            string[] inputs;
            Player player = null;
            Player opponent = null;
            Stopwatch stopwatch = new Stopwatch();
            for (int i = 0; i < 2; i++)
            {
                inputs = ReadLine().Split(' ');
                int playerHealth = int.Parse(inputs[0]);
                stopwatch.Restart();
                int playerMana = int.Parse(inputs[1]);
                int playerDeck = int.Parse(inputs[2]);
                int playerRune = int.Parse(inputs[3]);
                int playerDraw = int.Parse(inputs[4]);
                if (i == 0)
                {
                    player = new Player
                    {
                        Health = playerHealth,
                        Mana = playerMana,
                        RemainingCards = playerDeck,
                        Rune = playerRune,
                        CardsDraw = playerDraw
                    };
                }
                else
                {
                    opponent = new Player
                    {
                        Health = playerHealth,
                        Mana = playerMana,
                        RemainingCards = playerDeck,
                        Rune = playerRune,
                        CardsDraw = playerDraw
                    };
                }
            }
            inputs = ReadLine().Split(' ');
            int opponentHand = int.Parse(inputs[0]);
            int opponentActions = int.Parse(inputs[1]);
            List<int> opponentCardNumbers = new List<int>();
            for (int i = 0; i < opponentActions; i++)
            {
                string cardNumberAndAction = ReadLine();
                int opponentCardNumber = int.Parse(cardNumberAndAction.Split(" ")[0]);
                opponentCardNumbers.Add(opponentCardNumber);
            }
            int cardCount = int.Parse(ReadLine());
            var playerCards = new List<Card>();
            var playerCreatures = new List<Creature>();
            var opponentCreatures = new List<Creature>();
            for (int i = 0; i < cardCount; i++)
            {
                inputs = ReadLine().Split(' ');
                var cardNumber = int.Parse(inputs[0]);
                var instanceId = int.Parse(inputs[1]);
                var location = int.Parse(inputs[2]);
                var cardType = CardTypeMapping[int.Parse(inputs[3])];
                var cost = int.Parse(inputs[4]);
                var attack = int.Parse(inputs[5]);
                var defense = int.Parse(inputs[6]);
                var abilities = inputs[7].Replace("-", "");
                var myHealthChange = int.Parse(inputs[8]);
                var opponentHealthChange = int.Parse(inputs[9]);
                var cardDraw = int.Parse(inputs[10]);
                var lane = int.Parse(inputs[11]);
                if (location == 0)
                {
                    var card = new Card(cardType, cost, attack, defense, abilities, cardDraw, myHealthChange, opponentHealthChange, instanceId, cardNumber);
                    playerCards.Add(card);
                }
                else if (location == 1)
                {
                    var creature = new Creature(attack, defense, abilities, instanceId, lane);
                    playerCreatures.Add(creature);
                }
                else if (location == -1)
                {
                    var creature = new Creature(attack, defense, abilities, instanceId, lane);
                    opponentCreatures.Add(creature);
                }
            }
            if (IsPlayerSecond == null)
            {
                IsPlayerSecond = player.RemainingCards < opponent.RemainingCards;
            }
            player.IsSecond = IsPlayerSecond.Value;
            player.HandCardsCount = playerCards.Count;
            opponent.IsSecond = !IsPlayerSecond.Value;
            opponent.HandCardsCount = opponentHand;

            if (player.IsSecond && player.Mana == 2)
            {
                player.Mana--;
            }

            GameState = new GameState(playerCreatures, opponentCreatures, playerCards, player, opponent, Turn, opponentCardNumbers, stopwatch);
        }

        private string ReadLine()
        {
            var line = Console.ReadLine();
            return line;
        }

        public GameState GetGameState()
        {
            return GameState;
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Linq;

    public class GameState
    {
        public const int LaneCount = 2;
        public const int LaneSize = 3;

        public int Turn;
        public bool AttackerAttacked = false;
        public List<Creature> Attackers;
        public List<Creature> Defenders;
        public List<Card> Cards;
        public List<Card> UseCards;
        public Player Attacker;
        public Player Defender;
        public List<int> OpponentCardNumbers;
        public Stopwatch Stopwatch;
        public bool[] AttackerLanesFull;
        public bool[] AttackerLanesFree;
        public int AdditionalScore;

        public GameState(List<Creature> attackers, List<Creature> defenders, List<Card> cards, Player attacker, Player defender, int turn, List<int> opponentCardNumbers, Stopwatch stopwatch)
        {
            Turn = turn;
            Attackers = attackers;
            Defenders = defenders;
            Cards = cards;
            Attacker = attacker;
            Defender = defender;
            OpponentCardNumbers = opponentCardNumbers; // TODO: do not copy -- waste of time!
            Stopwatch = stopwatch;

            AttackerLanesFull = new bool[LaneCount];
            AttackerLanesFree = new bool[LaneCount];
            for (var i = 0; i < LaneCount; i++)
            {
                var laneAttackers = Attackers.Count(a => a.Lane == i);
                if (laneAttackers >= LaneSize) AttackerLanesFull[i] = true;
            }
            UseCards = new List<Card>();
        }

        public GameState(GameState gameState)
        {
            Turn = gameState.Turn;
            AttackerAttacked = gameState.AttackerAttacked;
            Attackers = gameState.Attackers.Select(attacker => new Creature(attacker)).ToList();
            Defenders = gameState.Defenders.Select(defender => new Creature(defender)).ToList();
            Cards = gameState.Cards.Select(card => new Card(card)).ToList();
            Attacker = gameState.Attacker == null ? null : new Player(gameState.Attacker);
            Defender = gameState.Defender == null ? null : new Player(gameState.Defender);
            Stopwatch = gameState.Stopwatch;

            AttackerLanesFull = new bool[LaneCount];
            AttackerLanesFree = new bool[LaneCount];
            for (var i = 0; i < LaneCount; i++)
            {
                AttackerLanesFull[i] = gameState.AttackerLanesFull[i];
                AttackerLanesFree[i] = gameState.AttackerLanesFree[i];
            }
            AdditionalScore = gameState.AdditionalScore;
            UseCards = gameState.UseCards.Select(card => new Card(card)).ToList();
        }

        public void UpdateTo(GameState gameState)
        {
            Turn = gameState.Turn;
            AttackerAttacked = gameState.AttackerAttacked;
            Attackers = gameState.Attackers;
            Defenders = gameState.Defenders;
            Cards = gameState.Cards;
            Attacker = gameState.Attacker;
            Defender = gameState.Defender;
            Stopwatch = gameState.Stopwatch;
        }

        public GameState SwitchSideNoCards()
        {
            var defenders = new List<Creature>(Defenders.Select(defender => new Creature(defender))).ToList();
            var attackers = new List<Creature>(Attackers.Select(attacker => new Creature(attacker))).ToList();
            return new GameState(defenders, attackers, new List<Card>(), Defender, Attacker, Turn, null, Stopwatch);
        }

        public GameState SwitchSide()
        {
            var defenders = new List<Creature>(Defenders.Select(defender => new Creature(defender))).ToList();
            var attackers = new List<Creature>(Attackers.Select(attacker => new Creature(attacker))).ToList();
            var cards = new List<Card>(Cards.Select(card => new Card(card))).ToList();
            return new GameState(defenders, attackers, cards, Defender, Attacker, Turn, null, Stopwatch);
        }

        public override string ToString()
        {
            return $"A: {string.Join(", ", Attackers)} D: {string.Join(", ", Defenders)} C: {Cards.Count} HP: att={Attacker.Health} def={Defender.Health}";
        }
    }
}
namespace LOCM
{
    using System.Linq;

    public class GameStateKey : IGameStateKey
    {
        public string GetKey(GameState gameState)
        {
            var attackers = gameState.Attackers.Select(attacker => attacker.CreatureKey()).OrderBy(attacker => attacker);
            var defenders = gameState.Defenders.Select(defender => defender.CreatureKey()).OrderBy(defender => defender);
            var cards = gameState.Cards.Select(card => card.InstanceId).OrderBy(x => x);
            return string.Join(", ", attackers) + " || " + string.Join(", ", defenders) + " || " + string.Join(", ", cards) + " || " + gameState.AdditionalScore;
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;

    public abstract class AgentModule : IDebug
    {
        public bool Debug { get; set; } = false;
        public bool IsFinalResult { get; set; } = false;

        public void DebugMessage(string message)
        {
            if (Debug) Console.Error.WriteLine(message);
        }

        public List<string> Execute(GameState gameState)
        {
            return ExecuteModule(gameState);
        }

        protected abstract List<string> ExecuteModule(GameState gameState);
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Linq;

    public class AttackModule : AgentModule
    {
        public bool AlwaysAttack { get; set; } = false;
        public int CreaturesAdvantage { get; set; } = 4;

        protected override List<string> ExecuteModule(GameState gameState)
        {
            var actions = new List<string>();
            var attackers = gameState.Attackers.Where(attacker => !attacker.Attacked).ToList();

            if (AlwaysAttack)
            {
                actions.AddRange(AvailableAttackActions(gameState));
                return actions;
            }

            var availableDamage = attackers.Sum(attacker => attacker.Attack);
            var creaturesAdvantage = gameState.Attackers.Count - gameState.Defenders.Count;
            var cardsLimitReached = gameState.Defender.HandCardsCount + gameState.Defender.CardsDraw >= 8;
            var creaturesAdvantageReached = creaturesAdvantage >= CreaturesAdvantage;
            var cardsExhausted = gameState.Defender.RemainingCards <= gameState.Defender.CardsDraw;
            var overwhelmingAttack = availableDamage >= gameState.Defender.Health / 2;
            var noDanger = gameState.Defender.Health - availableDamage >= gameState.Defender.Rune;
            DebugMessage($"oppRem: {gameState.Defender.RemainingCards} cardDraw: {gameState.Defender.CardsDraw}");
            if (cardsLimitReached || creaturesAdvantageReached || cardsExhausted || overwhelmingAttack || noDanger)
            {
                actions.AddRange(AvailableAttackActions(gameState));
            }
            return actions;
        }

        private List<string> AvailableAttackActions(GameState gameState)
        {
            var actions = new List<string>();
            for (var i = 0; i < GameState.LaneCount; i++)
            {
                var laneAttackers = gameState.Attackers.Where(attacker => !attacker.Attacked && attacker.Lane == i).ToList();
                var laneGuardians = gameState.Defenders.Where(defender => defender.Guard && defender.Lane == i).ToList();
                if (laneGuardians.Any()) continue;
                foreach (var attacker in laneAttackers)
                {
                    actions.Add($"ATTACK {attacker.InstanceId} -1");
                }
            }
            return actions;
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;

    public class DeckTracking : AgentModule
    {
        private readonly DeckTracker DeckTracker;
        private bool CardsInitialized = false;

        public DeckTracking(DeckTracker deckTracker)
        {
            DeckTracker = deckTracker;
        }

        protected override List<string> ExecuteModule(GameState gameState)
        {
            if (gameState.Attacker.Mana == 0)
            {
                var playerCards = gameState.Cards;
                DeckTracker.PickCard(playerCards);
            }
            else
            {
                if (!CardsInitialized)
                {
                    DeckTracker.AssignRemainingCardsFromPickedCards();
                    CardsInitialized = true;
                }
                DebugMessage($"opponentCardsUsed: {string.Join(" ", gameState.OpponentCardNumbers)}");
                foreach (var cardNumber in gameState.OpponentCardNumbers)
                {
                    DeckTracker.UseCard(cardNumber);
                }
                if (Debug) DeckTracker.DebugInfo();
            }
            return new List<string>();
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class Draft : AgentModule
    {
        public enum DraftStrategy
        {
            Default,
            Basic,
            Refined,
            Experimental,
        }

        private static readonly List<int> FirstPlayerCardOrdering = @"116 68 151 51 65 80 7 53 29 37 67 32 139 69 49 33 66 147 18 152 28 48 82 88 23 84 52 44 87 148 99 121 64 85 103 141 158 50 95 115 133 19 109 54 157 81 150 21 34 36 135 134 70 3 61 111 75 17 144 129 145 106 9 105 15 114 128 155 96 11 8 86 104 97 41 12 26 149 90 6 13 126 93 98 83 71 79 72 73 77 59 100 137 5 89 142 112 25 62 125 122 74 120 159 22 91 39 94 127 30 16 146 1 45 38 56 47 4 58 118 119 40 27 35 101 123 132 2 136 131 20 76 14 43 102 108 46 60 130 117 140 42 124 24 63 10 154 78 31 57 138 107 113 55 143 92 156 110 160 153".Split(" ").Select(x => int.Parse(x)).ToList();
        private static readonly List<int> SecondPlayerCardOrdering = @"116 68 151 51 65 7 80 53 29 37 67 32 139 69 49 33 66 147 18 152 28 48 82 88 23 84 52 44 87 148 99 121 64 85 103 141 158 50 95 96 133 8 109 19 150 5 157 21 34 36 135 134 3 6 26 111 75 17 144 129 145 106 9 105 15 114 128 155 115 11 54 86 104 97 41 12 61 149 90 70 13 126 93 98 83 71 79 72 73 77 59 81 137 100 89 142 112 25 62 125 122 74 120 159 22 91 39 94 127 30 16 146 1 45 38 56 47 4 58 118 119 40 27 35 101 123 132 2 136 131 20 76 14 43 102 108 46 60 130 117 140 42 124 24 63 10 154 78 31 57 138 107 113 55 143 92 156 110 160 153".Split(" ").Select(x => int.Parse(x)).ToList();
        private static readonly List<int> RefinedCardOrdering = @"116 68 151 51 80 53 65 7 37 67 32 139 69 49 18 66 147 33 152 48 88 23 84 52 44 82 87 148 99 64 85 103 141 158 50 95 115 133 19 109 54 157 150 21 75 76 43 135 124 134 34 70 3 61 111 17 144 129 145 106 9 105 15 114 128 155 96 11 127 122 8 86 104 97 41 12 10 26 142 149 90 137 126 125 120 119 130 121 42 81 29 6 98 40 93 39 13 83 71 36 79 72 73 77 59 100 28 5 89 112 46 62 74 159 22 91 94 30 16 146 1 45 38 56 47 4 58 118 27 35 101 123 132 2 136 131 20 14 102 108 60 117 140 25 24 63 154 78 31 57 138 107 113 55 143 92 110 156 160 153".Split(" ").Select(x => int.Parse(x)).ToList();
        private static readonly List<int> ExperimentalCardOrdering = @"68 151 51 80 53 65 7 37 67 32 139 69 49 18 66 147 33 152 48 88 23 84 52 44 82 87 148 99 64 85 103 141 158 50 95 115 133 19 109 54 157 150 21 75 76 43 124 134 135 34 70 3 111 17 144 129 145 106 9 105 15 114 128 155 96 11 127 122 8 86 104 97 41 12 10 26 63 142 149 90 137 126 125 120 119 130 121 42 29 6 98 40 93 39 13 71 74 110 36 72 73 77 59 100 5 28 89 112 159 22 91 94 30 16 146 1 45 38 56 47 4 58 118 27 35 101 123 132 2 136 131 20 14 102 108 60 117 140 154 78 116 62 81 79 61 46 83 25 31 57 24 138 107 113 55 143 92 156 160 153".Split(" ").Select(x => int.Parse(x)).ToList();
        private static readonly List<int> DefaultCardOrdering = @"116 68 151 51 65 80 7 53 29 37 67 32 139 69 49 33 66 147 18 152 28 48 82 88 23 84 52 44 87 148 99 121 64 85 103 141 158 50 95 115 133 19 109 54 157 81 150 21 34 36 135 134 70 3 61 111 75 17 144 129 145 106 9 105 15 114 128 155 96 11 8 86 104 97 41 12 26 149 90 6 13 126 93 98 83 71 79 72 73 77 59 100 137 5 89 142 112 25 62 125 122 74 120 159 22 91 39 94 127 30 16 146 1 45 38 56 47 4 58 118 119 40 27 35 101 123 132 2 136 131 20 76 14 43 102 108 46 60 130 117 140 42 124 24 63 10 154 78 31 57 138 107 113 55 143 92 156 110 160 153".Split(" ").Select(x => int.Parse(x)).ToList();

        public bool DefaultStrategy { get; set; } = false;
        public bool UseNewStrategy { get; set; } = true;
        private readonly DraftStrategy _draftStrategy;

        public Draft(DraftStrategy draftStrategy)
        {
            _draftStrategy = draftStrategy;
        }

        protected override List<string> ExecuteModule(GameState gameState)
        {
            var pickedCard = PickCard(gameState);
            return pickedCard != null ? new List<string> { pickedCard } : new List<string>();
        }

        private string PickCard(GameState gameState)
        {
            if (gameState.Attacker.Mana != 0) return null;

            var playerCards = gameState.Cards;
            var cardOrdering = GetCardOrdering(gameState);
            if (!DefaultStrategy && !UseNewStrategy) cardOrdering = gameState.Attacker.IsSecond ? SecondPlayerCardOrdering : FirstPlayerCardOrdering;
            var cards = playerCards.Select((card, idx) => new { idx, card }).OrderBy(card => cardOrdering.IndexOf(card.card.CardNumber)).ToList();
            var bestCardIndex = cards.First().idx;
            return $"PICK {bestCardIndex}";
        }

        private List<int> GetCardOrdering(GameState gameState)
        {
            switch (_draftStrategy)
            {
                case DraftStrategy.Default:
                    return DefaultCardOrdering;

                case DraftStrategy.Basic:
                    return gameState.Attacker.IsSecond ? SecondPlayerCardOrdering : FirstPlayerCardOrdering;

                case DraftStrategy.Refined:
                    return RefinedCardOrdering;

                case DraftStrategy.Experimental:
                    return ExperimentalCardOrdering;

                default:
                    throw new ArgumentException($"invalid draftStrategy: {_draftStrategy}");
            }
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Linq;

    public class OpponentLethalModule : AgentModule
    {
        private readonly ActionsProvider _actionsProvider;
        private readonly ActionsHandler _actionsHandler;
        private readonly IGameStateKey _gameStateKey;
        public int LethalAdditionalDamage { get; set; }
        public int LethalDamage { get; private set; }

        public OpponentLethalModule(ActionsProvider actionsProvider, ActionsHandler actionsHandler, IGameStateKey gameStateKey)
        {
            _actionsProvider = actionsProvider;
            _actionsHandler = actionsHandler;
            _gameStateKey = gameStateKey;
        }

        protected override List<string> ExecuteModule(GameState gameState)
        {
            var stopwatch = Stopwatch.StartNew();
            var lethal = CheckLethal(gameState, _gameStateKey);
            stopwatch.Stop();
            DebugMessage($"lethal time: {stopwatch.ElapsedMilliseconds}ms");
            if (lethal.Any())
            {
                DebugMessage("lethal found!");
            }
            return lethal;
        }

        private List<string> CheckLethal(GameState initialGameState, IGameStateKey gameStateKey)
        {
            var result = new List<string>();
            var keys = new HashSet<string>();
            var gameStates = new Stack<(GameState, List<string>)>();
            gameStates.Push((new GameState(initialGameState), new List<string>()));
            while (gameStates.Count > 0)
            {
                var item = gameStates.Pop();
                var gameState = item.Item1;
                var moves = item.Item2;

                var key = gameStateKey.GetKey(gameState);
                if (keys.Contains(key)) continue;
                keys.Add(key);

                var attackers = gameState.Attackers.Where(attacker => !attacker.Attacked).ToList();
                var laneGuardians = Enumerable.Range(0, GameState.LaneCount).Select(x => gameState.Defenders.Any(defender => defender.Guard && defender.Lane == x)).ToList();
                var totalAttack = LethalAdditionalDamage;
                for (var i = 0; i < GameState.LaneCount; i++)
                {
                    var laneAttackers = attackers.Where(attacker => attacker.Lane == i).ToList();
                    var laneAttackersAttack = laneAttackers.Sum(attacker => attacker.Attack);
                    if (laneGuardians[i]) continue;
                    totalAttack += laneAttackersAttack;
                }
                if (gameState.Defender.IsDead(totalAttack))
                {
                    LethalDamage = totalAttack;
                    result.AddRange(moves);
                    foreach (var attacker in attackers)
                    {
                        if (attacker.Attacked || laneGuardians[attacker.Lane]) continue;

                        result.Add($"ATTACK {attacker.InstanceId} -1");
                    }
                    return result;
                }

                var actions = _actionsProvider.AvailableLethalActions(gameState);
                foreach (var action in actions)
                {
                    var newGameState = new GameState(gameState);
                    _actionsHandler.ExecuteAction(newGameState, action);
                    gameStates.Push((newGameState, new List<string>(moves) { action }));
                }
            }
            return result;
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;

    public class SimulationModule : AgentModule
    {
        private readonly GameStateSimulation _simulation;
        private readonly SelectiveActionsProvider _actionsProvider;
        private readonly ActionsHandler _actionsExecutor;
        private readonly GameStatesEvaluator _gameStatesEvaluator;
        private readonly IGameStateKey _gameStateKey;

        public SimulationModule(GameStateSimulation simulation, SelectiveActionsProvider actionsProvider, ActionsHandler actionsExecutor, GameStatesEvaluator gameStatesEvaluator, IGameStateKey gameStateKey)
        {
            _simulation = simulation;
            _actionsProvider = actionsProvider;
            _actionsExecutor = actionsExecutor;
            _gameStatesEvaluator = gameStatesEvaluator;
            _gameStateKey = gameStateKey;
        }

        protected override List<string> ExecuteModule(GameState gameState)
        {
            if (gameState.Attacker.Mana <= 0) return new List<string>();

            _simulation.Reset();
            var (actions, bestGameState) = _simulation.Simulate(gameState, _actionsProvider, _actionsExecutor,
                _gameStatesEvaluator, _gameStateKey, gameState.Stopwatch);
            bestGameState.AttackerAttacked = false;
            gameState.UpdateTo(bestGameState);
            DebugMessage($"finalGameState: {gameState}");
            return actions;
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;

    public static class AgentFactory
    {
        public enum AgentStrategy
        {
            Default,
            Aggresive
        }

        public static Agent GetAgent(AgentStrategy agentStrategy)
        {
            switch (agentStrategy)
            {
                case AgentStrategy.Default:
                    return CreateDefaultAgent();

                case AgentStrategy.Aggresive:
                    return CreateAggresiveAgent();

                default:
                    throw new ArgumentException("invalid");
            }
        }

        private static Agent CreateAgent((IGameStateScorer, IGameStateScorer) scorers)
        {
            var gameStateKey = new GameStateKey();
            var (playerGameStateScorer, opponentGameStateScorer) = scorers;
            var gameActionScorer = new GameActionScorer();
            var opponentGameActionScorer = new GameActionScorer();
            var actionsProvider = new SelectiveActionsProvider(gameActionScorer, 3);
            var lethalActionsProvider = new SelectiveActionsProvider(gameActionScorer, 15);
            var opponentActionsProvider = new SelectiveActionsProvider(opponentGameActionScorer, 3);
            var actionsHandler = new ActionsHandler();
            var gameStatesEvaluator = new GameStatesEvaluator(opponentActionsProvider, actionsHandler,
                playerGameStateScorer, opponentGameStateScorer, gameStateKey, true, 2)
            {
                Debug = false,
            };
            var simulation = new GameStateSimulation()
            {
                Experimental = true,
                Debug = true,
                CombinationsCountLimit = 45,
                TimeLimit = 185,
                MaxTimeLimit = 190
            };
            var deckDraft = new DeckDraft();
            var deckTracker = new DeckTracker(deckDraft);
            var modules = new List<AgentModule>
            {
                new DeckTracking(deckTracker),
                new Draft(Draft.DraftStrategy.Experimental) { IsFinalResult = true },
                new OpponentLethalModule(lethalActionsProvider, actionsHandler, gameStateKey) { Debug = true, IsFinalResult = true },
                new SimulationModule(simulation, actionsProvider, actionsHandler, gameStatesEvaluator, gameStateKey) { Debug = true },
                new AttackModule() { AlwaysAttack = true }
            };
            var agent = new Agent(modules);
            return agent;
        }

        private static Agent CreateDefaultAgent()
        {
            return CreateAgent(ScorersFactory.GetScorers(ScorersFactory.ScorersStrategy.Default));
        }

        private static Agent CreateAggresiveAgent()
        {
            return CreateAgent(ScorersFactory.GetScorers(ScorersFactory.ScorersStrategy.Aggresive));
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class OneLaneStrategy : IGameStateScorer
    {
        private const int DefenseLimit = 7;
        public int AttackWeight { get; set; }
        public int DefenseWeight { get; set; }
        public int WardWeight { get; set; }
        public int LethalWeight { get; set; }
        public int DrainWeight { get; set; }
        public int BreakthroughWeight { get; set; }
        public int GuardWeight { get; set; }
        public int OpponentScoreMultiplier { get; set; }
        public int PlayerScoreMultiplier { get; set; }
        public int ClearLaneWeight { get; set; }
        public int DamageWeight { get; set; }
        public int UseCardWeight { get; set; }
        public double GameStateScore(GameState gameState)
        {
            var attackerScore = new List<double>();
            var attackerDamageAdvantage = gameState.Attackers.Sum(attacker => attacker.Attack) > gameState.Defenders.Sum(defender => defender.Attack);
            var defenderDamageAdvantage = gameState.Defenders.Sum(attacker => attacker.Attack) > gameState.Attackers.Sum(defender => defender.Attack);
            var laneDefenders = Enumerable.Range(0, GameState.LaneCount).Select(i => gameState.Defenders.Any(defender => defender.Guard && defender.Lane == i)).ToList();
            foreach (var attacker in gameState.Attackers)
            {
                var attackerCreatureScore = attacker.Attack * AttackWeight + attacker.Defense * DefenseWeight;
                attackerCreatureScore += attacker.Ward ? WardWeight : 0;
                attackerCreatureScore += attacker.Lethal ? LethalWeight : 0;
                attackerCreatureScore += attacker.Drain ? attacker.Attack * DrainWeight : 0;
                attackerCreatureScore += attacker.Breakthrough ? BreakthroughWeight : 0;
                attackerCreatureScore += attacker.Guard ? GuardWeight : 0;
                attackerCreatureScore += attackerDamageAdvantage && !attacker.Attacked && !laneDefenders[attacker.Lane] ? attacker.Attack * DamageWeight : 0;
                attackerScore.Add(attackerCreatureScore);
            }
            var defenderScore = new List<double>();
            foreach (var defender in gameState.Defenders)
            {
                var defenderCreatureScore = defender.Attack * AttackWeight + defender.Defense * DefenseWeight;
                defenderCreatureScore += defender.Ward ? WardWeight : 0;
                defenderCreatureScore += defender.Lethal ? LethalWeight : 0;
                defenderCreatureScore += defender.Drain ? defender.Attack * DrainWeight : 0;
                defenderCreatureScore += defender.Breakthrough ? BreakthroughWeight : 0;
                defenderCreatureScore += defender.Guard ? GuardWeight : 0;
                defenderScore.Add(defenderCreatureScore);
            }
            var remainingCardsBonus = gameState.Cards.Where(card => card.CardType != CardType.Creature).Sum(card => UseCardWeight == 0 ? 0 : UseCardWeight + Math.Min(DefenseLimit, Math.Abs(card.Defense)) * (UseCardWeight > 0 ? 1 : -1)) * PlayerScoreMultiplier;
            var useCardsBonus = UseCardWeight == 0 ? 0 : gameState.UseCards.Sum(card => -Math.Min(DefenseLimit, Math.Abs(card.Defense)));
            var totalAttackerScore = attackerScore.Sum() * PlayerScoreMultiplier;
            var totalDefenderScore = defenderScore.Sum() * OpponentScoreMultiplier;
            var attackerLaneBonus = GetLaneScore(gameState.Attackers, gameState.Defenders, ClearLaneWeight);
            var defenderLaneBonus = GetLaneScore(gameState.Defenders, gameState.Attackers, ClearLaneWeight);
            var values = new[] { totalAttackerScore, remainingCardsBonus, useCardsBonus, attackerLaneBonus, -totalDefenderScore, -defenderLaneBonus };
            var total = values.Sum();
            return total;
        }

        private int GetLaneScore(List<Creature> units, List<Creature> oppositeUnits, int score)
        {
            for (var i = 0; i < GameState.LaneCount; i++)
            {
                var laneUnits = units.Where(unit => unit.Lane == i).ToList();
                var laneOppositeUnits = oppositeUnits.Where(unit => unit.Lane == i).ToList();
                if (laneUnits.Any() && !laneOppositeUnits.Any()) return score;
            }
            return 0;
        }
    }
}
namespace LOCM
{
    using System;
    using System.Linq;

    public class ActionsHandler
    {
        public void ExecuteAction(GameState gameState, string action)
        {
            var inputs = action.Split(" ");
            switch (inputs[0])
            {
                case "ATTACK":
                    HandleAttackCommand(gameState, inputs);
                    break;
                case "SUMMON":
                    HandleSummonCommand(gameState, inputs);
                    break;
                case "USE":
                    HandleUseCommand(gameState, inputs);
                    break;
                default:
                    throw new Exception("Invalid action");
            }
        }

        private void HandleAttackCommand(GameState gameState, string[] inputs)
        {
            var attackerId = int.Parse(inputs[1]);
            var defenderId = int.Parse(inputs[2]);
            var attacker = gameState.Attackers.First(a => a.InstanceId == attackerId);
            if (defenderId == -1)
            {
                gameState.Defender.DealDamageToPlayer(attacker.Attack);
                attacker.Attacked = true;
            }
            else
            {
                var defender = gameState.Defenders.First(d => d.InstanceId == defenderId);

                if (attacker.Lane != defender.Lane)
                {
                    throw new ArgumentException($"invalid attack {attacker.InstanceId} ({attacker.Lane}) -> {defender.InstanceId} ({defender.Lane})");
                }

                var attackerDamage = defender.Ward ? 0 : attacker.Attack;
                var breakthroughDamage = attacker.Breakthrough ? Math.Max(attackerDamage - defender.Defense, 0) : 0;
                var drainDamage = attacker.Drain ? attackerDamage : 0;
                if (drainDamage > 0) gameState.AdditionalScore++;
                if (breakthroughDamage > 0) gameState.AdditionalScore++;
                gameState.Attacker.ModifyHealth(drainDamage);
                gameState.Defender.DealDamageToPlayer(breakthroughDamage);
                attacker.CreatureAttack(defender);
                if (!attacker.IsAlive)
                {
                    gameState.Attackers.Remove(attacker);

                    if (gameState.AttackerLanesFull[attacker.Lane])
                    {
                        gameState.AttackerLanesFree[attacker.Lane] = true;
                    }
                }
                if (!defender.IsAlive)
                {
                    gameState.Defenders.Remove(defender);
                }
            }
            gameState.AttackerAttacked = true;
        }

        private void HandleSummonCommand(GameState gameState, string[] inputs)
        {
            var cardId = int.Parse(inputs[1]);
            var lane = int.Parse(inputs[2]);
            var card = gameState.Cards.First(c => c.InstanceId == cardId);
            gameState.Attackers.Add(new Creature(card, !card.Charge, lane));
            gameState.Attacker.ModifyHealth(card.HealthChange);
            gameState.Defender.ModifyHealth(card.OpponentHealthChange);
            gameState.Attacker.Mana -= card.Cost;
            gameState.Cards.Remove(card);

            if (gameState.Attackers.Count(attacker => attacker.Lane == lane) >= 3)
            {
                gameState.AttackerLanesFull[lane] = true;
                gameState.AttackerLanesFree[lane] = false;
            }
        }

        private void HandleUseCommand(GameState gameState, string[] inputs)
        {
            var cardId = int.Parse(inputs[1]);
            var targetId = int.Parse(inputs[2]);
            var card = gameState.Cards.First(c => c.InstanceId == cardId);
            gameState.Attacker.Mana -= card.Cost;
            gameState.Cards.Remove(card);
            gameState.Attacker.ModifyHealth(card.HealthChange);
            gameState.Defender.ModifyHealth(card.OpponentHealthChange);

            gameState.UseCards.Add(card);

            if (card.CardType == CardType.Green)
            {
                var attacker = gameState.Attackers.First(a => a.InstanceId == targetId);
                card.UseGreen(attacker);
            }
            else if (card.CardType == CardType.Red)
            {
                var defender = gameState.Defenders.First(d => d.InstanceId == targetId);
                card.UseRed(defender);
                if (!defender.IsAlive)
                {
                    gameState.Defenders.Remove(defender);
                }
            }
            else if (card.CardType == CardType.Blue)
            {
                if (targetId != -1)
                {
                    var defender = gameState.Defenders.First(d => d.InstanceId == targetId);
                    card.UseBlue(defender);
                    if (!defender.IsAlive)
                    {
                        gameState.Defenders.Remove(defender);
                    }
                }
                else
                {
                    gameState.Defender.ModifyHealth(card.Defense);
                }
            }
            else
            {
                throw new Exception($"Invalid cardType: {card.CardType} for use");
            }
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class ActionsProvider : IDebug
    {
        public bool Debug { get; set; } = false;

        public void DebugMessage(string message)
        {
            if (Debug) Console.Error.WriteLine(message);
        }

        public List<string> AvailableActions(GameState gameState)
        {
            var result = new List<string>();

            if (!gameState.AttackerAttacked)
            {
                result.AddRange(AvailableSummonActions(gameState));
                result.AddRange(AvailableOffensiveActions(gameState));
                result.AddRange(AvailableDefensiveActions(gameState));
            }

            for (var i = 0; i < GameState.LaneCount; i++)
            {
                if (gameState.AttackerLanesFree[i])
                {
                    result.AddRange(AvailableSummonActions(gameState, i));
                }
            }
            result.AddRange(AvailableAttackActions(gameState));
            return result;
        }

        private List<string> AvailableDefensiveActions(GameState gameState)
        {
            var result = new List<string>();

            var cards = GetUniqueCards(gameState.Cards, gameState.Attacker.Mana);
            var offensiveCards = cards.Where(card => (card.CardType == CardType.Red || card.CardType == CardType.Blue) && card.Cost <= gameState.Attacker.Mana).ToList();
            foreach (var card in offensiveCards)
            {
                foreach (var defender in gameState.Defenders)
                {
                    result.Add($"USE {card.InstanceId} {defender.InstanceId}");
                }
            }
            return result;
        }

        private List<string> AvailableOffensiveActions(GameState gameState)
        {
            var result = new List<string>();

            var cards = GetUniqueCards(gameState.Cards, gameState.Attacker.Mana);
            var greenCards = cards.Where(card => card.CardType == CardType.Green && card.Cost <= gameState.Attacker.Mana).ToList();
            foreach (var card in greenCards)
            {
                foreach (var attacker in gameState.Attackers)
                {
                    result.Add($"USE {card.InstanceId} {attacker.InstanceId}");
                }
            }
            return result;
        }

        private List<string> AvailableSummonActions(GameState gameState)
        {
            var result = new List<string>();

            var cards = GetUniqueCards(gameState.Cards, gameState.Attacker.Mana);
            for (var i = 0; i < GameState.LaneCount; i++)
            {
                var laneAttackers = gameState.Attackers.Where(attacker => attacker.Lane == i).ToList();
                if (laneAttackers.Count >= GameState.LaneSize) continue;

                foreach (var card in cards)
                {
                    if (card.CardType == CardType.Creature && card.Cost <= gameState.Attacker.Mana)
                    {
                        result.Add($"SUMMON {card.InstanceId} {i}");
                    }
                }
            }
            return result;
        }

        private List<string> AvailableSummonActions(GameState gameState, int lane)
        {
            var result = new List<string>();

            var cards = GetUniqueCards(gameState.Cards, gameState.Attacker.Mana);
            var laneAttackers = gameState.Attackers.Where(attacker => attacker.Lane == lane).ToList();
            if (laneAttackers.Count >= GameState.LaneSize) return result;

            foreach (var card in cards)
            {
                if (card.CardType == CardType.Creature && card.Cost <= gameState.Attacker.Mana)
                {
                    result.Add($"SUMMON {card.InstanceId} {lane}");
                }
            }
            return result;
        }

        public virtual List<string> AvailableAttackActions(GameState gameState)
        {
            var result = new List<string>();

            var defenders = gameState.Defenders;
            var attackers = gameState.Attackers.Where(attacker => !attacker.Attacked).ToList();
            for (var i = 0; i < GameState.LaneCount; i++)
            {
                var laneAttackers = GetUniqueCreatures(attackers, i);
                var laneDefenders = GetUniqueCreatures(defenders, i);
                var guardians = laneDefenders.Where(defender => defender.Guard).ToList();
                laneDefenders = guardians.Any() ? guardians : laneDefenders;
                foreach (var attacker in laneAttackers)
                {
                    foreach (var defender in laneDefenders)
                    {
                        result.Add($"ATTACK {attacker.InstanceId} {defender.InstanceId}");
                    }
                }
            }
            return result;
        }

        // TODO: should change this! verify!
        public virtual List<string> AvailableLethalActions(GameState gameState)
        {
            List<string> result = new List<string>();
            var guardians = gameState.Defenders.Where(defender => defender.Guard).ToList();
            var attackers = gameState.Attackers.Where(attacker => !attacker.Attacked).ToList();
            foreach (var card in GetUniqueCards(gameState.Cards, gameState.Attacker.Mana))
            {
                if (card.CardType == CardType.Creature && (card.Charge || card.OpponentHealthChange < 0) && card.Cost <= gameState.Attacker.Mana)
                {
                    for (var i = 0; i < GameState.LaneCount; i++)
                    {
                        var laneAttackers = gameState.Attackers.Where(attacker => attacker.Lane == i).ToList();
                        if (laneAttackers.Count >= GameState.LaneSize) continue;
                        result.Add($"SUMMON {card.InstanceId} {i}");
                    }
                }
                if (card.CardType == CardType.Blue && card.Cost <= gameState.Attacker.Mana)
                {
                    foreach (var guardian in gameState.Defenders)
                    {
                        result.Add($"USE {card.InstanceId} {guardian.InstanceId}");
                    }
                    result.Add($"USE {card.InstanceId} -1");
                }
                if (guardians.Any() && card.CardType == CardType.Red && card.Cost <= gameState.Attacker.Mana)
                {
                    foreach (var guardian in guardians)
                    {
                        result.Add($"USE {card.InstanceId} {guardian.InstanceId}");
                    }
                }
                if (attackers.Any() && card.CardType == CardType.Green && card.Cost <= gameState.Attacker.Mana && (card.Attack > 0 || card.Lethal))
                {
                    foreach (var attacker in attackers)
                    {
                        result.Add($"USE {card.InstanceId} {attacker.InstanceId}");
                    }
                }
            }
            result.AddRange(AvailableGuardianAttackActions(gameState));
            return result;
        }

        public virtual List<string> AvailableGuardianAttackActions(GameState gameState)
        {
            var result = new List<string>();

            var defenders = gameState.Defenders;
            var attackers = gameState.Attackers.Where(attacker => !attacker.Attacked).ToList();
            for (var i = 0; i < GameState.LaneCount; i++)
            {
                var laneAttackers = GetUniqueCreatures(attackers, i);
                var laneDefenders = GetUniqueCreatures(defenders, i);
                var guardians = laneDefenders.Where(defender => defender.Guard).ToList();
                if (!guardians.Any()) continue;

                foreach (var attacker in laneAttackers)
                {
                    foreach (var defender in guardians)
                    {
                        result.Add($"ATTACK {attacker.InstanceId} {defender.InstanceId}");
                    }
                }
            }
            return result;
        }

        public static List<Card> GetUniqueCards(List<Card> cards, int availableMana)
        {
            var result = new List<Card>();
            var seen = new HashSet<int>();
            foreach (var card in cards.Where(card => card.Cost <= availableMana))
            {
                if (seen.Contains(card.CardNumber)) continue;
                seen.Add(card.CardNumber);
                result.Add(card);
            }
            return result;
        }

        public static List<Creature> GetUniqueCreatures(List<Creature> creatures)
        {
            var result = new List<Creature>();
            var seen = new HashSet<string>();
            foreach (var creature in creatures)
            {
                var creatureKey = $"{creature.Attack} {creature.Defense} {creature.GetAbilitiesString()}";
                if (seen.Contains(creatureKey)) continue;
                seen.Add(creatureKey);
                result.Add(creature);
            }
            return result;
        }

        public static List<Creature> GetUniqueCreatures(List<Creature> creatures, int lane)
        {
            var result = new List<Creature>();
            var seen = new HashSet<string>();
            foreach (var creature in creatures)
            {
                if (creature.Lane != lane) continue;
                var creatureKey = $"{creature.Attack} {creature.Defense} {creature.GetAbilitiesString()}";
                if (seen.Contains(creatureKey)) continue;
                seen.Add(creatureKey);
                result.Add(creature);
            }
            return result;
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Linq;

    public class SelectiveActionsProvider : ActionsProvider, IDebug
    {
        private readonly IGameActionScorer GameActionScorer;
        public int ActionsLimit { get; }

        public SelectiveActionsProvider(IGameActionScorer gameActionScorer, int actionsLimit)
        {
            GameActionScorer = gameActionScorer;
            ActionsLimit = actionsLimit;
        }
        private List<string> TrimActions(GameState gameState, List<string> actions)
        {
            return actions.OrderByDescending(action => GameActionScorer.GameActionScore(gameState, action))
                .Take(ActionsLimit)
                .ToList();
        }

        public override List<string> AvailableAttackActions(GameState gameState)
        {
            var attackActions = base.AvailableAttackActions(gameState);
            return TrimActions(gameState, attackActions);
        }

        public override List<string> AvailableLethalActions(GameState gameState)
        {
            var lethalActions = base.AvailableLethalActions(gameState);
            return TrimActions(gameState, lethalActions);
        }
    }
}
namespace LOCM
{
    using System.Linq;

    public class GameActionScorer : IGameActionScorer
    {
        public int AttackWeight { get; set; } = 10;
        public int DefenseWeight { get; set; } = 6;

        // TODO: optimize
        public int GameActionScore(GameState gameState, string gameAction)
        {
            var parts = gameAction.Split(" ");

            switch (parts[0])
            {
                case "ATTACK":
                    return HandleAttackCommand(gameState, parts);

                default:
                    return 0;
            }
        }

        private int HandleAttackCommand(GameState gameState, string[] parts)
        {
            var sourceId = int.Parse(parts[1]);
            var targetId = int.Parse(parts[2]);
            var attacker = gameState.Attackers.First(a => a.InstanceId == sourceId);
            var defender = gameState.Defenders.First(d => d.InstanceId == targetId);
            return attacker.Ward || (attacker.Defense > defender.Attack && !defender.Lethal) ? defender.Attack * AttackWeight + defender.Defense * DefenseWeight : 0;
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Linq;

    public class GameStateSimulation
    {
        public void DebugMessage(string message)
        {
            if (Debug) Console.Error.WriteLine(message);
        }

        public bool Debug { get; set; } = false;
        public bool Experimental { get; set; } = false;
        public int TimeLimit { get; set; } = 190;
        public int MaxTimeLimit { get; set; } = 190;
        public int? CombinationsCountLimit { get; set; } = null;

        public int Iterations = 0;

        public void Reset()
        {
            Iterations = 0;
        }

        public (List<string>, GameState) Simulate(GameState initialGameState, SelectiveActionsProvider actionsProvider, ActionsHandler actionsExecutor, GameStatesEvaluator gameStatesEvaluator, IGameStateKey gameStateKey, Stopwatch stopwatch)
        {
            var cards = initialGameState.Cards;
            if (Experimental && initialGameState.Attacker.RemainingCards <= 2)
            {
                cards = cards.Where(card => card.CardDraw <= 0 || card.Cost >= 8).ToList();
            }
            var combinations = SummonCombinations.GetDominatingCardsCombinations(cards, initialGameState.Attacker.Mana);
            if (CombinationsCountLimit.HasValue) combinations.Take(CombinationsCountLimit.Value);
            combinations.Add(new List<Card>());
            var results = new List<Tuple<List<string>, GameState>>();
            foreach (var combination in combinations)
            {
                if (stopwatch?.ElapsedMilliseconds > TimeLimit)
                {
                    DebugMessage("EARLY BREAK COMBO");
                    break;
                }
                var gameState = new GameState(initialGameState);
                var actions = new List<string>();
                gameState.Cards = combination;
                var result = SimulateState(gameState, actionsProvider, actionsExecutor, gameStatesEvaluator, gameStateKey, stopwatch);
                result.Item1.AddRange(actions);
                results.Add(result);
            }
            gameStatesEvaluator.Reset();
            var resultCount = 0;
            foreach (var result in results)
            {
                resultCount++;
                gameStatesEvaluator.AddGameState(result.Item2, result.Item1);
                if (stopwatch?.ElapsedMilliseconds > MaxTimeLimit)
                {
                    break;
                }
            }
            if (stopwatch?.ElapsedMilliseconds > TimeLimit)
            {
                DebugMessage($"checked {resultCount}/{results.Count} final states");
                DebugMessage("EARLY BREAK FINAL");
            }
            var bestActions = gameStatesEvaluator.GetBestActions();
            var bestGameState = gameStatesEvaluator.GetBestGameState();
            return (bestActions, bestGameState);
        }

        private Tuple<List<string>, GameState> SimulateState(GameState initialGameState, ActionsProvider actionsProvider, ActionsHandler actionsExecutor, GameStatesEvaluator gameStatesEvaluator, IGameStateKey gameStateKey, Stopwatch stopwatch)
        {
            var gameStates = new Stack<Tuple<GameState, List<string>>>();
            var keys = new HashSet<string>();
            gameStates.Push(Tuple.Create(new GameState(initialGameState), new List<string>()));
            gameStatesEvaluator.Reset();
            while (gameStates.Count > 0)
            {
                Iterations++;

                var item = gameStates.Pop();
                var gameState = item.Item1;
                var moves = item.Item2;

                var key = gameStateKey.GetKey(gameState);
                if (!keys.Contains(key))
                {
                    keys.Add(key);
                    gameStatesEvaluator.AddGameState(gameState, moves);

                    if (stopwatch?.ElapsedMilliseconds > TimeLimit)
                    {
                        DebugMessage("EARLY BREAK");
                        break;
                    }

                    var actions = actionsProvider.AvailableActions(gameState);
                    foreach (var action in actions)
                    {
                        var newGameState = new GameState(gameState);
                        actionsExecutor.ExecuteAction(newGameState, action);
                        gameStates.Push(Tuple.Create(newGameState, new List<string>(moves) { action }));
                    }
                }
            }
            var bestActions = gameStatesEvaluator.GetBestActions();
            var bestGameState = gameStatesEvaluator.GetBestGameState();
            return Tuple.Create(bestActions, bestGameState);
        }
    }
}
namespace LOCM
{
    public enum Ability
    {
        Charge,
        Drain,
        Breakthrough,
        Ward,
        Guard,
        Lethal
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;

    public class Card
    {
        private static readonly IReadOnlyDictionary<char, Ability> AbilityMapping = new Dictionary<char, Ability>
        {
            ['C'] = Ability.Charge,
            ['B'] = Ability.Breakthrough,
            ['D'] = Ability.Drain,
            ['L'] = Ability.Lethal,
            ['W'] = Ability.Ward,
            ['G'] = Ability.Guard,
        };

        public int CardNumber { get; private set; }
        public int InstanceId { get; private set; }
        public CardType CardType { get; private set; }
        public int Attack { get; private set; }
        public int Defense { get; private set; }
        public int Cost { get; private set; }
        public int HealthChange { get; private set; }
        public int OpponentHealthChange { get; private set; }
        public int CardDraw { get; private set; }
        public HashSet<Ability> Abilities { get; private set; } = new HashSet<Ability>();
        public bool Charge => Abilities.Contains(Ability.Charge);
        public bool Lethal => Abilities.Contains(Ability.Lethal);
        public bool Breakthrough => Abilities.Contains(Ability.Breakthrough);
        public bool Guard => Abilities.Contains(Ability.Guard);
        public bool Ward => Abilities.Contains(Ability.Ward);
        public bool Drain => Abilities.Contains(Ability.Drain);

        public Card(CardType cardType, int cost, int attack, int defense, string abilities, int cardDraw, int healthChange, int opponentHealthChange, int instanceId, int cardNumber)
        {
            CardType = cardType;
            Attack = attack;
            Defense = defense;
            InstanceId = instanceId;
            HealthChange = healthChange;
            OpponentHealthChange = opponentHealthChange;
            CardDraw = cardDraw;
            Cost = cost;
            CardNumber = cardNumber;
            foreach (var ability in abilities)
            {
                Abilities.Add(AbilityMapping[ability]);
            }
        }

        public Card(Card card)
        {
            CardType = card.CardType;
            Attack = card.Attack;
            Defense = card.Defense;
            InstanceId = card.InstanceId;
            HealthChange = card.HealthChange;
            OpponentHealthChange = card.OpponentHealthChange;
            CardDraw = card.CardDraw;
            Cost = card.Cost;
            CardNumber = card.CardNumber;
            foreach (var ability in card.Abilities)
            {
                Abilities.Add(ability);
            }
        }

        public void UseGreen(Creature creature)
        {
            creature.Defense += Defense;
            creature.Attack += Attack;
            foreach (var ability in Abilities)
            {
                creature.Abilities.Add(ability);
            }
        }

        public void UseRed(Creature creature)
        {
            foreach (var ability in Abilities)
            {
                creature.Abilities.Remove(ability);
            }
            if (Defense != 0 && creature.Ward)
            {
                creature.Abilities.Remove(Ability.Ward);
            }
            else
            {
                creature.Defense += Defense;
            }
            creature.Attack = Math.Max(0, creature.Attack + Attack);
        }

        public void UseBlue(Creature creature)
        {
            if (Defense != 0 && creature.Ward)
            {
                creature.Abilities.Remove(Ability.Ward);
            }
            else
            {
                creature.Defense += Defense;
            }
        }
    }
}
namespace LOCM
{
    public enum CardType
    {
        Green,
        Red,
        Creature,
        Blue
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class Creature
    {
        private static readonly IReadOnlyDictionary<char, Ability> AbilityMapping = new Dictionary<char, Ability>
        {
            ['C'] = Ability.Charge,
            ['B'] = Ability.Breakthrough,
            ['D'] = Ability.Drain,
            ['L'] = Ability.Lethal,
            ['W'] = Ability.Ward,
            ['G'] = Ability.Guard,
        };

        private static readonly IReadOnlyDictionary<Ability, string> AbilityStringMapping = new Dictionary<Ability, string>
        {
            [Ability.Charge] = "C",
            [Ability.Breakthrough] = "B",
            [Ability.Drain] = "D",
            [Ability.Lethal] = "L",
            [Ability.Ward] = "W",
            [Ability.Guard] = "G",
        };

        public int Attack { get; set; }
        public int Defense { get; set; }
        public int InstanceId { get; set; }
        public int Lane { get; set; } = -1;
        public HashSet<Ability> Abilities { get; set; } = new HashSet<Ability>();
        public bool Attacked { get; set; } = false;
        public bool Charge => Abilities.Contains(Ability.Charge);
        public bool Lethal => Abilities.Contains(Ability.Lethal);
        public bool Breakthrough => Abilities.Contains(Ability.Breakthrough);
        public bool Guard => Abilities.Contains(Ability.Guard);
        public bool Ward => Abilities.Contains(Ability.Ward);
        public bool Drain => Abilities.Contains(Ability.Drain);
        public bool IsAlive => Defense > 0;

        public Creature(int attack, int defense, string abilities, int instanceId, int lane)
        {
            Attack = attack;
            Defense = defense;
            InstanceId = instanceId;
            Lane = lane;
            foreach (var ability in abilities)
            {
                Abilities.Add(AbilityMapping[ability]);
            }
            //Attacked = !Abilities.Contains(Ability.Charge); // TODO: check correction
        }

        public Creature(Creature creature)
        {
            Attack = creature.Attack;
            Defense = creature.Defense;
            InstanceId = creature.InstanceId;
            foreach (var ability in creature.Abilities)
            {
                Abilities.Add(ability);
            }
            Attacked = creature.Attacked;
            Lane = creature.Lane;
        }

        public Creature(Card card, bool attacked, int lane)
        {
            Attack = card.Attack;
            Defense = card.Defense;
            InstanceId = card.InstanceId;
            foreach (var ability in card.Abilities)
            {
                Abilities.Add(ability);
            }
            Attacked = attacked;
            Lane = lane;
        }

        public static void CreatureAttack(Creature attacker, Creature defender)
        {
            if (attacker.Lane != defender.Lane)
            {
                throw new ArgumentException($"{attacker.InstanceId} -> {defender.InstanceId} invalid lane target");
            }

            var attackerDefense = attacker.Ward ? attacker.Defense : defender.Lethal && defender.Attack > 0 ? 0 : attacker.Defense - defender.Attack;
            var attackerWard = attacker.Ward && defender.Attack <= 0;
            attacker.Defense = attackerDefense;
            attacker.Attacked = true;
            if (!attackerWard)
            {
                attacker.Abilities.Remove(Ability.Ward);
            }

            var defenderDefense = defender.Ward ? defender.Defense : attacker.Lethal && attacker.Attack > 0 ? 0 : defender.Defense - attacker.Attack;
            var defenderWard = defender.Ward && attacker.Attack <= 0;
            defender.Defense = defenderDefense;
            if (!defenderWard)
            {
                defender.Abilities.Remove(Ability.Ward);
            }
        }

        public void CreatureAttack(Creature creature)
        {
            CreatureAttack(this, creature);
        }

        public string GetAbilitiesString()
        {
            var abilities = string.Join("", Abilities.Select(ability => AbilityStringMapping[ability]).OrderBy(x => x));
            return abilities;
        }

        public string CreatureKey()
        {
            var abilities = string.Join("", Abilities.Select(ability => AbilityStringMapping[ability]));
            return $"{InstanceId} {Attack} {Defense} {abilities} {Attacked} {Lane}";
        }

        public override string ToString()
        {
            return $"({Attack}|{Defense}|{Lane}|{GetAbilitiesString()})";
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Linq;

    public class DeckDraft
    {
        private static readonly List<int> CardOrdering = @"116 68 151 51 65 80 7 53 29 37 67 32 139 69 49 33 66 147 18 152 28 48 82 88 23 84 52 44 87 148 99 121 64 85 103 141 158 50 95 115 133 19 109 54 157 81 150 21 34 36 135 134 70 3 61 111 75 17 144 129 145 106 9 105 15 114 128 155 96 11 8 86 104 97 41 12 26 149 90 6 13 126 93 98 83 71 79 72 73 77 59 100 137 5 89 142 112 25 62 125 122 74 120 159 22 91 39 94 127 30 16 146 1 45 38 56 47 4 58 118 119 40 27 35 101 123 132 2 136 131 20 76 14 43 102 108 46 60 130 117 140 42 124 24 63 10 154 78 31 57 138 107 113 55 143 92 156 110 160 153".Split(" ").Select(x => int.Parse(x)).ToList();

        public static Card PickCard(List<Card> cards)
        {
            var indexedCards = cards.Select((card, idx) => new { idx, card }).OrderBy(card => CardOrdering.IndexOf(card.card.CardNumber)).ToList();
            var bestCard = indexedCards.First().card;
            return bestCard;
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class DeckTracker : IDebug
    {
        private readonly DeckDraft DeckDraft;
        private readonly List<List<Card>> CardDrafts = new List<List<Card>>();
        private readonly Dictionary<int, int> CardDraftsCount = new Dictionary<int, int>();
        private readonly HashSet<int> AvailableDraftIndices = new HashSet<int>();
        private readonly Dictionary<int, int> PickedCards = new Dictionary<int, int>();
        private Dictionary<int, int> RemainingCards = new Dictionary<int, int>();
        private readonly Dictionary<int, Card> CardMapping = new Dictionary<int, Card>();
        private readonly List<int> UsedCards = new List<int>();
        private int DraftIndex = 0;
        private int WrongGuesses = 0;

        public bool Debug { get; set; } = true;

        public void DebugMessage(string message)
        {
            if (Debug) Console.Error.WriteLine(message);
        }

        public DeckTracker(DeckDraft deckDraft)
        {
            DeckDraft = deckDraft;
        }

        public void PickCard(List<Card> cards)
        {
            CardDrafts.Add(cards);
            foreach (var draftCard in cards)
            {
                var draftKey = draftCard.CardNumber;
                if (!CardDraftsCount.ContainsKey(draftKey))
                {
                    CardDraftsCount[draftKey] = 0;
                }
                CardDraftsCount[draftKey] += 1;
                AvailableDraftIndices.Add(DraftIndex++);
            }
            var card = DeckDraft.PickCard(cards);
            var key = card.CardNumber;
            Console.Error.WriteLine($"opponent card picked: {key}");
            if (!PickedCards.ContainsKey(key))
            {
                PickedCards[key] = 0;
                CardMapping[key] = card;
            }
            PickedCards[key] += 1;
        }

        public void AssignRemainingCardsFromPickedCards()
        {
            RemainingCards = new Dictionary<int, int>();
            foreach (var item in PickedCards)
            {
                RemainingCards[item.Key] = item.Value;
            }
        }

        public void UseCard(int cardNumber)
        {
            UsedCards.Add(cardNumber);
            var key = cardNumber;
            if (CardDraftsCount.ContainsKey(key) && CardDraftsCount[key] == 1)
            {
                CardDraftsCount[key] -= 1;
                var availableDrafts = CardDrafts
                    .Select((cards, index) => new { cards, index })
                    .Where(item => AvailableDraftIndices.Contains(item.index))
                    .ToList();
                var targetDraft = availableDrafts.First(item => item.cards.Select(card => card.CardNumber).Contains(key));
                AvailableDraftIndices.Remove(targetDraft.index);
            }
            if (!PickedCards.ContainsKey(key))
            {
                WrongGuesses++;
                // possible drafts
            }
            else if (RemainingCards.ContainsKey(key) && RemainingCards[key] > 0)
            {
                RemainingCards[key] -= 1;
            }
        }

        public List<Card> GetRemainingCards()
        {
            var result = new List<Card>();
            foreach (var item in RemainingCards)
            {
                for (int i = 0; i < item.Value; i++)
                {
                    result.Add(CardMapping[item.Key]);
                }
            }
            return result;
        }

        public void DebugInfo()
        {
            Console.Error.WriteLine($"Wrong guesses: {WrongGuesses}");
            Console.Error.WriteLine(string.Join(" ", RemainingCards.OrderBy(item => item.Key).Select(item => $"{item.Key}: {item.Value}")));
        }
    }
}
namespace LOCM
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class GameStatesEvaluator : IDebug
    {
        private readonly SelectiveActionsProvider _actionsProvider;
        private readonly ActionsHandler _actionsExecutor;
        private readonly IGameStateScorer _playerGameStateScorer;
        private readonly IGameStateScorer _opponentGameStateScorer;
        private readonly IGameStateKey _gameStateKey;
        private readonly OpponentLethalModule _opponentLethalModule;
        private readonly bool _enablePlayerLethalDetection;
        private Tuple<double, double> _bestScore = null;
        private GameState _bestGameState;
        private List<string> _bestActions;
        public bool Debug { get; set; } = false;
        public bool CalculateOpponentScore { get; set; } = true;

        public void DebugMessage(string message)
        {
            if (Debug) Console.Error.WriteLine(message);
        }

        public GameStatesEvaluator(SelectiveActionsProvider actionsProvider, ActionsHandler actionsExecutor, IGameStateScorer playerGameStateScorer, IGameStateScorer opponentGameStateScorer, IGameStateKey gameStateKey, bool enablePlayerLethalDetection = false, int lethalAdditionalDamage = 0)
        {
            _actionsProvider = actionsProvider;
            _actionsExecutor = actionsExecutor;
            _playerGameStateScorer = playerGameStateScorer;
            _opponentGameStateScorer = opponentGameStateScorer;
            _gameStateKey = gameStateKey;
            _enablePlayerLethalDetection = enablePlayerLethalDetection;
            _opponentLethalModule = new OpponentLethalModule(actionsProvider, actionsExecutor, gameStateKey)
            {
                LethalAdditionalDamage = lethalAdditionalDamage
            };
        }

        public void AddGameState(GameState gameState, List<string> moves)
        {
            var opponentScore = 0.0;
            if (CalculateOpponentScore) opponentScore = SimulateEnemy(gameState, _opponentGameStateScorer, _gameStateKey);
            var playerScore = _playerGameStateScorer.GameStateScore(gameState) + gameState.AdditionalScore;
            var playerBonus = 0;

            if (_enablePlayerLethalDetection)
            {
                var opponentGameState = gameState.SwitchSideNoCards();
                var actions = _opponentLethalModule.Execute(opponentGameState);
                if (actions.Any())
                {
                    playerBonus = -10000 * _opponentLethalModule.LethalDamage;
                }
                for (var i = 0; i < GameState.LaneCount; i++)
                {
                    var laneAttackers = gameState.Attackers.Where(attacker => attacker.Lane == i).ToList();
                    if (laneAttackers.Count == 3 && laneAttackers.Sum(attacker => attacker.Attack) <= 5)
                    {
                        playerBonus -= 1000;
                    }
                }
            }

            var score = Tuple.Create(-opponentScore + playerScore * 0.25 + playerBonus, playerScore);

            DebugMessage($"{gameState} scores: {score} {opponentScore} {playerScore} {string.Join(" ", moves)}");
            if (_bestScore == null || score.Item1 > _bestScore.Item1
                || (score.Item1 == _bestScore.Item2 && score.Item2 < _bestScore.Item2))
            {
                _bestScore = score;
                _bestGameState = gameState;
                _bestActions = moves;
            }
        }

        public void Reset()
        {
            _bestScore = null;
        }

        public List<string> GetBestActions()
        {
            return _bestActions;
        }

        public GameState GetBestGameState()
        {
            return _bestGameState;
        }

        public double SimulateEnemy(GameState playerFinalState, IGameStateScorer opponentGameStateScorer, IGameStateKey gameStateKey)
        {
            Stack<Tuple<GameState, List<string>>> gameStates = new Stack<Tuple<GameState, List<string>>>();
            gameStates.Push(Tuple.Create(new GameState(playerFinalState.SwitchSide()), new List<string>()));
            HashSet<string> keys = new HashSet<string>();
            double? bestScore = null;
            while (gameStates.Count > 0)
            {
                var item = gameStates.Pop();
                var gameState = item.Item1;
                var moves = item.Item2;

                var key = gameStateKey.GetKey(gameState);

                if (!keys.Contains(key))
                {
                    keys.Add(key);
                    var score = opponentGameStateScorer.GameStateScore(gameState);
                    if (!bestScore.HasValue || score > bestScore.Value)
                    {
                        bestScore = score;
                    }

                    var actions = _actionsProvider.AvailableAttackActions(gameState);
                    foreach (var action in actions)
                    {
                        var newGameState = new GameState(gameState);
                        _actionsExecutor.ExecuteAction(newGameState, action);
                        gameStates.Push(Tuple.Create(newGameState, new List<string>(moves) { action }));
                    }
                }
            }
            return bestScore.Value;
        }
    }
}
namespace LOCM
{
    using System;

    public class Player
    {
        public int Health { get; set; }
        public int Mana { get; set; }
        public int RemainingCards { get; set; }
        public int Rune { get; set; }
        public int CardsDraw { get; set; }
        public int HandCardsCount { get; set; }
        public bool IsSecond { get; set; }

        public Player()
        {
        }

        public Player(Player player)
        {
            Health = player.Health;
            Mana = player.Mana;
            RemainingCards = player.RemainingCards;
            Rune = player.Rune;
            CardsDraw = player.CardsDraw;
            IsSecond = player.IsSecond;
            HandCardsCount = player.HandCardsCount;
        }

        public bool IsDead(int damage)
        {
            var currentRune = Rune;
            var health = Health - damage;
            var draws = CardsDraw;
            while (health <= currentRune && currentRune > 0)
            {
                draws += 1;
                currentRune -= 5;
            }
            var remainingRunes = currentRune / 5;
            return health <= 0 || (draws > RemainingCards && draws - RemainingCards > remainingRunes);
        }

        public bool IsDead()
        {
            var remainingRunes = Rune / 5;
            return Health <= 0 || (CardsDraw > RemainingCards && CardsDraw - RemainingCards > remainingRunes);
        }

        public void DealDamageToPlayer(int damage)
        {
            var currentRune = Rune;
            var health = Health - damage;
            var draws = CardsDraw;
            while (health <= currentRune && currentRune > 0)
            {
                draws += 1;
                currentRune -= 5;
            }
            var remainingRunes = currentRune / 5;
            CardsDraw = draws;
            Health = health;
            Rune = remainingRunes * 5;
        }

        public void ModifyHealth(int healValue)
        {
            if (healValue == 0) return;

            if (healValue < 0)
            {
                DealDamageToPlayer(Math.Abs(healValue));
            }
            else
            {
                Health += healValue;
            }
        }
    }
}
namespace LOCM
{
    using System.Collections.Generic;
    using System.Linq;
  using System;

    public static class SummonCombinations
    {
        public static List<List<Card>> GetSummonCombinations(List<Card> cards, int maxMana)
        {
            var combinations = new List<List<Card>>();
            var summonCards = cards.Where(card => card.CardType == CardType.Creature).ToList();
            var stack = new Stack<Tuple<List<Card>, int, List<Card>>>();
            stack.Push(Tuple.Create(summonCards, maxMana, new List<Card>()));
            var seen = new HashSet<string>();
            while (stack.Count > 0)
            {
                var item = stack.Pop();
                var availableCards = item.Item1;
                var availableMana = item.Item2;
                var combination = item.Item3;

                if (combination.Any()) combinations.Add(combination);

                foreach (var card in availableCards.Where(card => card.Cost <= availableMana))
                {
                    var remainingCards = new List<Card>(availableCards);
                    remainingCards.Remove(card);
                    var newCombination = new List<Card>(combination) { card };
                    var key = string.Join(" ", newCombination.OrderBy(c => c.CardNumber).Select(c => c.CardNumber));
                    if (seen.Contains(key)) continue;
                    seen.Add(key);
                    stack.Push(Tuple.Create(remainingCards, availableMana - card.Cost, newCombination));
                }
            }
            return combinations
                .OrderByDescending(combination => combination.Sum(card => card.Cost))
                .ThenBy(combination => combination.Count)
                .ToList();
        }

        public static List<List<Card>> GetCardsCombinations(List<Card> cards, int maxMana)
        {
            var combinations = new List<List<Card>>();
            var summonCards = cards.ToList();
            var stack = new Stack<Tuple<List<Card>, int, List<Card>>>();
            stack.Push(Tuple.Create(summonCards, maxMana, new List<Card>()));
            var seen = new HashSet<string>();
            while (stack.Count > 0)
            {
                var item = stack.Pop();
                var availableCards = item.Item1;
                var availableMana = item.Item2;
                var combination = item.Item3;

                if (combination.Any()) combinations.Add(combination);

                foreach (var card in availableCards.Where(card => card.Cost <= availableMana))
                {
                    var remainingCards = new List<Card>(availableCards);
                    remainingCards.Remove(card);
                    var newCombination = new List<Card>(combination) { card };
                    var key = string.Join(" ", newCombination.OrderBy(c => c.CardNumber).Select(c => c.CardNumber));
                    if (seen.Contains(key)) continue;
                    seen.Add(key);
                    stack.Push(Tuple.Create(remainingCards, availableMana - card.Cost, newCombination));
                }
            }
            return combinations
                .OrderByDescending(combination => combination.Sum(card => card.Cost))
                .ThenBy(combination => combination.Count)
                .ToList();
        }

        public static List<List<Card>> GetDominatingCardsCombinations(List<Card> cards, int maxMana)
        {
            var combinations = GetCardsCombinations(cards, maxMana);
            var scoredCombinations = combinations
                .Select(combo => new { combo, score = combo.Sum(card => 1 << cards.IndexOf(card)) })
                .OrderByDescending(item => item.score);
            var validCombinations = new List<List<Card>>();
            var seen = new List<int>();
            foreach (var item in scoredCombinations)
            {
                var combination = item.combo;
                var value = item.score;
                if (seen.Any(seenValue => (value & seenValue) == value)) continue;
                seen.Add(value);
                validCombinations.Add(combination);
            }
            return validCombinations;
        }
    }
}
namespace LOCM
{
    public static class AggresiveScorersFactory
    {
        public static IGameStateScorer GetPlayerScorer()
        {
            var playerGameStateScorer = new OneLaneStrategy
            {
                AttackWeight = 13,
                DefenseWeight = 6,
                BreakthroughWeight = 1,
                DrainWeight = 5,
                GuardWeight = 12,
                LethalWeight = 25,
                WardWeight = 20,
                OpponentScoreMultiplier = 10,
                PlayerScoreMultiplier = 12,
                ClearLaneWeight = 10,
                DamageWeight = 25,
                UseCardWeight = 15
            };
            return playerGameStateScorer;
        }

        public static IGameStateScorer GetOpponentScorer()
        {
            var opponentGameStateScorer = new OneLaneStrategy
            {
                AttackWeight = 13,
                DefenseWeight = 6,
                BreakthroughWeight = 1,
                DrainWeight = 5,
                GuardWeight = 12,
                LethalWeight = 25,
                WardWeight = 20,
                OpponentScoreMultiplier = 10,
                PlayerScoreMultiplier = 10,
                ClearLaneWeight = 0,
                DamageWeight = 25,
                UseCardWeight = -15
            };
            return opponentGameStateScorer;
        }
    }
}
namespace LOCM
{
    public static class DefaultScorersFactory
    {
        public static IGameStateScorer GetPlayerScorer()
        {
            var playerGameStateScorer = new OneLaneStrategy
            {
                AttackWeight = 10,
                DefenseWeight = 6,
                BreakthroughWeight = 1,
                DrainWeight = 5,
                GuardWeight = 12,
                LethalWeight = 25,
                WardWeight = 20,
                OpponentScoreMultiplier = 10,
                PlayerScoreMultiplier = 11,
                ClearLaneWeight = 10,
                DamageWeight = 5,
                UseCardWeight = 15
            };
            return playerGameStateScorer;
        }

        public static IGameStateScorer GetOpponentScorer()
        {
            var opponentGameStateScorer = new OneLaneStrategy
            {
                AttackWeight = 10,
                DefenseWeight = 6,
                BreakthroughWeight = 1,
                DrainWeight = 5,
                GuardWeight = 12,
                LethalWeight = 25,
                WardWeight = 20,
                OpponentScoreMultiplier = 11,
                PlayerScoreMultiplier = 10,
                ClearLaneWeight = 0,
                DamageWeight = 5,
                UseCardWeight = -15
            };
            return opponentGameStateScorer;
        }
    }
}
namespace LOCM
{
    using System;

    public static class ScorersFactory
    {
        public enum ScorersStrategy
        {
            Default,
            Aggresive
        }

        public static (IGameStateScorer, IGameStateScorer) GetScorers(ScorersStrategy scorersStrategy)
        {
            switch (scorersStrategy)
            {
                case ScorersStrategy.Default:
                    return (DefaultScorersFactory.GetPlayerScorer(), DefaultScorersFactory.GetOpponentScorer());

                case ScorersStrategy.Aggresive:
                    return (AggresiveScorersFactory.GetPlayerScorer(), AggresiveScorersFactory.GetOpponentScorer());

                default:
                    throw new ArgumentException($"invalid scorersStrategy: {scorersStrategy}");
            }
        }
    }
}
namespace LOCM
{
    public interface IDebug
    {
        bool Debug { get; set; }

        void DebugMessage(string message);
    }
}
namespace LOCM
{
    public interface IGameActionScorer
    {
        int GameActionScore(GameState gameState, string gameAction);
    }
}
namespace LOCM
{
    public interface IGameStateKey
    {
        string GetKey(GameState gameState);
    }
}
namespace LOCM
{
    public interface IGameStateScorer
    {
        double GameStateScore(GameState gameState);
    }
}
