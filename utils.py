from operator import mod
from signal import raise_signal
import pywebio
from pywebio import output as o
from pywebio import input as i
from pywebio import session
import random
import pandas as pd
import time

class GameField:
    def __init__(self) -> None:
        # 玩家得分
        self.players_score = [0, 0]
        # 总棋子数
        self.count = 0
        # 棋盘
        self.field = [[-1]*9 for _ in range(9)]
        # 当前轮次
        self.round = 0
        # loc确定当前可行的棋子范围
        self.loc = 0 # 0表示可以在任意位置下棋
        self.last_pos = None # 记录上一步棋子的位置
        # 重置棋盘
        self.reset()
    
    # 重置棋盘
    def reset(self):
        # 玩家得分
        self.players_score = [0, 0]
        # 总棋子数
        self.count = 0
        self.loc = 0
        self.last_pos = None
        # 棋盘
        self.field = [[-1]*9 for _ in range(9)]
    
    # 检查游戏是否结束
    def check_end(self):
        if self.count == 81:
            return True
        return False
    
    # 检查当前位置是否能放置棋子
    def check_pos(self, pos : tuple):
        if self.loc == 0:
            return True
        x, y = pos
        loc = 3 * (x // 3) + (y // 3) + 1
        if loc == self.loc:
            return True
        return False
    
    def check_loc(self):
        # 获取当前网格范围
        r1 = 3*( (self.loc-1) // 3)
        r2 = r1 + 3
        c1 = 3*( (self.loc-1) % 3)
        c2 = c1 + 3
        for x in range(r1,r2):
            for y in range(c1,c2):
                if self.field[x][y] == -1:
                    return True
        return False
        
    # 更新游戏分数
    def update_score(self, pos : list) -> None:
        """
        update_score(self, pos : list) -> None
            更新游戏分数
        
        Parameters
        ----------
        pos : list
            最后一步操作的坐标
        """
        piece = 1 if self.round == 1 else 0
        # 获取当前网格范围
        r1 = 3*( (self.loc-1) // 3)
        r2 = r1 + 3
        c1 = 3*( (self.loc-1) % 3)
        c2 = c1 + 3
        # 检验横轴
        cnt = 0
        for i in range(c1,c2):
            if self.field[pos[0]][i] == piece:
                cnt += 1
        if cnt == 3:
            self.players_score[self.round] += 1
        # 检验纵轴
        cnt = 0
        for i in range(r1,r2):
            if self.field[i][pos[1]] == piece:
                cnt += 1
        if cnt == 3:
            self.players_score[self.round] += 1
        # 检验对角线
        diag = [(r1 + i,c1 + i) for i in range(3)]
        anti_diag = [(r1 + i,c2 - 1 - i) for i in range(3)]
        if pos in diag:
            cnt = 0
            for x,y in diag:
                if self.field[x][y] == piece:
                    cnt += 1
            if cnt == 3:
                self.players_score[self.round] += 1
        if pos in anti_diag:
            cnt = 0
            for x,y in anti_diag:
                if self.field[x][y] == piece:
                    cnt += 1
            if cnt == 3:
                self.players_score[self.round] += 1
    
    def set_chess(self, args):
        pos = args[0]
        my_turn = args[1]
        if my_turn is None:
            o.toast("你仅能观看比赛", color='error')
            return
        else:
            # 当前不是你的回合
            if self.round != my_turn:
                o.toast("当前不是你的回合", color='error')
                return
            # 如果当前位置无法放置棋子
            if not self.check_pos(pos):
                o.toast("当前不能在该位置放置棋子！", color='error')
                return
        # 放置棋子
        x, y = pos
        self.field[x][y] = my_turn
        self.last_pos = (x,y)
        # 更新分数
        if self.loc == 0:
            self.loc = 3 * (x % 3) + (y % 3) + 1
        self.update_score(pos)
        # 更新下棋位置
        self.loc = 3 * (x % 3) + (y % 3) + 1
        # 判断是否有下棋点，没有则获得任意下棋的机会
        if not self.check_loc():
            self.loc = 0
            o.toast("对手获得一次任意放置棋子的机会！", color='success')
        # 切换轮次
        self.round = (self.round + 1) % 2
        self.count += 1


class GameAI:
    def __init__(self, level : str="入门") -> None:
        self.level = level

    def __call__(self, game_field : GameField) -> None:
        # 获得可行的方案
        fesible_move = self._get_fesible_move(game_field)
        try:
            assert(self.level in ["入门"])
        except:
            raise Exception("难度设置错误")
        if self.level == "入门":
            time.sleep(0.6)
            game_field.set_chess(args=[random.choice(fesible_move),1])
    
    def set_level(self, level : str) -> None:
        self.level = level

    def _get_fesible_move(self, game_field : GameField) -> list:
        res = []
        # 获得任意下棋的机会
        for x in range(9):
            for y in range(9):
                loc = 3 * (x // 3) + (y // 3) + 1
                if (game_field.loc == 0 or game_field.loc == loc) and game_field.field[x][y] == -1:
                    res.append([x,y])
        return res


def update_score(score : pd.DataFrame, player : str, win : bool=True, mode : str="PvP", level : str=None) -> pd.DataFrame:
    if win:
        if player not in list(score["玩家昵称"]):
            record = pd.Series(
                {
                    "玩家昵称": player,
                    "PvP次数": 0,
                    "PvP胜率": 0.0,
                    "PvE次数": 0,
                    "PvE胜率": 0.0,
                    "挑战成功最高难度AI": "无记录",
                    "综合胜率": 1.0
                }
            )
            record["%s次数"%(mode)] = 1
            record["%s胜率"%(mode)] = 1.0
            if mode == "PvE":
                record["挑战成功最高难度AI"] = level
            score.append(record,ignore_index=True)
        else:
            idx = score["玩家昵称"] == player
            score.loc[idx,"%s胜率"%(mode)] =\
                    int(score.loc[idx,"%s胜率"%(mode)] * score.loc[idx,"%s次数"%(mode)] + 1) / (score.loc[idx,"%s次数"%(mode)] + 1)
            score.loc[idx,"%s次数"%(mode)] += 1
            score.loc[idx,"综合胜率"] =\
                int(score.loc[idx,"PvP胜率"] * score.loc[idx,"PvP次数"] + score.loc[idx,"PvE胜率"] * score.loc[idx,"PvE次数"]) / (score.loc[idx,"PvP次数"] + score.loc[idx,"PvE次数"])
            if mode == "PvE":
                score.loc[idx,"挑战成功最高难度AI"] = level
    else:
        if player not in list(score["玩家昵称"]):
            record = pd.Series(
                {
                    "玩家昵称": player,
                    "PvP次数": 0,
                    "PvP胜率": 0.0,
                    "PvE次数": 0,
                    "PvE胜率": 0.0,
                    "挑战成功最高难度AI": "无记录",
                    "综合胜率": 0.0
                }
            )
            record["%s次数"%(mode)] = 1
            score.append(record,ignore_index=True)
        else:
            idx = score["玩家昵称"] == player
            score.loc[idx,"%s胜率"%(mode)] =\
                    int(score.loc[idx,"%s胜率"%(mode)] * score.loc[idx,"%s次数"%(mode)]) / (score.loc[idx,"%s次数"%(mode)] + 1)
            score.loc[idx,"%s次数"%(mode)] += 1
            score.loc[idx,"综合胜率"] =\
                int(score.loc[idx,"PvP胜率"] * score.loc[idx,"PvP次数"] + score.loc[idx,"PvE胜率"] * score.loc[idx,"PvE次数"]) / (score.loc[idx,"PvP次数"] + score.loc[idx,"PvE次数"])
    return score