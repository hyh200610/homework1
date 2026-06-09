import random
class chouka:
    def __init__(self, name="default",baodi=0,dabaodi=0):
        self.name = name
        self.baodi=baodi
        self.dabaodi=dabaodi
    def set_up(self,up="庄方宜"):
        self.up=up
    def set_other6(self,other6=["汤汤","洛茜","余烬","别礼","艾尔黛拉","骏卫","黎风"]):
        self.other6=other6
    def set_other5(self,other5=["佩丽卡","大潘","弧光","昼雪","狼卫","艾维文娜","赛希","阿列什","陈千语"]):
        self.other5=other5
    def set_other4(self,other4=["卡契尔","埃特拉","安塔尔","秋栗","萤石"]):
        self.other4=other4
    def choujiang(self,times): 
        result=[]
        for i in range(times):
            who=random.randint(1,1000)
            if who<=8+max(0,(self.dabaodi-65))*50 and who>=1:
                if random.randint(0,1)==0:
                    wo=(f"****** {random.choice(self.other6)}")
                    self.baodi=0
                    self.dabaodi=0
                else:
                    wo=(f"****** {self.up}")
                    self.baodi=0
                    self.dabaodi=0
                self.baodi=0
                self.dabaodi=0
            elif who<=80+max(0,(self.dabaodi-65))*50 and who>8+max(0,(self.dabaodi-65))*50:
                wo=(f"***** {random.choice(self.other5)}")
                self.baodi=0 
                self.dabaodi=self.dabaodi+1
            else:
                wo=(f"**** {random.choice(self.other4)}")   
                self.baodi=self.baodi+1
                self.dabaodi=self.dabaodi+1
            if self.baodi == 10 and self.dabaodi != 80:
                wo=(f"***** {random.choice(self.other5)}")
                self.baodi=0
            elif self.dabaodi == 80:
                if random.randint(0,1)==0:
                    wo=(f"****** {random.choice(self.other6)}")
                else:
                    wo=(f"****** {self.up}")
                self.dabaodi=0
                self.baodi=0
            
            result.append(wo)
        return result


        
