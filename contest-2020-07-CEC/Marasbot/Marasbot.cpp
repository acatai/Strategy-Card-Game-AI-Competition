#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
static unsigned long rand_x=123456789, rand_y=362436069, rand_z=521288629;

unsigned long generate_random() 
{          
unsigned long rand_t;
    rand_x ^= rand_x << 16;
    rand_x ^= rand_x >> 5;
    rand_x ^= rand_x << 1;

   rand_t = rand_x;
   rand_x = rand_y;
   rand_y = rand_z;
   rand_z = rand_t ^ rand_x ^ rand_y;

   return rand_z;
}

int ability_to_int(char ability) 
{
    if(ability=='L') return 100000;
    if(ability=='G') return 10000;
    if(ability=='C') return 1000;
    if(ability=='W') return 100;
    if(ability=='D') return 10;
    if(ability=='B') return 1;
}
 
bool have_ability(int creature_abilities, char ability)
{
    int ability_number=ability_to_int(ability);
    if(((creature_abilities%(ability_number*10))/ability_number)==1) return true;
    return false;
}
 
int get_ability(string abilities)
{
    int result=0;
    if(abilities.find('L') < 100) result+=100000;
    if(abilities.find('G') < 100) result+=10000;
    if(abilities.find('C') < 100) result+=1000;
    if(abilities.find('W') < 100) result+=100;
    if(abilities.find('D') < 100) result+=10;
    if(abilities.find('B') < 100) result+=1;
    return result;
}

int place_in_board(int my_board[3][5])
{
    for(int i=0; i<6; i++)
    {
        if(my_board[i][0]==0) return i;
    }
    
    return 7;
}

int hand_size(int hand[8][6])
{
    for(int i=0; i<8; i++)
    {
        if(hand[i][0]==0) return i;
    }
    return 8;
}

int to_one(int number)
{
    string text = to_string(number);

    for(int i=0; i<text.length(); i++)
    {
        if(text[i]!='0') text[i]='1';
    }
    
    
    int result = atoi(text.c_str());
    return result;
}

int is_guarded(int enemy_board[3][5], int end)
{
    for(int i=0; i<end; i++)
    {
        if(have_ability(enemy_board[i][3], 'G')) return i;
    }
    return -2;
}



int heuristic_value(int hand [8][6], int my_board[3][5], int enemy_board[3][5], int my_board_two[3][5], int enemy_board_two[3][5], int mana, int enemy_hp)
{
    int final_points=0;
    
    final_points-=enemy_hp*35;
    if(enemy_hp<=0) return 1000000;
    
    for(int i=0; i<8; i++)
    {
        if(hand[i][0]==0) break;
        if(have_ability(hand[i][5], 'L') & have_ability(hand[i][5], 'C')) final_points+=300;
        if(hand[i][5]==42) final_points+=400;
        if(hand[i][4]!=0) final_points+=200;
    }    
    
    for(int i=0; i<3; i++)
    {  
        if(my_board[i][0]!=0)
        {
            final_points+=5000;
            final_points+=my_board[i][1]*2;
            final_points+=my_board[i][2]*3;
            
            if(have_ability(my_board[i][3], 'L')) final_points+=250;
            
            if(have_ability(my_board[i][3], 'G')) final_points+=350*my_board[i][2];
            if(have_ability(my_board[i][3], 'W')) final_points+=250;
            /*
            if(have_ability(my_board[i][3], 'D')) final_points+=20*my_board[i][1];
            /*
            if(have_ability(my_board[i][3], 'B')) final_points+=1;
            */
        }
        if(enemy_board[i][0]!=0)
        {
            
            final_points-=17000;
            final_points-=enemy_board[i][1]*3;
            final_points-=enemy_board[i][2]*2;
            
            if(enemy_board[i][2]<=2) final_points-=1400;
            
            if(have_ability(enemy_board[i][3], 'L')) final_points-=150;
            if(have_ability(enemy_board[i][3], 'G')) final_points-=120*enemy_board[i][2];
        
            /*
            if(have_ability(enemy_board[i][3], 'W')) final_points-=250;
            
            /*
            if(have_ability(enemy_board[i][3], 'D')) final_points-=200;
            /*
            if(have_ability(enemy_board[i][3], 'B')) final_points-=1;
            */
        }
        if(my_board_two[i][0]!=0)
        {
            final_points+=5000;
            final_points+=my_board_two[i][1]*2;
            final_points+=my_board_two[i][2]*3;
            
            if(have_ability(my_board_two[i][3], 'L')) final_points+=250;
            
            if(have_ability(my_board_two[i][3], 'G')) final_points+=350*my_board_two[i][2];
            if(have_ability(my_board_two[i][3], 'W')) final_points+=250;
            /*
            if(have_ability(my_board[i][3], 'D')) final_points+=20*my_board[i][1];
            /*
            if(have_ability(my_board[i][3], 'B')) final_points+=1;
            */
        }
        if(enemy_board_two[i][0]!=0)
        {
            
            final_points-=17000;
            final_points-=enemy_board_two[i][1]*3;
            final_points-=enemy_board_two[i][2]*2;
            
            if(enemy_board_two[i][2]<=2) final_points-=1400;
            
            if(have_ability(enemy_board_two[i][3], 'L')) final_points-=150;
            if(have_ability(enemy_board_two[i][3], 'G')) final_points-=120*enemy_board_two[i][2];
        
            /*
            if(have_ability(enemy_board[i][3], 'W')) final_points-=250;
            
            /*
            if(have_ability(enemy_board[i][3], 'D')) final_points-=200;
            /*
            if(have_ability(enemy_board[i][3], 'B')) final_points-=1;
            */
        }
    }
    
    return final_points;
    
    
}

string final_play[2];

string* my_play(int my_hand [8][6], int my_board[3][5], int enemy_board[3][5], int my_board_two[3][5], int enemy_board_two[3][5], int mana, int enemy_hp)
{

    int random;
    
    int summoning_phase=7;
    int attacking_phase=5;
    int place;
    int enemy_place;
    int hand_sizer=hand_size(my_hand);
    int random_enemy;

    string plays_array [14];
    int plays_counter=0;
    
    final_play[0]="";
    final_play[1]="";
    
    
    random=generate_random();
    random=abs(random);
    
    for(int i=0; i<hand_sizer; i++)
    {
        random++;
        random%=hand_sizer;
        
        if(mana >= my_hand[random][1])
        {
            if(my_hand[random][4]==0)
                {
                place=place_in_board(my_board);
                
                if(place<3)
                {
                    mana-=my_hand[random][1];
                    my_board[place][0]=my_hand[random][0];
                    my_board[place][1]=my_hand[random][2];
                    my_board[place][2]=my_hand[random][3];
                    my_board[place][3]=my_hand[random][5];
                    if(have_ability(my_hand[random][5], 'C')) my_board[place][4]=1;
                    else my_board[place][4]=0;
                    plays_array[plays_counter]=(";SUMMON " + to_string(my_hand[random][0]) + " " + to_string(0));
                    plays_counter++;
                }
                else
                {
                    place=place_in_board(my_board_two);
                
                if(place<3)
                {
                    mana-=my_hand[random][1];
                    my_board_two[place][0]=my_hand[random][0];
                    my_board_two[place][1]=my_hand[random][2];
                    my_board_two[place][2]=my_hand[random][3];
                    my_board_two[place][3]=my_hand[random][5];
                    if(have_ability(my_hand[random][5], 'C')) my_board_two[place][4]=1;
                    else my_board_two[place][4]=0;
                    plays_array[plays_counter]=(";SUMMON " + to_string(my_hand[random][0]) + " " + to_string(1));
                    plays_counter++;
                }
                }
            }
            
            if(my_hand[random][4]==1) //green
            {
                if(mana >= my_hand[random][1])
                {
                    place=place_in_board(my_board);
                    
                    if(place > 0)
                    {
                        mana-=my_hand[random][1];
                        random_enemy=generate_random();
                        random_enemy=abs(random_enemy);
                        random_enemy%= place;
                        my_board[random_enemy][1]+=my_hand[random][2];
                        my_board[random_enemy][2]+=my_hand[random][3];
                        my_board[random_enemy][3]+=my_hand[random][5];
                        my_board[random_enemy][3]=to_one(my_board[random_enemy][3]);
                        plays_array[plays_counter]=(";USE " + to_string(my_hand[random][0]) + " " + to_string(my_board[random_enemy][0]));
                        plays_counter++;
                    }
                    else
                    {
                        place=place_in_board(my_board_two);
                    
                    if(place > 0)
                    {
                        mana-=my_hand[random][1];
                        random_enemy=generate_random();
                        random_enemy=abs(random_enemy);
                        random_enemy%= place;
                        my_board_two[random_enemy][1]+=my_hand[random][2];
                        my_board_two[random_enemy][2]+=my_hand[random][3];
                        my_board_two[random_enemy][3]+=my_hand[random][5];
                        my_board_two[random_enemy][3]=to_one(my_board_two[random_enemy][3]);
                        plays_array[plays_counter]=(";USE " + to_string(my_hand[random][0]) + " " + to_string(my_board_two[random_enemy][0]));
                        plays_counter++;
                    }
                    }
                }
            }
            
            if(my_hand[random][4]==2) //red
            {
                if(mana >= my_hand[random][1])
                {
                    place=place_in_board(enemy_board);
                    
                    if(place > 0)
                    {
                        mana-=my_hand[random][1];
                        random_enemy=generate_random();
                        random_enemy=abs(random_enemy);
                        random_enemy%= place;
                        enemy_board[random_enemy][1]+=my_hand[random][2];
                        //enemy_board[random_enemy][2]+=my_hand[random][3];
                        plays_array[plays_counter]=(";USE " + to_string(my_hand[random][0]) + " " + to_string(enemy_board[random_enemy][0]));
                        plays_counter++;
                        enemy_board[random_enemy][3]+=my_hand[random][5];
                        enemy_board[random_enemy][3]=to_one(enemy_board[random_enemy][3]);
                        enemy_board[random_enemy][3]-=my_hand[random][5];

                        if(!(have_ability(enemy_board[random_enemy][3], 'W')))
                        {
                            enemy_board[random_enemy][2]+=my_hand[random][3];
                        }
                        else
                        {
                            enemy_board[random_enemy][2]-=get_ability("W");
                            continue;
                        }
                        
                        if(enemy_board[random_enemy][2]<=0)
                        {
                            enemy_board[random_enemy][0]=0;
                            for(int swaper=0; swaper<5; swaper++)
                            {
                                swap(enemy_board[random_enemy][swaper], enemy_board[place-1][swaper]);
                            }
                        }
                        
                    }
                    
                    else
                    
                    place=place_in_board(enemy_board_two);
                    
                    if(place > 0)
                    {
                        mana-=my_hand[random][1];
                        random_enemy=generate_random();
                        random_enemy=abs(random_enemy);
                        random_enemy%= place;
                        enemy_board_two[random_enemy][1]+=my_hand[random][2];
                        //enemy_board[random_enemy][2]+=my_hand[random][3];
                        plays_array[plays_counter]=(";USE " + to_string(my_hand[random][0]) + " " + to_string(enemy_board_two[random_enemy][0]));
                        plays_counter++;
                        enemy_board_two[random_enemy][3]+=my_hand[random][5];
                        enemy_board_two[random_enemy][3]=to_one(enemy_board_two[random_enemy][3]);
                        enemy_board_two[random_enemy][3]-=my_hand[random][5];

                        if(!(have_ability(enemy_board_two[random_enemy][3], 'W')))
                        {
                            enemy_board_two[random_enemy][2]+=my_hand[random][3];
                        }
                        else
                        {
                            enemy_board_two[random_enemy][2]-=get_ability("W");
                            continue;
                        }
                        
                        if(enemy_board_two[random_enemy][2]<=0)
                        {
                            enemy_board_two[random_enemy][0]=0;
                            for(int swaper=0; swaper<5; swaper++)
                            {
                                swap(enemy_board_two[random_enemy][swaper], enemy_board_two[place-1][swaper]);
                            }
                        }
                        
                    }
                }
            }
            /*
            if(my_hand[i][4]==3) //blue
            {
                if(mana >= my_hand[i][1])
                {
                    mana-=my_hand[i][1];
                    plays_array[plays_counter]=(";USE " + to_string(my_hand[i][0]) + " " + to_string(-1));
                    plays_counter++;
                }
            }
            */
            
        }
    }
    
    place=place_in_board(my_board);
    
    random=generate_random();
    random=abs(random);
    
    for(int i=0; i<place; i++)
    {
        
        random++;
        random%=place;
        
        enemy_place=place_in_board(enemy_board);
        
        if(i==place) break;
        if(my_board[random][4]==0 || my_board[random][1]==0)
        {
            continue;
        }
        
        random_enemy=is_guarded(enemy_board, enemy_place);
        
        
        
        
        if(random_enemy==-2)
        {
            /*
            if(have_ability(my_board[random][3], 'G'))
            {
                plays_array[plays_counter]=(";ATTACK " + to_string(my_board[random][0]) + " " + to_string(-1));
                plays_counter++;
                continue;
            }
            */
            random_enemy=generate_random();
            random_enemy=abs(random_enemy);
            random_enemy%= (enemy_place+1);
            random_enemy-=1;
        }
        
        if(random_enemy==-1)
        {
            enemy_hp-=my_board[random][1];
            plays_array[plays_counter]=(";ATTACK " + to_string(my_board[random][0]) + " " + to_string(-1));
            plays_counter++;
            continue;
        }
        
        plays_array[plays_counter]=(";ATTACK " + to_string(my_board[random][0]) + " " + to_string(enemy_board[random_enemy][0]));
        plays_counter++;
        
        if(!(have_ability(my_board[random][3], 'W')))
        {
            if(have_ability(enemy_board[random_enemy][3], 'L')) my_board[random][2]=0;
            if(have_ability(enemy_board[random_enemy][3], 'D')) enemy_hp+=enemy_board[random_enemy][1];
            
            my_board[random][2]-=enemy_board[random_enemy][1];
        }
        else    my_board[random][3]-=get_ability("W");
        
        if(!(have_ability(enemy_board[random_enemy][3], 'W')))
        {
            if(have_ability(my_board[random][3], 'L')) enemy_board[random_enemy][2]=0;
            if(have_ability(my_board[random][3], 'B')) enemy_hp-=(enemy_board[random_enemy][2]-my_board[random][1]-abs(enemy_board[random_enemy][2]-my_board[random][1]))/2;
            enemy_board[random_enemy][2]-=my_board[random][1];
        }
        else    enemy_board[random_enemy][3]-=get_ability("W");
        
        
        
        if(enemy_board[random_enemy][2]<=0)
        {
            enemy_board[random_enemy][0]=0;
            for(int swaper=0; swaper<5; swaper++)
            {
                swap(enemy_board[random_enemy][swaper], enemy_board[enemy_place-1][swaper]);
            }
        }
        
        if(my_board[random][2]<=0)
        {
            my_board[random][0]=0;
            my_board[random][4]=0;
            for(int swaper=0; swaper<5; swaper++)
            {
                swap(my_board[random][swaper], my_board[place-1][swaper]);
            }
        }
    }
        
        
    place=place_in_board(my_board_two);
    
    random=generate_random();
    random=abs(random);
    
    for(int i=0; i<place; i++)
    {
        
        random++;
        random%=place;
        
        enemy_place=place_in_board(enemy_board_two);
        
        if(i==place) break;
        if(my_board_two[random][4]==0 || my_board_two[random][1]==0)
        {
            continue;
        }
        
        random_enemy=is_guarded(enemy_board_two, enemy_place);
        
        
        
        
        if(random_enemy==-2)
        {
            /*
            if(have_ability(my_board[random][3], 'G'))
            {
                plays_array[plays_counter]=(";ATTACK " + to_string(my_board[random][0]) + " " + to_string(-1));
                plays_counter++;
                continue;
            }
            */
            random_enemy=generate_random();
            random_enemy=abs(random_enemy);
            random_enemy%= (enemy_place+1);
            random_enemy-=1;
        }
        
        if(random_enemy==-1)
        {
            enemy_hp-=my_board_two[random][1];
            plays_array[plays_counter]=(";ATTACK " + to_string(my_board_two[random][0]) + " " + to_string(-1));
            plays_counter++;
            continue;
        }
        
        plays_array[plays_counter]=(";ATTACK " + to_string(my_board_two[random][0]) + " " + to_string(enemy_board_two[random_enemy][0]));
        plays_counter++;
        
        if(!(have_ability(my_board_two[random][3], 'W')))
        {
            if(have_ability(enemy_board_two[random_enemy][3], 'L')) my_board_two[random][2]=0;
            if(have_ability(enemy_board_two[random_enemy][3], 'D')) enemy_hp+=enemy_board_two[random_enemy][1];
            
            my_board_two[random][2]-=enemy_board_two[random_enemy][1];
        }
        else    my_board_two[random][3]-=get_ability("W");
        
        if(!(have_ability(enemy_board_two[random_enemy][3], 'W')))
        {
            if(have_ability(my_board_two[random][3], 'L')) enemy_board_two[random_enemy][2]=0;
            if(have_ability(my_board_two[random][3], 'B')) enemy_hp-=(enemy_board_two[random_enemy][2]-my_board_two[random][1]-abs(enemy_board_two[random_enemy][2]-my_board_two[random][1]))/2;
            enemy_board_two[random_enemy][2]-=my_board_two[random][1];
        }
        else    enemy_board_two[random_enemy][3]-=get_ability("W");
        
        
        
        if(enemy_board_two[random_enemy][2]<=0)
        {
            enemy_board_two[random_enemy][0]=0;
            for(int swaper=0; swaper<5; swaper++)
            {
                swap(enemy_board_two[random_enemy][swaper], enemy_board_two[enemy_place-1][swaper]);
            }
        }
        
        if(my_board_two[random][2]<=0)
        {
            my_board_two[random][0]=0;
            my_board_two[random][4]=0;
            for(int swaper=0; swaper<5; swaper++)
            {
                swap(my_board_two[random][swaper], my_board_two[place-1][swaper]);
            }
        }
       
        
    }
    for(int i=0; i<plays_counter; i++)
    {
        final_play[0]+=plays_array[i];
    }
    final_play[1]=to_string(heuristic_value(my_hand, my_board, enemy_board, my_board_two, enemy_board_two, mana, enemy_hp));
    return final_play;
}



 
int main()
{
string my_move;
int my_hp;
int enemy_hp;

int tmp_points;
int points;
string* move_and_value = new string[2];

int empty_hand [8][6]={0};
int empty_board [3][5]={0};

int my_hand [8][6]={0};
int my_board [3][5]={0};
int enemy_board [3][5]={0};
int my_board_two [3][5]={0};
int enemy_board_two [3][5]={0};

int my_hand_copy [8][6]={0};
int my_board_copy [3][5]={0};
int enemy_board_copy [3][5]={0};
int my_board_copy_two [3][5]={0};
int enemy_board_copy_two [3][5]={0};

int my_hand_counter=0;
int my_board_counter=0;
int enemy_board_counter=0;

int drafter_tab [3]={0};
int spells_counter=0;
int playerHealth;
int playerMana;
int my_mana;
int playerDeck;
int playerRune;
int playerDraw;

    // game loop
    while (1) {
        my_hand_counter=0;
        my_board_counter=0;
        enemy_board_counter=0;
        int my_board_counter_two=0;
        int enemy_board_counter_two=0;
        
        std::copy(&empty_hand[0][0], &empty_hand[0][0]+8*6,&my_hand[0][0]);
        std::copy(&empty_board[0][0], &empty_board[0][0]+8*6,&my_board[0][0]);
        std::copy(&empty_board[0][0], &empty_board[0][0]+8*6,&enemy_board[0][0]);
        std::copy(&empty_board[0][0], &empty_board[0][0]+8*6,&my_board_two[0][0]);
        std::copy(&empty_board[0][0], &empty_board[0][0]+8*6,&enemy_board_two[0][0]);
        
        for (int i= 0; i < 2; i++) {
            int playerHealth;
            int playerMana;
            int playerDeck;
            int playerRune;
            int playerDraw;
            cin >> playerHealth >> playerMana >> playerDeck >> playerRune >> playerDraw; cin.ignore();
            if(i==0) 
            {
                my_mana=playerMana;
                my_hp=playerHealth;
            }
            else enemy_hp=playerHealth;
        }
        int opponentHand;
        int opponentActions;
        cin >> opponentHand >> opponentActions; cin.ignore();
        for (int i = 0; i < opponentActions; i++) {
            string cardNumberAndAction;
            getline(cin, cardNumberAndAction);
        }
        int cardCount;
        cin >> cardCount; cin.ignore();
        for (int i = 0; i < cardCount; i++) {
            int cardNumber;
            int instanceId;
            int location;
            int cardType;
            int cost;
            int attack;
            int defense;
            string abilities;
            int myHealthChange;
            int opponentHealthChange;
            int cardDraw;
            int lane;
            cin >> cardNumber >> instanceId >> location >> cardType >> cost >> attack >> defense >> abilities >> myHealthChange >> opponentHealthChange >> cardDraw >> lane; cin.ignore();
            if(my_mana==0)
            {
                drafter_tab[i]=0;
                if(cardNumber==140 || (cardType==0 & attack==0) || (cardType==2 & defense==0))
                {
                    drafter_tab[i]-=10000;
                }
                if(cardNumber == 151)
                {
                    drafter_tab[i]+=10000;
                }
                if(cardType==1)
                {
                    drafter_tab[i]+=8000;
                    spells_counter++;
                }
                if(cardType==2)
                {
                    drafter_tab[i]+=8000;
                    spells_counter++;
                }
                if(cardType==3)
                {
                    drafter_tab[i]-=100000000;
                }
                if(cost<5)
                {
                    drafter_tab[i]+=1100;
                }
                if(cardType!=0 & spells_counter>10)
                {
                    drafter_tab[i]-=60000;
                }
                if(cardType==0 & abilities.find('L') <100)
                {
                    drafter_tab[i]+=1200;
                }
                if(cardType==0 & abilities.find('G') <100)
                {
                    drafter_tab[i]+=1200;
                }
                if(cardType==0 & abilities.find('D') <100)
                {
                    drafter_tab[i]+=800;
                }
                if(cardType==0 & abilities!="------")
                {
                    drafter_tab[i]+=1500;
                }
                //drafter_tab[i]+=440*cardNumber;
                drafter_tab[i]+=cost*10;
                drafter_tab[i]+=abs(defense)*20;
                drafter_tab[i]+=abs(attack)*20;
                drafter_tab[i]=(drafter_tab[i]+abs(drafter_tab[i]))/2;
                drafter_tab[i]+=i;
            }
            if(location==0 & my_mana!=0)
            {
                my_hand[my_hand_counter][0]=instanceId;
                my_hand[my_hand_counter][1]=cost;
                my_hand[my_hand_counter][2]=attack;
                my_hand[my_hand_counter][3]=defense;
                my_hand[my_hand_counter][4]=cardType;
                my_hand[my_hand_counter][5]=get_ability(abilities);
                if(cardNumber==151) my_hand[my_hand_counter][5]=42;
                my_hand_counter++;
            }
            if(location==1 & lane==0)
            {
                my_board[my_board_counter][0]=instanceId;
                my_board[my_board_counter][1]=attack;
                my_board[my_board_counter][2]=defense;
                my_board[my_board_counter][3]=get_ability(abilities);
                my_board[my_board_counter][4]=1;
                my_board_counter++;
            }
            if(location==-1 & lane==0)
            {
                enemy_board[enemy_board_counter][0]=instanceId;
                enemy_board[enemy_board_counter][1]=attack;
                enemy_board[enemy_board_counter][2]=defense;
                enemy_board[enemy_board_counter][3]=get_ability(abilities);
                enemy_board[enemy_board_counter][4]=1;
                enemy_board_counter++;
            }
            if(location==1 & lane==1)
            {
                my_board_two[my_board_counter_two][0]=instanceId;
                my_board_two[my_board_counter_two][1]=attack;
                my_board_two[my_board_counter_two][2]=defense;
                my_board_two[my_board_counter_two][3]=get_ability(abilities);
                my_board_two[my_board_counter_two][4]=1;
                my_board_counter_two++;
            }
            if(location==-1 & lane==1)
            {
                enemy_board_two[enemy_board_counter_two][0]=instanceId;
                enemy_board_two[enemy_board_counter_two][1]=attack;
                enemy_board_two[enemy_board_counter_two][2]=defense;
                enemy_board_two[enemy_board_counter_two][3]=get_ability(abilities);
                enemy_board_two[enemy_board_counter_two][4]=1;
                enemy_board_counter_two++;
            }
        }

        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;


        if(my_mana==0)
        {
            sort(drafter_tab, drafter_tab + 3);
            cout<<("PICK " + to_string(drafter_tab[2]%10))<<endl;
        }
        else
        {
            points=-214748364;
            for(int x=0; x<5500; x++)
            {
                std::copy(&my_hand[0][0], &my_hand[0][0]+8*6,&my_hand_copy[0][0]);
                std::copy(&my_board[0][0], &my_board[0][0]+3*5,&my_board_copy[0][0]);
                std::copy(&enemy_board[0][0], &enemy_board[0][0]+3*5,&enemy_board_copy[0][0]);
                std::copy(&my_board_two[0][0], &my_board_two[0][0]+3*5,&my_board_copy_two[0][0]);
                std::copy(&enemy_board_two[0][0], &enemy_board_two[0][0]+3*5,&enemy_board_copy_two[0][0]);
                move_and_value = my_play(my_hand_copy, my_board_copy, enemy_board_copy, my_board_copy_two, enemy_board_copy_two, my_mana, enemy_hp); 
                tmp_points=std::stoi(move_and_value[1]);
                if(tmp_points>points)
                {
                    points=tmp_points;
                    my_move=move_and_value[0];
                }
            
            }


            cout << (my_move == "" ? "PASS" : my_move) << endl;
        }
            
    }
}
