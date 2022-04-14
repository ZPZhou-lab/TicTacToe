# Web版本的超级井字棋
from tkinter.messagebox import NO
import pywebio
from pywebio import output as o
from pywebio import session
import time

# 当前会话
session_id = 0
# 玩家人数
player_count = [0, 0]

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
    
# 创建游戏棋盘
game_field = GameField()
# 游戏主函数入口
def main():
    global session_id, game_field

    # 玩家退出
    @session.defer_call
    def player_exit():
        # 玩家人数减1
        player_count[my_turn] -= 1
    
    # 判断轮次
    my_turn = session_id % 2
    # 选择棋子
    my_chess = ['🟨', '🟢'][my_turn]
    # 轮次更新
    session_id += 1
    # 玩家人数
    player_count[my_turn] += 1
    # 初始化环境
    session.set_env(title="TicTacToe",output_animation=False)

    # 设置页面
    o.put_html("""\
    <style> \
        table th, table td { padding: 0px !important;} \
        button {padding: .75rem!important; margin:0!important} \
    </style>""")
    # 输出信息
    o.put_markdown(f"""## 超级井字棋""")
    o.put_markdown(f"""所有在线玩家会被分为2组，分别控制黄色方棋🟨和绿色圆棋🟢  
    <font color=royalblue>**当前在线玩家人数:**</font> **{player_count[0]} for 🟨, {player_count[1]} for 🟢**  
    <font color=tomato>**你控制的棋子是 {my_chess}**</font>""")
    
    # 显示棋盘
    @o.use_scope('board', clear=True)
    def show_board():
        table = []
        for x,row in enumerate(game_field.field):
            table_row = []
            for y,cell in enumerate(row):
                if cell == -1:
                    loc = 3 * (x // 3) + (y // 3) + 1
                    if game_field.loc == 0 or loc == game_field.loc:
                        color = 'secondary'
                        label = '⬜'
                    else:
                        color = 'light'
                        label = '⬜'
                    table_row.append(o.put_buttons([dict(label=label, value=[(x, y), my_turn], color=color)], onclick=game_field.set_chess).style("width:50px; height: 50px; text-align: center; vertical-align: middle;"))
                else:
                    table_row.append(o.put_text(['🟨', '🟢'][cell]).style("width:50px; height: 50px; text-align: center; line-height: 50px"))
            table.append(table_row[:])
        # 绘制棋盘
        o.put_markdown(f"""**当前比分：🟨:&nbsp;&nbsp;&nbsp;{game_field.players_score[0]}&nbsp;&nbsp;&nbsp;VS&nbsp;&nbsp;&nbsp;{game_field.players_score[1]}&nbsp;&nbsp;&nbsp;:🟢**""")
        o.put_table(table)
    
    # 显示棋盘
    # o.put_markdown(f"""**当前比分：🟨:&nbsp;&nbsp;&nbsp;{game_field.players_score[0]}&nbsp;&nbsp;&nbsp;VS&nbsp;&nbsp;&nbsp;{game_field.players_score[1]}&nbsp;&nbsp;&nbsp;:🟢**""")
    show_board()
    # 当游戏没有结束时
    while not game_field.check_end():
        with o.use_scope('msg', clear=True):
            # 记录当前轮次
            current_round_copy = game_field.round
            # 如果当前轮次是我的轮次
            if current_round_copy == my_turn:
                o.put_markdown(f"""**你的回合!**""")
            # 如果当前轮次不是我的轮次
            else:
                # 进入等待阶段，放置一个loading的图标
                o.put_row([o.put_markdown(f"""**你对手的回合, 请等待...**"""), o.put_loading().style('width:1.5em; height:1.5em')], size='auto 1fr')
            # 等待下一步操作
            while game_field.round == current_round_copy and not session.get_current_session().closed():
                time.sleep(0.2)
            # 更新棋盘
            if game_field.loc == 0:
                o.toast("你获得任意放置棋子的机会！", color='success')
            show_board()
            
    # 游戏结束，显示获胜者信息
    with o.use_scope('msg', clear=True):
        if game_field.players_score[0] > game_field.players_score[1]:
            winner = '🟨'
        else:
            winner = '🟢'
        o.put_markdown(f"""**游戏结束. 获胜方为 {winner}!**""")
        o.put_markdown(f"""刷新页面开始一局游戏**""")

if __name__ == '__main__':
    pywebio.start_server(main, debug=True, port=9900)