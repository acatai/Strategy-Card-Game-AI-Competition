
# Algorytm



## Pseudokod

Parametry globalne:
- `P` - wielkość populacji
- `G` - liczba generacji

```
InitPopulation()
for i=1..G:
  PrepareDraft()
  parallel_for 1..P:
    SelectParents()
    CrossoverChildren()
    MutateChildren()
  ScoreChildrenPopulation()
  PopulationSelectMerge()
```


## Podprocedury


### InitPopulation()

Inicjalizujemy wszystkich osobników w populacji, zależy od reprezentacji.

Po tym, nalezy obliczyć ich fitness. Można to robić na wiele sposobów, np:
1. dać wszystkim po 0
1. robić mecze między losowymi parami na losowych draftach
1. grać przeciwko ustalonemu osobnikowi (np. ClosetAI) na losowych draftach

Na razie proponuję 1 - bo parę pierwszych populacji powinno sprawę _jakoś_ rozwiązać, a szkoda nam na razie czasu na bardziej wysublimowane algorytmy.


### PrepareDraft()

Zwraca info o drafcie który testujemy w tej generacji, w szczególności karty które są w nim użyte. Karty te będziemy określać jako _geny aktywne_.



### SelectParents()
Parametry:
- `ts` - tournament size
- `tg` - liczba gier między jedną parą

Żeby wybrać jednego rodzica, losujemy z populacji `ts` osobników (z uniform probability może na razie) i obliczamy jak dobrze grają na aktualnym drafcie.

Opcje są dwie. Mniej zasobożerna jest taka, że `ts` jest potęgą dwójki i przeprowadzamy prawdziwy turniej, tzn. ustalamy pary i między każdą rozgrywamy `tg` potyczek, a zwycięzcy przechodzą dalej aż mamy tylko jednego osobnika.

Bardziej zasobożerna, że każdy gra z każdym i wybieramy tego z największą liczbą punktów.

Drugiego rodzica wybieramy tak samo.

Tak naprawdę nie potrzebujemy calego genomu rodziców tylko geny aktywne, i tylko je można przekazywać w kolejnych krokach. Tzn. jeśli to będzie prostsze/szybsze to osobnicy w populacji dzieci mogą zawierać wyłącznie geny aktywne.




### CrossoverChildren() i MutateChildren()

Parametry:
- `pm` - do sterowania prawdopodobieństwem mutacji

Dla zadanej pary rodziców robimy crossover produkując parę dzieci, a następnie na każdym z tych dzieci odpalamy podprocedurę do mutacji (patrz reprezentacje).


### ScoreChildrenPopulation()

Parametry:
- `sr` - liczba rund
- `sg` - liczba gier między jedną parą

OK, mamy tę populację dzieci i trzeba im nadać jakieś fitness.

Opcja 1. Robimy `sr` rund, a w każdej sortujemy populację po aktualnym fitness (początkowo 0), po czym dobieramy w pary (1 z ostatnim, drugi z przedostatnim itd - albo - 1 z drugim, trzeci z czwartym itd) i pomiędzy każdą parą wykonujemy `sg` gier.

_(Tutaj rozgrywki między niezależnymi parami można parallelizować.)_

Opcja 2. Jakoś turniejowo, ale wtedy nie dostajemy fitness tylko pozycję, więc na razie bym się w to nie bawił, bo będzie ciężej w pozostałych krokach algorytmu.


### PopulationSelectMerge()

OK, mamy dane populacje rodziców i populacje dzieci, obie mają przypisany fitness. Trzeba to jakoś zmergować i to może być czołowy operator w naszym procesie.

Propozycja jest taka żeby robić roulette wheel selection (czyli losować proporcjonalnie do wartości fitness). Tzn. `P` razy losujemy tak rodzica i losujemy dziecko, a następnie mergujemy oba genomy. Propozycje mergów zależą od reprezentacji.


## Wyniki

To co nas interesuje to, po zrobieniu `G` generacji, sprawdzenie jak dybry jest nasz zwycięzca na wszystkich testach (draftach) od początku ewolucji (nazwijmy go `W`). Czyli chcemy obliczyć jego score dla każdego z tych dratów i zrobić ładny wykresik.

Tutaj dotykamy standardowego problemu czyli jak mu kurde obliczyć score? 

Propozycja na szybko jest taka żeby pamiętać część (wszystkich?) odobników w każdej generacji, i obliczając score w `i`-tej generacji grać tym naszym `W` przeciw każdemu osobnikowi z tej generacji korzystając z `i`-tego draftu. Dobrze by mieć trzy punkty, score vs najlepszy w tej generacji, score vs najgorszy i średnia ze score przeciw wszystkim.





## Reprezentacje


### Priorytetowa-liczbowa

Genotyp jest tablicą id->priority, tzn. dla każdego id karty mamy potany priorytet (float 0-1) z jakim chcemy ją wziąć. Gdy dostajemy 3 karty do wyboru bierzemy tę z najwyższym priorytetem.

#### Initialization

Tablica losowych liczb z przedziału 0-1.

#### Crossover

Uniform crossover.

#### Mutacja

Dla każdego genu, z prawdopodobieństwem `pm` wylosuj mu nową wartość (liczba [0-1]).

#### Merge

Robimy zwykłe kopiowanie aktywnych genów z dziecka do rodzica - a nuż zadziała ^^'.

```
[0.1, 0.5, 1.0, 0.3, 0.3] + [-, 0.2, 0.3, _, 0.7] -> [0.1, 0.2, 0.3, 0.3, 0.7]
```


### Priorytetowo-liczbowa wariant 2

#### Initialization i Crossover

Jak dla wariantu podstawowego

#### Mutacja

Gaussowska - czyli dodajemy coś wylosowane z rozkładem normalnym: μ=0, σ² nie wiem, może po prostu gdzieś w okolicach 1?

#### Merge

Dla aktywnych genów średnia ważona między ich wartością u dziecka (waga _wc_) i  u rodzica (1-_wc_). Może na początek zobaczyc _wc_=0.1.





### Priorytetowa-sekwencyjna

#### Initialization

Losowa permutacja identyfikatorów.

Genotyp jest tablicą zawierającą id kart. Gdy dostajemy 3 karty do wyboru bierzemy tę która znajduje się najbliżej początku tablicy (ma najniższy indeks).

([o operatorach](https://www.researchgate.net/publication/226665831_Genetic_Algorithms_for_the_Travelling_Salesman_Problem_A_Review_of_Representations_and_Operators))

#### Crossover

Nie wiem, może order crossover operator (OX1) się nadaje...

#### Mutacja

Z prawdopodobieństwem `pm` wylosuj dwa indeksy i zamień ze sobą miejscami.

#### Merge

Zaznaczmy w genomie rodzice te geny które są aktywne i nadpisujemy ich zawartość zgodnie z kolejnością genów aktywnych w dziecku.

```
[23, 12, 4, 5, 78, 3, 125] + [78, 4, 12] -> [23, 78, 4, 5, 12, 3, 125]
```


### Pozostałe 

- cośtam, cośtam ;-)

