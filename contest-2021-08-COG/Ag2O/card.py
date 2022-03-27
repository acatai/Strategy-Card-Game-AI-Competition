
class Card:
    def __init__(self, card_id=0):
        self.id = card_id           # card id
        self.score = 0              # card score
        self.link_list = []         # card link list
        self.link_score = [0]*160   # link card score
        self.update_num = 0         # update number

    # score update
    def update_score(self,q):
        self.score += q
        self.update_num += 1
    
    # print card score
    def print_info(self):
        print("card_info: id=",self.id," score=",self.score," update_num=",self.update_num)
        print("link_list=",self.link_list)
    
    # reset update number
    def reset(self):
        self.update_num = 0
    
    # cut the link
    def link_out(self):
        temp_list = []
        for id in self.link_list:
            if 0 < self.link_score[id-1]:
                temp_list.append(id)
        self.link_list = temp_list

        if self.score <= 0:
            self.link_list = []
            self.link_score = [0]*160
    
    # total link card score
    def sum_link_score(self):
        res = 0
        for scr in self.link_score:
            res += scr

        if len(self.link_score) > 0:
            res = res / len(self.link_score)
        return res
    
    # maximum link card score
    def max_link_score(self):
        res = 0
        for scr in self.link_score:
            if res < abs(scr):
                res = abs(scr)
        return res