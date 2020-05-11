import sys
import math
import random
import time
import copy

#meta
#new
#main
#"Well met!","Hello!","Greetings!"
#                  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  150  151  152  153  154  155  156  157  158  159  160
value_lists = [ [116, 68,151, 51, 65, 80,  7, 53, 29, 37, 67, 32,139, 69, 49, 33, 66,147, 18,152, 28, 48, 82, 88, 23, 84, 52, 44, 87,148, 99,121, 64, 85,103,141,158, 50, 95,115,133, 19,109, 54,157, 81,150, 21, 34, 36,135,134, 70,  3, 61,111, 75, 17,144,129,145,106,  9,105, 15,114,128,155, 96, 11,  8, 86,104, 97, 41, 12, 26,149, 90,  6, 13,126, 93, 98, 83, 71, 79, 72, 73, 77, 59,100,137,  5, 89,142,112, 25, 62, 125, 122,  74, 120, 159,  22,  91,  39,  94, 127,  30,  16, 146,   1,  45,  38,  56,  47,   4,  58, 118, 119,  40,  27,  35, 101, 123, 132,   2, 136, 131,  20,  76,  14,  43, 102, 108,  46,  60, 130, 117, 140,  42, 124,  24,  63,  10, 154,  78,  31,  57, 138, 107, 113,  55, 143,  92, 156, 110, 160, 153],
                [ 65, 30, 80, 50, 70, 71,115, 71, 73, 43, 77, 62, 63, 50, 66, 50, 66, 90, 75, 50, 58, 57, 70, 42, 63, 71, 52, 73, 90, 60, 47, 87, 81, 72, 62, 73, 94, 56, 62, 51, 61, 43, 54, 89, 54, 57, 49,109,111, 89,114, 97,115, 93,  2, 54, 25, 63, 62, 58, 79, 79, 15, 82, 92,106,104,146, 98, 70, 56, 65, 52, 54, 65, 55, 77, 48, 75,115, 84, 89, 68, 82, 71, 46, 73, 90, 47, 63, 70, 22, 71, 54, 85, 77, 77, 64, 82,  62,  49,  43, 78,   67,  72,  67,  36,  58,  75,  -8,  85,  69,  32,  82,  98, 124,  35,  60,  59,  65,  97,  55,  35,  22,  45,  54,  51,  60,  59,  38,  31,  43,  66,  55,  50,  41,  70,  38,  83,   1,  30,   2,   1,  55,  45,  12,  67,  77,   3,  78,  91,  55, -30,   0,  52, -10,  10,  69,  30, -20,],
                # [116, 68, 151, 51, 65, 80, 7, 53, 29, 37, 67, 32, 139, 69, 49, 33, 66, 147, 18, 152, 28, 48, 82, 88, 23, 84, 52, 44, 87, 148, 99, 121, 64, 85, 103, 141, 158, 50, 95, 115, 133, 19, 109, 54, 157, 81, 150, 21, 34, 36, 135, 134, 70, 3, 61, 111, 75, 17, 144, 129, 145, 106, 9, 105, 15, 114, 128, 155, 96, 11, 8, 86, 104, 97, 41, 12, 26, 149, 90, 6, 13, 126, 93, 98, 83, 71, 79, 72, 73, 77, 59, 100, 137, 5, 89, 142, 112, 25, 62, 125, 122, 74, 120, 159, 22, 91, 39, 94, 127, 30, 16, 146, 1, 45, 38, 56, 47, 4, 58, 118, 119, 40, 27, 35, 101, 123, 132, 2, 136, 131, 20, 76, 14, 43, 102, 108, 46, 60, 130, 117, 140, 42, 124, 24, 63, 10, 154, 78, 31, 57, 138, 107, 113, 55, 143, 92, 156, 110, 160, 153],
                # [116, 68, 151, 51, 65, 80, 7, 53, 29, 37, 67, 32, 139, 69, 49, 33, 66, 147, 18, 152, 28, 48, 82, 88, 23, 84, 52, 44, 87, 148, 99, 121, 64, 85, 103, 141, 158, 50, 95, 115, 133, 19, 109, 54, 157, 81, 150, 21, 34, 36, 135, 134, 70, 3, 61, 111, 75, 17, 144, 129, 145, 106, 9, 105, 15, 114, 128, 155, 96, 11, 8, 86, 104, 97, 41, 12, 26, 149, 90, 6, 13, 126, 93, 98, 83, 71, 79, 72, 73, 77, 59, 100, 137, 5, 89, 142, 112, 25, 62, 125, 122, 74, 120, 159, 22, 91, 39, 94, 127, 30, 16, 146, 1, 45, 38, 56, 47, 4, 58, 118, 119, 40, 27, 35, 101, 123, 132, 2, 136, 131, 20, 76, 14, 43, 102, 108, 46, 60, 130, 117, 140, 42, 124, 24, 63, 10, 154, 78, 31, 57, 138, 107, 113, 55, 143, 92, 156, 110, 160, 153],
                # [123,72,143,101,139,138,168,137,118,26,114,82,83,33,93,55,94,154,108,32,92,57,103,53,86,132,85,149,158,84,45,152,116,51,43,36,111,128,121,40,58,25,41,146,30,47,119,169,164,150,167,144,162,153,16,49,28,52,88,38,75,68,54,145,163,125,147,166,159,98,78,61,74,48,115,35,69,37,70,156,79,127,130,157,135,91,110,122,65,56,131,15,124,97,141,134,107,80,136,62,46,31,126,76,117,102,23,44,109,12,96,67,20,120,89,160,24,99,100,66,87,64,42,22,71,90,60,77,113,34,29,19,129,63,105,73,106,17,161,14,140,21,18,151,95,50,133,155,27,142,165,104,10,39,112,13,59,148,81,11],
                # [123,72,143,101,139,138,168,137,118,26,114,82,83,33,93,55,94,154,108,32,92,57,103,53,86,132,85,149,158,84,45,152,116,51,43,36,111,128,121,40,58,25,41,146,30,47,119,169,164,150,167,144,162,153,16,49,28,52,88,38,75,68,54,145,163,125,147,166,159,98,78,61,74,48,115,35,69,37,70,156,79,127,130,157,135,91,110,122,65,56,131,15,124,97,141,134,107,80,136,62,46,31,126,76,117,102,23,44,109,12,96,67,20,120,89,160,24,99,100,66,87,64,42,22,71,90,60,77,113,34,29,19,129,63,105,73,106,17,161,14,140,21,18,151,95,50,133,155,27,142,165,104,10,39,112,13,59,148,81,11],
                [117,72,139,101,140,138,165,134,119,26,120,82,83,33,93,55,94,155,108,32,92,57,103,53,86,132,85,147,159,84,45,152,121,51,43,36,116,124,115,40,58,25,41,146,30,47,113,168,164,150,162,144,161,154,16,49,28,52,88,38,75,68,54,145,163,128,151,169,157,98,78,61,74,48,112,35,69,37,70,158,79,129,130,156,135,91,111,125,65,56,127,15,122,97,142,133,107,80,136,62,46,31,126,76,118,102,23,44,110,12,96,67,20,123,89,166,24,99,100,66,87,64,42,22,71,90,60,77,114,34,29,19,131,63,105,73,106,17,160,14,141,21,18,148,95,50,137,153,27,143,167,104,10,39,109,13,59,149,81,11],
                [117,72,139,101,140,138,165,134,119,26,120,82,83,33,93,55,94,155,108,32,92,57,103,53,86,132,85,147,159,84,45,152,121,51,43,36,116,124,115,40,58,25,41,146,30,47,113,168,164,150,162,144,161,154,16,49,28,52,88,38,75,68,54,145,163,128,151,169,157,98,78,61,74,48,112,35,69,37,70,158,79,129,130,156,135,91,111,125,65,56,127,15,122,97,142,133,107,80,136,62,46,31,126,76,118,102,23,44,110,12,96,67,20,123,89,166,24,99,100,66,87,64,42,22,71,90,60,77,114,34,29,19,131,63,105,73,106,17,160,14,141,21,18,148,95,50,137,153,27,143,167,104,10,39,109,13,59,149,81,11],
                # [ 66, 32,115, 53, 81, 87,147,106,123, 17, 92, 85, 75, 26,113, 42,103,148,122, 30,114, 54,130, 20, 59, 91, 31,129,150, 61, 10,156,142, 89, 35, 95,146, 60, 46, 38, 79, 11, 33,136, 40, 23, 57,145,159,127,154,134,153,112,  7, 51, 13, 41, 68, 18, 90, 52, 14,131,152,132,140,157,144,108, 71, 73, 69, 72,111, 25, 62, 21, 83,149,116,138, 76,151,141, 82,125,143, 58, 78, 49,  8, 65, 50,124,118, 99, 80,133, 77, 44, 27,117, 84, 97,100, 15, 28,120,  1,101, 67, 12, 98,121,160, 19, 74,45,47,119,63,34,22,56,86,48,93,104,24,29,37,135,107,102,36,64,9,155,2,94,39,3,109,88,43,139,128,70,105,158,126,4,16,96,5,110,137,55,6],
                # [78,34,122,70,91,95,146,93,112,6,110,84,59,32,103,40,98,148,114,29,109,47,125,20,53,88,30,119,150,57,14,149,134,83,35,81,144,74,61,38,87,12,33,136,39,22,52,152,159,135,151,130,154,111,9,43,17,42,58,23,82,65,18,138,153,127,132,156,145,105,68,55,69,60,106,25,50,15,73,147,117,140,90,157,131,80,128,142,54,75,71,5,79,46,123,129,96,66,133,63,37,24,116,72,89,101,16,26,121,1,104,62,13,102,113,160,19,86,56,76,124,77,44,21,67,85,51,107,108,27,28,36,137,94,97,41,64,10,155,7,120,45,8,126,92,31,141,139,49,118,158,115,2,11,100,3,99,143,48,4],
                # [ 65, 30, 80, 50, 70, 71,115, 71, 73, 43, 77, 62, 63, 50, 66, 50, 66, 90, 75, 50, 58, 57, 70, 42, 63, 71, 52, 73, 90, 60, 47, 87, 81, 72, 62, 73, 94, 56, 62, 51, 61, 43, 54, 89, 54, 57, 49,109,111, 89,114, 97,115, 93,  2, 54, 25, 63, 62, 58, 79, 79, 15, 82, 92,106,104,146, 98, 70, 56, 65, 52, 54, 65, 55, 77, 48, 75,115, 84, 89, 68, 82, 71, 46, 73, 90, 47, 63, 70, 22, 71, 54, 85, 77, 77, 64, 82,  62,  49,  43, 78,   67,  72,  67,  36,  58,  75,  -8,  85,  69,  32,  82,  98, 124,  35,  60,  59,  65,  97,  55,  35,  22,  45,  54,  51,  60,  59,  38,  31,  43,  66,  55,  50,  41,  70,  38,  83,   1,  30,   2,   1,  55,  45,  12,  67,  77,   3,  78,  91,  55, -30,   0,  52, -10,  10,  69,  30, -20,],
                # [ 41, 32, 57, 57, 57, 57, 70, 58, 62, 46, 31, 55, 43, 50, 66, 45, 66, 70, 67, 42, 48, 46, 66, 14, 40, 57, 30, 53, 55, 48, 46, 56, 58, 57, 41, 59, 60, 51, 41, 21, 35, 28, 47, 83, 49, 27, 57, 75, 84, 72, 80, 70, 86, 89, 20, 51, 43, 55, 47, 40, 50, 57, 48, 58, 78, 67, 70,105, 72, 51, 45, 45, 45, 49, 60, 37, 47, 22, 47, 68, 54, 67, 35, 38, 37, 33, 58, 51, 44, 36, 51,  9, 51, 56, 63, 62, 52, 70, 77,  39,  68,  42,  72,  70,  60,  60,  32,  22,  67,  20,  60,  52,  27,  54,  65,  90,  20,  55,  35,  65,  50,  40,  30,  15,  22,  25,  33,  30,  30,  28,  15,  16,  43,  40,  40,  45,  55,   5,  55,  35,  30,   2,   1,  90,  30,  20,  15,  37,   3,  78,  86,  40, -30,   0,  52, -10,  10,  69,  39, -20,],
                # [ 50, 36, 80, 28, 55, 57, 78, 58, 65, 46, 32, 59, 43, 17, 66, 23, 66, 68, 67, 19, 50, 48, 55, 20, 33, 57, 39, 15, 15, 26, 10, 29, 33, 38, 35, 39, 60, 58, 43, 35, 35, 18, 47, 71, 53, 40, 64, 75, 70, 69, 80, 62, 80, 89, 10, 30, 20, 56, 48, 49, 40, 43, 11, 52, 78, 63, 70, 78, 71, 50, 45, 43, 40, 40, 50, 50, 48, 13, 46, 53, 50, 55, 35, 35, 50, 28, 40, 51, 30, 20, 13,  9, 47, 24, 59, 60, 52, 42, 45,  38,  34,  29,  59,  50,  54,  49,  31,  22,  67,   4,  60,  47,  10,  53,  40,  73,  15,  27,  22,  30,  23,  30,  16,  20,  24,  25,  33,  24,  35,  30,  15,  16,  40,  15,  30,  10,  51,  11,  50,  12,  11,   2,   1,  14,  19,  12,  10,  37,   3,  78,  86,  35, -30,   0,  52, -10,  10,  69,  25, -20,],
                # [ 93, 68, 107, 56, 86, 73, 203, 61, 59, 45, 75, 50, 61, 92, 58, 66, 58, 84, 57, 69, 62, 58, 62, 52, 65, 74, 54, 83, 95, 63, 44, 98, 99, 88, 87, 135, 99, 82, 93, 46, 69, 48, 47, 112, 53, 45, 56, 502, 263, 198, 160, 146, 137, 185, 41, 45, 39, 47, 55, 38, 60, 62, 183, 181, 203, 102, 95, 108, 71, 71, 73, 60, 56, 56, 62, 47, 55, 35, 55, 110, 70, 84, 105, 201, 73, 54, 67, 83, 75, 64, 77, 18, 97, 53, 66, 78, 59, 50, 55, 47, 48, 46, 56, 59, 54, 59, 38, 38, 57, 31, 59, 48, 29, 59, 75, 142,  35,  60,  59,  49,  72,  54,  35,  22,  50,  54,  51,  54,  59,  38,  31,  43,  62,  55,  57,  41,  70,  38,  76,   1,  11,   2,   1,  14,  19,  12,  10,  37,   3,  78,  86,  35, -30,   0,  52, -10,  10,  69,  25, -20,],
                # [ 88, 63,100, 50, 81, 68,200, 56, 54, 43, 70, 45, 57, 87, 53, 62, 53, 78, 52, 65, 57, 54, 57, 50, 62, 69, 51, 81, 93, 59, 42, 95, 96, 85, 85,133, 95, 75, 88, 43, 67, 45, 44,109, 49, 42, 50,500,261,195,156,143,137,183, 36, 40, 34, 43, 51, 35, 55, 58,180,180,200,100, 92,104, 66, 66, 71, 56, 52, 52, 57, 44, 51, 33, 51,106, 67, 81,100,200, 70, 50, 64, 80, 73, 62, 67, 18, 92, 48, 61, 73, 55, 46, 50,  42,  45,  43,  51,  55,  50,  55,  36,  35,  52,  27,  55,  44,  27,  55,  73, 139,  35,  60,  59,  49,  72,  54,  35,  22,  50,  54,  51,  54,  59,  38,  31,  43,  62,  55,  57,  41,  70,  38,  76,   1,  11,   2,   1,  14,  19,  12,  10,  37,   3,  78,  86,  35, -30,   0,  52, -10,  10,  69,  25, -20,],
                # [ 58, 56, 85, 67, 58, 56, 57, 55, 55, 29, 57, 54, 49, 64, 55, 49, 55, 70, 55, 51, 55, 51, 59, 30, 43, 56, 42, 33, 34, 47, 29, 42, 47, 43, 33, 42, 55, 82, 58, 37, 31, 35, 41, 48, 46, 40, 67, 75, 51, 52, 59, 45, 19, 43, 53, 54, 53, 45, 51, 42, 58, 53, 55, 30, 57, 35, 46, 56, 64, 56, 32, 49, 48, 45, 55, 41, 51, 31, 51, 57, 37, 40, 60, 32, 40, 46, 43, 43, 27, 34, 106, 1, 59, 54, 56, 57, 47, 46, 55, 54, 42, 35, 55, 49, 50, 50, 28, 38, 55, 42, 51, 46, 23, 51, 35, 45,  35,  60,  59,  49,  72,  54,  35,  22,  50,  54,  51,  54,  59,  38,  31,  43,  62,  55,  57,  41,  70,  38,  76,   1,  11,   2,   1,  14,  19,  12,  10,  66,   3,  78,  86,  35, -30,   0,  52, -10,  10,  69,  25, -20,],
                [ 58, 40, 85, 67, 58, 56, 57, 55, 55, 29, 57, 54, 49, 64, 55, 49, 55, 70, 55, 51, 55, 51, 59, 30, 43, 56, 42, 33, 34, 47, 29, 42, 47, 43, 33, 42, 55, 82, 58, 37, 31, 35, 41, 48, 46, 40, 67, 75, 51, 52, 59, 45, 19, 43, 53, 54, 53, 45, 51, 42, 58, 53, 55, 30, 57, 35, 46, 56, 64, 56, 32, 49, 48, 45, 55, 41, 51, 31, 51, 57, 37, 40, 60, 32, 40, 46, 43, 43, 27, 34, 106, 1, 59, 54, 56, 57, 47, 46, 55, 54, 42, 35, 55, 49, 50, 50, 28, 38, 55, 42, 51, 46, 23, 51, 35, 45,  35,  60,  59,  49,  72,  54,  35,  22,  50,  54,  51,  54,  59,  38,  31,  43,  62,  55,  57,  41,  70,  38,  76,   1,  11,   2,   1,  14,  19,  12,  10,  66,   3,  78,  86,  35, -30,   0,  52, -10,  10,  69,  25, -20,]]
static_values = []
card_values = []
selector = random.randint(0,2)
# selector = 0

# aggressive
# late game
# mid game
# control curve
# aggro curve
# midrange to test curve
manaCurve_lists = [ [0, 3, 5, 6, 6, 4, 3, 3],
                    [0, 3, 6, 7, 5, 3, 3, 3],
                    [0, 2,12, 6, 6, 1, 3, 0],
                    [0, 2, 6, 5, 5, 5, 4, 3],
                    [0, 2, 5, 6, 7, 5, 3, 2],
                    [0, 6, 8, 4, 2, 3, 3, 4],
                    [2, 9, 8,10, 1, 0, 0, 0],
                    [0, 1, 8, 6, 4, 3, 3, 3],
                    [0, 0, 6, 4, 6, 2, 2, 2]]
manaCurve_selector = random.randint(0,len(manaCurve_lists)-1)

ownCurve = [0, 0, 0, 0, 0, 0, 0, 0]

# containers
players = []

cards = []

hand = []
board = []
oboard = []

position = 1

deck = []
moves = []
bestMoves = []

currentBoardValue = 0
output = ""

class player:
    def __init__(self,player_health, player_mana, player_deck, player_rune, player_draw):
        self.hp = player_health
        self.mp = player_mana
        self.d = player_deck
        self.r = player_rune
        self.draw = player_draw

    def update(self,player_health, player_mana, player_deck, player_rune, player_draw):
        self.hp = player_health
        self.mp = player_mana
        self.d = player_deck
        self.r = player_rune
        self.draw = player_draw

class card:
    def __init__(self, card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, lane, _id):
        self.n = card_number
        self.i = instance_id
        self.l = location
        self.t = card_type
        self.c = cost
        self.a = attack
        self.d = defense
        self.ab = abilities
        self.hp = my_health_change
        self.ohp = opponent_health_change
        self.dr = card_draw
        self.lane = lane
        self._id = _id
        self.value = card_values[card_number -1]
        self.ready = True

def guarded():
    for i in range(len(oboard)):
        if "G" in oboard[i].ab:
            return i
    return -1

def haveGuard():
    g = []
    for i in range(len(board)):
        if "G" in board[i].ab:
            g.append(i)
    return g

def evalHand():
    for h in hand:
        if manaCurve[ min(h.c,7) ]-1 > 0 and (h.t == 0 or h.t == 2 or h.t == 3 and h.d < 0):
            h.value += 30
        elif manaCurve[ min(h.c,7) ]-1 < 0 or h.t == 1:
            h.value -= 30

def evalHand2():
    global position
    for h in hand:
        if h.c >= 7 and ownCurve[ min(h.c,7) ] >= 3 and "G" not in h.ab:
            h.value -= 10
        if h.c == 6 and ownCurve[ 6 ] >= 3 and "G" not in h.ab:
            h.value -= 10

def lethal():
    dmg = 0
    for b in board:
        if b.ready:
            dmg += b.a
    return players[1].hp - dmg

def boardEval():
    tVal = 0
    for b in board:
        if b.d > 0 and b.l == 1:
            tVal += b.a + b.d/10 + (("W" in b.ab) + ("G" in b.ab) + ("L" in b.ab)) / 10
    for o in oboard:
        if o.d > 0:
            tVal -= o.a + o.d/10 + (("W" in o.ab) + ("G" in o.ab) + ("L" in o.ab)) / 10
    bonus = (players[0].hp <= 0) * -10000 + (players[1].hp <= 0) * 10000
    return tVal + players[0].hp/100 - players[1].hp/100 + bonus - guarded() * 5

def missedLethal():
    global output
    if lethal() <= 0 and guarded() == -1:
        for b in board:
            if len(output) > 0:
                output += ";"
            output += "ATTACK " + str(b.i) + " -1 Goodbye!"
            b.ready = False

def simulateOpponent(newCard):
    testb = copy.deepcopy(board)
    testo = oboard[:]
    if newCard == None or newCard.t > 0:
        return 0
    else:
        testb.append(newCard)

    guardCount = len(haveGuard())

    oVal = 0
    surv = 0

    if guardCount >= 1:
        bb = newCard
        for oo in testo:
            if oo.d + ("W" in oo.ab) * 10000 - (bb.a + ("L" in bb.ab) * 1000) > 0:
                pass
            elif bb.d + ("W" in bb.ab) * 10000 - (oo.a + ("L" in oo.ab) * 1000) <= 0:
                pass
            else:
                oVal += 2
        return oVal
    elif newCard != None:
        bb = newCard
        for oo in testo:
            if oo.d + ("W" in oo.ab) * 10000 - (bb.a + ("L" in bb.ab) * 1000) > 0:
                if bb.d + ("W" in bb.ab) * 10000 - (oo.a + ("L" in oo.ab) * 1000) <= 0:
                    oVal -= 1
                else:
                    oVal += 1
            elif bb.d + ("W" in bb.ab) * 10000 - (oo.a + ("L" in oo.ab) * 1000) <= 0:
                oVal -= 0
            else:
                oVal += 2
        return oVal

    if newCard == None:
        pass
    else:
        testb.remove(newCard)

    return oVal

def moveGen():
    global position
    global currentBoardValue
    currentBoardValue = boardEval()
    global moves
    global output
    mVal = currentBoardValue
    # beforeState = simulateOpponent(None)
    # afterValue = beforeState
    afterValue = 0
    for h in hand:
        if players[1].hp + h.ohp <= 0:
            mVal += 10000
        if players[0].mp >= h.c:
            if h.t == 0 and len(board) < 6:
                temp = mVal
                if h.n == 53 and len(oboard) == 0 and players[1].hp > 10 and len(hand) + players[0].draw < 7:
                    mVal -= 10
                if "C" in h.ab:
                    guard = guarded()
                    for o in oboard:
                        if guard != -1 and "G" not in o.ab:
                            continue
                        if (o.d <= h.a or "L" in h.ab) and "W" not in o.ab:
                            mVal += h.a * (o.a > h.d or "L" in o.ab) and "W" not in h.ab + o.ab
                            if "L" in h.ab and ("L" not in o.ab and o.a <= 2 and o.d <= 2):
                                mVal -= 20
                            elif ("L" in o.ab or o.a >= 4):
                                mVal += 2 * ("L" in o.ab) + o.a
                    if lethal() - h.a <= 0 and guarded() == -1:
                        mVal += 10000
                        missedLethal()
                else:
                    if "L" not in h.ab and len(oboard) == 1 and oboard[0].a + 2 >= h.a and "L" in oboard[0].ab and h.a > oboard[0].d and "W" not in oboard[0].ab:
                        mVal += 2
                    if len(oboard) == 1 and "L" not in oboard[0].ab and h.a + 2 >= oboard[0].a and "L" in h.ab and oboard[0].a > h.d and "W" not in h.ab:
                        mVal = max(currentBoardValue, mVal-2)
                    manaLeft = players[0].mp - h.c
                    for h2 in hand[hand.index(h)+1:]:
                        if h2.t > 0:
                            continue
                        if manaLeft >= h2.c:
                            if len(board) < 5:
                                moves.append(["SUMMON " + str(h.i) + " " + random.choice(["0","1"]) + " Oops!" + ";SUMMON " + str(h2.i) + " " + random.choice(["0","1"]) + " Oops!", mVal, [["h", h, h2]], ((mVal + h.a + h.d + ("L" in h.ab) * 10 + h2.a + h2.d + ("L" in h2.ab) * 10) + max(simulateOpponent(h) + simulateOpponent(h2),0)) ])
                moves.append(["SUMMON " + str(h.i) + " " + random.choice(["0","1"]) + " Oops!", mVal, [["h", h]], ((mVal + h.a + h.d + ("L" in h.ab) * 10 ) + max(simulateOpponent(h),0)) ])
                mVal = temp
                afterValue = 0
            elif h.t == 1 and len(board) > 0 and len(oboard) == 0 and h.a > 0:
                for b in board:
                    moves.append(["USE " + str(h.i) + " " + str(b.i) + " Well Played!", mVal, [["h", h],["b", b]], mVal + h.a + 0.00001])
            elif (h.t == 2 or h.t == 3) and len(oboard) > 0:
                for o in oboard:
                    temp = mVal
                    if o.c == 0:
                        continue
                    if h.d + o.d <= 0 and ("W" not in o.ab or "W" in h.ab):
                        mVal += o.a + o.d + ("L" in o.ab)*5
                    else:
                        mVal -= h.a
                    if "W" in h.ab and "W" in o.ab or "L" in h.ab and "L" in o.ab:
                        mVal += 1
                    moves.append(["USE " + str(h.i) + " " + str(o.i) + " My magic will tear you apart!", mVal, [["h",h],["o",o]], mVal ])
                    mVal = temp
            elif h.t == 3:
                if players[1].hp + h.ohp <= 0:
                    temp = 10000
                    moves.append(["USE " + str(h.i) + " -1 The Light shall burn you!", temp, [["h", h]], temp ])
                elif players[1].hp + lethal() + h.d + h.ohp <= 0:
                    moves.append(["USE " + str(h.i) + " -1 The Light shall burn you!", 10000, [["h", h]], mVal ])
    guard = guarded()
    for b in board:
        if not b.ready:
            continue
        temp = mVal
        if guard == -1:
            missedLethal()
            mVal -= b.a
            ma = 0
            oa = 0
            # if guarded() == -1:
            for bb in board:
                if bb.ready:
                    ma += bb.a
            # if len(haveGuard()) == 0:
            for oo in oboard:
                oa += oo.a
            if oa > players[0].hp and ma < players[1].hp:
                mVal -= 10000
            if haveGuard() or players[0].hp > oa:
                mVal += 1
            moves.append(["ATTACK " + str(b.i) + " -1 Justice demands retribution!", mVal, [["b", b]], (mVal + b.a) ])
            mVal = temp
        for o in oboard:
            if (guard >= 0 or o.a == 0) and "G" not in o.ab or o.lane != b.lane:
                continue
            if "G" in o.ab and o.a == 0:
                mVal += 0.0009
            temp = mVal
            deadOpp  = (o.d <= b.a or "L" in b.ab) and "W" not in o.ab
            deadUnit = (b.d <= o.a or "L" in o.ab) and "W" not in b.ab
            if deadOpp:
                mVal += (o.a + o.d * 0.01 + len(o.ab) * 0.01 + ("L" in o.ab) * 0.1 + ("L" in o.ab and "L" not in b.ab and b.a <= o.a+2))
                if deadUnit:
                    if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                        mVal -= 10
            if deadUnit:
                mVal -= b.a
            afterValue = mVal
            if deadOpp:
                totalAttack = 0
                for ta in board:
                    if ta.ready and ta.i != b.i:
                        totalAttack += ta.a
                if "L" in o.ab and "G" in o.ab and totalAttack > 0:
                    afterValue += totalAttack
                if "G" in o.ab and totalAttack > 0:
                    afterValue += totalAttack
                    if (b.d <= o.a or "L" in o.ab) and "W" not in b.ab:
                        pass
                    else:
                        afterValue += b.a
                myGuards = haveGuard()
                extraValue = 0
                for bb in board:
                    if bb.i == b.i or len(myGuards) > 0 and "G" not in bb.ab or bb.lane != b.lane:
                        continue
                    if (bb.d <= o.a or "L" in o.ab) and "W" not in bb.ab and ((o.d <= bb.a or "L" in bb.ab) and "W" not in o.ab) == False:
                        extraValue = max(extraValue, bb.a )
                    elif (bb.d <= o.a or "L" in o.ab) and "W" not in bb.ab and bb.a > b.a:
                        extraValue = max(extraValue, bb.a )
                afterValue += extraValue
            if "B" in b.ab and "W" not in o.ab and b.a - o.d >= players[1].hp:
                mVal += 10000
            if len(board) == 6:
                mVal += 10
            if b.a == 0:
                mVal -= 50
                afterValue -= 50
            moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal, [["b", b], ["o", o]], afterValue ])
            if b.a == 0:
                mVal += 50
                afterValue += 50
            if deadUnit and o.d > b.a and "L" not in b.ab and "W" not in o.ab:
                for h2 in hand:
                    if h2.c <= players[0].mp and h2.t == 1 and ("W" in h2.ab or b.d + h2.d > o.a and "L" not in o.ab) and (h2.a + b.a >= o.d or "L" in h2.ab):
                        mVal += b.a + h2.a + o.a
                        afterValue += b.a + h2.a + o.a
                        if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                            mVal += 10
                        moves.append(["USE " + str(h2.i) + " " + str(b.i) + " Well Played!", mVal + 0.1, [["h", h2], ["b", b]], afterValue ])
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.01, [["b", b], ["o", o]], afterValue ])
                        if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                            mVal -= 10
                        mVal -= b.a + h2.a + o.a
                        afterValue -= b.a + h2.a + o.a
                    if h2.c <= players[0].mp and (h2.t == 2 or h2.t == 3) and (b.d > o.a + h2.a and ("L" not in o.ab or "L" in h.ab)) and (b.a >= o.d + h.d):
                        mVal += b.a + o.a
                        afterValue += b.a + o.a
                        if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                            mVal += 10
                        moves.append(["USE " + str(h2.i) + " " + str(o.i) + " Well Played!", mVal + 0.1, [["h", h2], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.01, [["b", b], ["o", o]], afterValue ])
                        if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                            mVal -= 10
                        mVal -= b.a + o.a
                        afterValue -= b.a + o.a
                for bb in board:
                    if bb.i == b.i or "L" in bb.ab or not bb.ready or bb.lane != b.lane:
                        continue
                    if bb.a + b.a >= o.d:
                        mVal += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
                        afterValue += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.002, [["b", b], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(bb.i) + " " + str(o.i) + " For justice!", mVal + 0.003, [["b", bb], ["o", o]], afterValue ])
                        mVal += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
                        afterValue += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
            elif deadUnit:
                for h2 in hand:
                    if h2.c <= players[0].mp and h2.t == 1 and ("W" in h2.ab or b.d + h2.d > o.a and "L" not in o.ab):
                        deadEnemy = ((h2.a + b.a >= o.d or "L" in h2.ab) and "W" not in o.ab) * o.a
                        mVal += b.a + deadEnemy
                        afterValue += b.a + h2.a + deadEnemy
                        if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                            mVal += 10
                        moves.append(["USE " + str(h2.i) + " " + str(b.i) + " Well Played!", mVal + 0.01, [["h", h2], ["b", b]], afterValue ])
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.001, [["b", b], ["o", o]], afterValue ])
                        if "G" in b.ab and "G" not in o.ab and len(board) == len(oboard) == 1:
                            mVal -= 10
                        mVal -= b.a + deadEnemy
                        afterValue -= b.a + h2.a + deadEnemy
                    if h2.c <= players[0].mp and h2.t == 2 and (b.d > o.a + h2.a and ("L" not in o.ab or "L" in h.ab)):
                        deadEnemy = ((h2.a + b.a >= o.d or "L" in h2.ab) and "W" not in o.ab) * o.a
                        mVal += b.a + deadEnemy
                        afterValue += b.a
                        if "G" in b.ab and ("G" not in o.ab or "G" in h2.ab) and len(board) == len(oboard) == 1:
                            mVal += 10
                        moves.append(["USE " + str(h2.i) + " " + str(o.i) + " Well Played!", mVal + 0.01, [["h", h2], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.001, [["b", b], ["o", o]], afterValue ])
                        if "G" in b.ab and ("G" not in o.ab or "G" in h2.ab) and len(board) == len(oboard) == 1:
                            mVal -= 10
                        mVal -= b.a + deadEnemy
                        afterValue -= b.a
            elif o.d > b.a and "L" not in b.ab and "W" not in o.ab:
                for h2 in hand:
                    if h2.c <= players[0].mp and h2.t == 1 and (h2.a + b.a >= o.d or "L" in h2.ab):
                        mVal += o.a + h2.a
                        afterValue += o.a + h2.a
                        moves.append(["USE " + str(h2.i) + " " + str(b.i) + " Well Played!", mVal + 0.001, [["h", h2], ["b", b]], afterValue ])
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.0001, [["b", b], ["o", o]], afterValue ])
                        mVal -= o.a + h2.a
                        afterValue -= o.a + h2.a
                    if h2.c <= players[0].mp and (h2.t == 2 or h2.t == 3) and (b.a >= o.d + h.d):
                        mVal += o.a
                        afterValue += o.a
                        moves.append(["USE " + str(h2.i) + " " + str(o.i) + " Well Played!", mVal + 0.001, [["h", h2], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.0001, [["b", b], ["o", o]], afterValue ])
                        mVal -= o.a
                        afterValue -= o.a
                for bb in board:
                    if bb.i == b.i or "L" in bb.ab or not bb.ready or bb.lane != b.lane:
                        continue
                    if bb.a + b.a >= o.d:
                        mVal += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
                        afterValue += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.002, [["b", b], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(bb.i) + " " + str(o.i) + " For justice!", mVal + 0.003, [["b", bb], ["o", o]], afterValue ])
                        mVal += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
                        afterValue += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)
            elif "W" in o.ab:
                for bb in board:
                    if bb.i == b.i or not bb.ready or bb.a == 0 or bb.lane != b.lane:
                        continue
                    if bb.a > o.d or "L" in bb.ab:
                        mVal += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) - b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                        afterValue += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) - b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.002, [["b", b], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(bb.i) + " " + str(o.i) + " For justice!", mVal + 0.003, [["b", bb], ["o", o]], afterValue ])
                        mVal += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) + b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                        afterValue += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab)  + b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                    elif b.a >= o.d or "L" in b.ab:
                        mVal += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) - b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                        afterValue += o.a - bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) - b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                        moves.append(["ATTACK " + str(b.i) + " " + str(o.i) + " For justice!", mVal + 0.003, [["b", b], ["o", o]], afterValue ])
                        moves.append(["ATTACK " + str(bb.i) + " " + str(o.i) + " For justice!", mVal + 0.002, [["b", bb], ["o", o]], afterValue ])
                        mVal += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) + b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
                        afterValue += - o.a + bb.a * (bb.d <= o.a or "L" in o.ab and "W" not in bb.ab) + b.a * (b.d <= o.a or "L" in o.ab and "W" not in b.ab)
            mVal = temp
            afterValue = 0
    print(mVal, file=sys.stderr)
    print("moves ",len(moves), file=sys.stderr)
    for m in moves:
        print(m, file=sys.stderr)

def applyMoves():
    global bestMoves
    global output
    print(bestMoves[0], file=sys.stderr)
    m = bestMoves[0]
    if len(m[2]) == 1:
        if m[2][0][0] == "h":
            for h in m[2][0][1:]:
                if players[0].mp < h.c:
                    return
                # creature gets played
                if h.t == 0:
                    if "C" in h.ab:
                        h.ready = True
                    else:
                        h.ready = False
                    board.append(h)
                elif h.t == 3:
                    players[1].hp += h.d
                players[0].hp += h.hp
                players[1].hp += h.ohp
                hand.remove(h)
                if len(output) > 0:
                    output += ";"
                output += m[0]
                players[0].mp -= h.c
        # creature hits player
        else:
            m[2][0][1].ready = False
            if len(output) > 0:
                output += ";"
            output += m[0]
            players[1].hp -= m[2][0][1].a
            if "D" in m[2][0][1].ab:
                players[0].hp += m[2][0][1].a
    else:
        # spells
        if m[2][0][0] == "h":
            if players[0].mp < m[2][0][1].c:
                return
            if m[2][0][1].t == 1:
                m[2][1][1].a += m[2][0][1].a
                m[2][1][1].d += m[2][0][1].d
                for _char in m[2][0][1].ab:
                    if _char not in m[2][1][1].ab:
                        m[2][1][1].ab += _char
            elif m[2][0][1].t == 2:
                m[2][1][1].d += m[2][0][1].d
                if m[2][1][1].d <= 0:
                    oboard.remove(m[2][1][1])
                else:
                    m[2][1][1].a += m[2][0][1].a
                    for _char in m[2][0][1].ab:
                        m[2][0][1].ab.replace(_char, "")
            elif m[2][0][1].t == 3:
                m[2][1][1].d += m[2][0][1].d
                if m[2][1][1].d <= 0:
                    oboard.remove(m[2][1][1])
            hand.remove(m[2][0][1])
            players[0].hp += m[2][0][1].hp
            players[1].hp += m[2][0][1].ohp
            if len(output) > 0:
                output += ";"
            output += m[0]
            players[0].mp -= m[2][0][1].c
        # creature hits creature
        elif m[2][0][1] in board and m[2][1][1] in oboard:
            m[2][0][1].ready = False
            if "W" in m[2][0][1].ab:
                m[2][0][1].ab.replace("W", "")
            else:
                if "L" in m[2][1][1].ab or m[2][0][1].d <= m[2][1][1].a:
                    board.remove(m[2][0][1])
                else:
                    m[2][0][1].d -= m[2][1][1].a
                if "B" in m[2][0][1].ab and m[2][0][1].a > m[2][1][1].d:
                    players[1].hp += m[2][1][1].d - m[2][0][1].a
            if "W" in m[2][1][1].ab:
                m[2][1][1].ab.replace("W", "")
            else:
                if "L" in m[2][0][1].ab or m[2][1][1].d <= m[2][0][1].a:
                    oboard.remove(m[2][1][1])
                else:
                    m[2][1][1].d -= m[2][0][1].a
            if len(output) > 0:
                output += ";"
            output += m[0]



def moveGen2(pos):
    global currentBoardValue
    currentBoardValue = boardEval()
    global output
    global best_output
    global best_score
    global board
    global players
    global oboard
    global on_board
    global on_enemy_board
    global ready_count

    # oboard.sort(key=lambda x: "G" in x.ab, reverse = True)
    # get idx in oboard of first obj with no "G"
    # enemy_guards = [x.idx for x in oboard if "G" in x.ab]
    # other_targets = [x.idx for x in oboard if "G" not in x.ab]
    # attackers = [x.idx for x in board if (x.l == 1 and x.ready or "C" in x.ab and x.l == 0 and players[0].mp >= x.c and x.t == 0 and on_board < 6)]
    attackers = [x for x in board if (x.l == 1 and x.ready or "C" in x.ab and x.l == 0 and players[0].mp >= x.c and x.t == 0 and on_board < 6)]
    weapons = [x for x in board if x.t == 1 and players[0].mp >= x.c]
    guardC = guarded()

    for b in attackers[pos:]:
        ready_ = b.l == 1 and b.ready
        charger = "C" in b.ab and b.l == 0 and players[0].mp >= b.c and b.t == 0 and on_board < 6
        if ready_ or charger:
            if charger:
                players[0].mp -= b.c
                b.l = 1
                on_board += 1
                ready_count += 1
                players[0].hp += b.hp
                players[1].hp += b.ohp

            b.ready = False
            ready_count -= 1

            if guardC < 0:
                players[1].hp -= b.a
                if "D" in b.ab:
                    players[0].hp += b.a

                to_cut = len(output)

                if charger:
                    if len(output) > 0:
                        output += ";"
                    output += "SUMMON " + str(b.i) + " " + random.choice(["0","1"])

                if len(output) > 0:
                    output += ";"
                output += "ATTACK " + str(b.i) + " -1"

                new_score = boardEval()
                if new_score > best_score:
                    best_score = new_score
                    best_output = output

                moveGen(attackers.index(b))

                if "D" in b.ab:
                    players[0].hp -= b.a
                players[1].hp += b.a
                output = output[:to_cut]

            targets = []
            if guardC >= 0:
                targets = [x for x in oboard if "G" in x.ab and x.d > 0]
            else:
                #
                # missedlethal
                #
                targets = [x for x in oboard if x.d > 0]
            for o in targets:
                if o.d > 0 and (guardC <= 0 or "G" in o.ab):
                    if "B" in b.ab and b.a > o.d:
                        players[1].hp -= b.a - o.d
                    if "D" in b.ab:
                        players[0].hp += min(o.d,b.a)
                    warded_b = False
                    warded_o = False
                    if "W" in b.ab:
                        warded_b = True
                        b.ab.replace("W", "")
                    else:
                        b.d -= o.a
                        if "L" in o.ab:
                            b.d -= 100
                    if "W" in o.ab:
                        warded_o = True
                        o.ab.replace("W", "")
                    else:
                        o.d -= b.a
                        if "L" in b.ab:
                            o.d -= 100

                    to_cut = len(output)

                    if charger:
                        if len(output) > 0:
                            output += ";"
                        output += "SUMMON " + str(b.i) + " " + random.choice(["0","1"])

                    if len(output) > 0:
                        output += ";"
                    output += "ATTACK " + str(b.i) + " " + str(o.i)

                    new_score = boardEval()
                    if new_score > best_score:
                        best_score = new_score
                        best_output = output

                    moveGen(attackers.index(b))

                    if warded_b:
                        b.ab += "W"
                    else:
                        b.d += o.a
                        if "L" in o.ab:
                            b.d += 100
                    if warded_o:
                        o.ab += "W"
                    else:
                        o.d += b.a
                        if "L" in b.ab:
                            o.d += 100
                    if "D" in b.ab:
                        players[0].hp -= min(o.d,b.a)
                    if "B" in b.ab and b.a > o.d:
                        players[1].hp += b.a - o.d
                    output = output[:to_cut]

            b.ready = True
            ready_count += 1
            if charger:
                on_board -= 1
                b.l = 0
                players[0].mp += b.c
                ready_count -= 1
                players[0].hp -= b.hp
                players[1].hp -= b.ohp

    return

    for o in oboard:
        o.attack_list = []
        attackers = [x for x in board if (x.l == 1 and x.ready or "C" in x.ab and x.l == 0 and players[0].mp >= x.c and x.t == 0 and on_board < 6)]
        for b in attackers:
            if o.d <= b.a:
                o.attack_list.append([o.idx,b.idx])
            else:
                remaining_attackers = [x.idx for x in attackers[attackers.index(b)+1:] if (x.l == 1 and x.ready or "C" in x.ab and x.l == 0 and players[0].mp >= x.c and x.t == 0 and on_board < 6)]
                for i in range(len(remaining_attackers)-1):
                    b2 = list(itertools.combinations(remaining_attackers,i))
                    for bb in b2:
                        if o.d <= sum(board[x].a for x in bb):
                            o.attack_list.append( ([o.idx,b.idx] + b2) )

    return


def summonGen():
    global currentBoardValue
    currentBoardValue = boardEval()
    global best_output
    global output
    output = best_output
    global best_score
    best_score = currentBoardValue
    global board
    global players
    global oboard
    global on_board
    global on_enemy_board

    playable = [x for x in board if (x.l == 0 and players[0].mp >= x.c and x.t == 0 and on_board < 6)]

    possible_plays = []

    for pl in playable:
        possible_plays.append([pl])

    for i in range(1,len(playable)):
        p2 = list(itertools.combinations(playable,i))
        for pp in p2:
            if players[0].mp >= sum(x.c for x in pp) and i + on_board <= 6:
                possible_plays.append(pp)

    for p in possible_plays:
        to_cut = len(output)

        for b in p:#
            players[0].mp -= b.c
            b.l = 1
            on_board += 1
            players[0].hp += b.hp
            players[1].hp += b.ohp
            if "C" in b.ab:
                b.ready = True

            if len(output) > 0:
                output += ";"
            output += "SUMMON " + str(b.i) + " " + random.choice(["0","1"])

        new_score = boardEval()
        if new_score > best_score:
            best_score = new_score
            best_output = output

        for b in p:
            on_board -= 1
            b.l = 0
            players[0].mp += b.c
            players[0].hp -= b.hp
            players[1].hp -= b.ohp

        output = output[:to_cut]


def applyMoves2():
    global best_output
    global board
    global players
    global oboard
    global on_board
    global on_enemy_board

    moves = best_output.split(";")

    for m in moves:
        move = m.split(" ")
        b = [x for x in board if x.i == int(move[1])][0]
        if move[0] == "SUMMON":
            players[0].mp -= b.c
            b.l = 1
            on_board += 1
            players[0].hp += b.hp
            players[1].hp += b.ohp
            if "C" in b.ab:
                b.ready = True
        if move[0] == "ATTACK":
            if move[2] == '-1':
                players[1].hp -= b.a
                if "D" in b.ab:
                    players[0].hp += b.a
            else:
                o = [x for x in oboard if x.i == int(move[2])][0]
                if "B" in b.ab and b.a > o.d:
                    players[1].hp -= b.a - o.d
                if "D" in b.ab:
                    players[0].hp += min(o.d,b.a)
                if "W" in b.ab:
                    b.ab.replace("W", "")
                else:
                    b.d -= o.a
                    if "L" in o.ab:
                        b.d -= 100
                if "W" in o.ab:
                    o.ab.replace("W", "")
                else:
                    o.d -= b.a
                    if "L" in b.ab:
                        o.d -= 100
        if move[0] == "USE":
            pass



for i in range(2):
    p = player( 0, 0, 0, 0, 0)
    players.append(p)

turn = 0
creat = 0
other = 0

# game loop
while True:
    turn += 1
    cards = []
    hand = []
    board = []
    oboard = []
    moves = []

    iniTime = time.process_time()
    for i in range(2):
        player_health, player_mana, player_deck, player_rune, player_draw = [int(j) for j in input().split()]

        players[i].update(player_health, player_mana, player_deck, player_rune, player_draw)

    if turn == 1:
        if players[0].d < players[1].d:
            position = 2
            selector = 3
            manaCurve_selector = 4
        else:
            selector = 2
            manaCurve_selector = 4
        # manaCurve_selector = 6

        manaCurve = manaCurve_lists[manaCurve_selector][:]
        static_values = value_lists[selector][:]
        card_values = value_lists[selector][:]

    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    for i in range(opponent_actions):
        card_number_and_action = input()
    card_count = int(input())

    for i in range(card_count):
        card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, lane = input().split()

        card_number = int(card_number)
        instance_id = int(instance_id)
        location = int(location)
        card_type = int(card_type)
        cost = int(cost)
        attack = int(attack)
        defense = int(defense)
        abilities = abilities.replace("-", "")
        my_health_change = int(my_health_change)
        opponent_health_change = int(opponent_health_change)
        card_draw = int(card_draw)
        lane = int(lane)

        c = card(card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw, lane, i)

        if location == 0 and (cost <= players[0].mp or turn <= 30):
            hand.append(c)
        elif location == 1:
            board.append(c)
        elif location == -1:
            oboard.append(c)

    t0 = time.process_time()

    if turn <= 30:

        if turn > 20:
            evalHand()
        evalHand2()

        if other < 10:
            if turn < 20:
                hand.sort(key=lambda x: ( x.value*-1, x.a == 0 and x.t == 0, x.c, (x.a + x.d)/max(x.c,1) * -1 ,len(x.ab)*-1 ) )
            else:
                hand.sort(key=lambda x: ( x.value*-1, x.a == 0 and x.t == 0, (x.a + x.d)/max(x.c,1) * -1 ,len(x.ab)*-1 ) )
        else:
            hand.sort(key=lambda x: ( x.value*-1, x.a == 0 and x.t == 0, x.c, (x.a + x.d)/max(x.c,1) * -1 ,len(x.ab)*-1 ) )

        fakeWinMsg = random.randint(0,9)

        if hand[0].n == hand[1].n or hand[0].n == hand[2].n or hand[2].n == hand[1].n:
            print("PICK 0")
        elif turn == 1:
            print( "PICK",hand[0]._id,["Well met!","Hello!","Greetings!","Greetings, traveler.","","!","?"][selector] )
        else:
            print( "PICK",hand[0]._id,random.choice(["Well met!","Hello!","Greetings!"]) )

        if hand[0].t == 0:
            creat += 1
        else:
            other += 1

        deck.append(hand[0])

        manaCurve[ min(7,hand[0].c) ] -= 1
        ownCurve[ min(7,hand[0].c) ] += 1

        # if hand[0].t > 0 and hand[0].c > 3:
        #     card_values[hand[0].n -1] -= 20

        print(manaCurve, file=sys.stderr)
        for h in hand:
            print(h.n,h.value, file=sys.stderr)

        if turn == 30:
            card_values = static_values

    else:
        output = ""

        currentBoardValue = boardEval()
        bestScore = currentBoardValue


        # moveGen2(0)
        # if len(best_output) > 0:
        #     applyMoves2()
        # summonGen()


        while True:
            moves = []
            missedLethal()
            moveGen()
            if len(moves) == 0:
                break
            bestMoves = [x for x in moves if x[1] > currentBoardValue]
            bestMoves.sort(key=lambda x: (x[1], x[3]), reverse=True)
            if len(bestMoves) > 0:
                applyMoves()
                missedLethal()
            elif len(moves) > 0:
                bestMoves = [x for x in moves if x[3] > currentBoardValue]
                bestMoves.sort(key=lambda x: (x[1], x[3]), reverse=True)
                if len(bestMoves) > 0:
                    applyMoves()
                    missedLethal()
                else:
                    break

        for b in board:
            if not b.ready:
                continue

            guard = guarded()

            if guard != -1:
                extraAtt = ("W" in oboard[guard].ab)

            hpleft = 0

            if guard != -1 and b.a > 0 and oboard[guard].d > b.a and ("L" not in b.ab or "W" in oboard[guard].ab):
                xx = 0
                hpleft = oboard[guard].d
                for bb in board:
                    xx += 1
                    if xx == 1 and extraAtt or bb.a == 0:
                        continue
                    if bb.ready:
                        hpleft -= bb.a

            dmgleft = 0
            for bb in board:
                if bb.ready:
                    dmgleft += bb.a

            if guard != -1 and b.a > 0 and hpleft <= 0 and bb.a > hpleft and (bb.a <= oboard[guard].a or players[0].hp < oboard[guard].a):
                if len(output) > 0:
                    output += ";"
                output += "ATTACK " + str(b.i) + " " + str(oboard[guard].i) + " WELL MET!"

                if "W" not in oboard[guard].ab:
                    oboard[guard].d -= b.a
                else:
                    oboard[guard].ab.replace("W", "")
                if oboard[guard].d <= 0 or "L" in b.ab and "W" not in oboard[guard].ab:
                    oboard.pop(guard)
                b.ready = False
            elif guard == -1:
                if len(output) > 0:
                    output += ";"
                output += "ATTACK " + str(b.i) + " -1 Goodbye!"
                b.ready = False

        if len(output) > 0:
            if turn == 31:
                print(output," Estimated win probability:"+str(manaCurve_selector+4)+str(fakeWinMsg)+"%")
            else:
                print(output," GET WRECKED!")
        else:
            if turn == 31:
                print("PASS Estimated win probability:"+str(manaCurve_selector+4)+str(fakeWinMsg)+"%")
            else:
                print("PASS GET REKT")

    now = time.process_time()
    print("time passed",now - iniTime, file=sys.stderr)







