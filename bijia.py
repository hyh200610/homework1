class bijia:
    def __init__(self, name, talpr, per):
        self.talpr = talpr  # 总价
        self.per = per      # 单位量
        self.name = name

    def get_arr(self):
        # 计算 单价 = 总价 / 单位
        return self.talpr / self.per

    @staticmethod
    def compare(a, b):
        arr_a = a.get_arr()
        arr_b = b.get_arr()

        # ========== 正确比价逻辑 ==========
        if arr_a < arr_b:
            # A 更便宜
            res = f"{a.name} 更便宜，单价：{arr_a:.2f}"
        
        elif arr_b < arr_a:
            # B 更便宜
            res = f"{b.name} 更便宜，单价：{arr_b:.2f}"
        
        else:
            # 单价一样 → 比总价，总价低的更划算
            if a.talpr < b.talpr:
                res = f"{a.name} 更划算（单价相同({arr_a:.2f}元/单位)总价更低）"
            else:
                res = f"{b.name} 更划算（单价相同({arr_b:.2f}元/单位)总价更低）"
        
        return res