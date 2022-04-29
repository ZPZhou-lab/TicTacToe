# Web版本的超级井字棋
from pickle import FALSE
import pywebio
from pywebio import output as o
from pywebio import input as i
from pywebio import session
from utils import GameField
from utils import update_score
import pandas as pd
import time

# 当前会话
session_id = 0
# 玩家人数
player_info = [None, None]
room_player = {}
refresh = True

# 创建游戏棋盘
game_field = GameField()
# 游戏主函数入口
def main():
    global session_id, game_field, refresh, room_player, player_info

    if refresh:
        session_id = 0
        player_info = [None, None]
        room_player = {}
        game_field.reset()
        refresh = False
        
    def check_user_name(name : str):
        if name in room_player:
            return "房间内有相同的昵称存在，请更换一个昵称！"
    # 输入用户名
    user_name = i.input("设定你的游戏昵称",required=True,validate=check_user_name)

    # 玩家退出
    @session.defer_call
    def player_exit():
        # 玩家人数减1
        if user_name in room_player:
            del room_player[user_name]
    
    # 判断轮次
    my_chess = None
    if session_id < 2:
        my_turn = session_id % 2
        # 选择棋子
        my_chess = ['🟨', '🟢'][my_turn]
        player_info[my_turn] = user_name
    else:
        my_turn = None
    # 轮次更新
    session_id += 1
    # 记录玩家信息
    room_player[user_name] = [my_chess,my_turn,session_id]
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
    
    # 显示玩家堆栈信息
    if session_id == 1:
        while player_info[1] is None:
            with o.use_scope('info', clear=True) as info:
                o.put_markdown(f"""<font color=royalblue>**当前游戏玩家:**</font> **🟨：{player_info[0]}**""")
                o.put_row([o.put_markdown(f"""**等待另一个玩家加入...**"""), o.put_loading().style('width:1.5em; height:1.5em')], size='auto 1fr')
                while player_info[1] is None:
                    time.sleep(0.2)
        o.clear(info)
    o.put_markdown(f"""<font color=royalblue>**当前游戏玩家:**</font> **🟨：{player_info[0]},&nbsp;&nbsp;🟢：{player_info[1]}**""")
    if session_id <= 2:
        o.put_row([o.put_markdown("你的游戏昵称：<font color=magenta>**%s**</font>,&nbsp;&nbsp;"%(user_name)), o.put_markdown(f"""<font color=tomato>**你控制的棋子是 {my_chess}**</font>""")], size='auto 1fr')
    else:
        o.put_row([o.put_markdown("你的游戏昵称：%s,&nbsp;&nbsp;"%(user_name)), o.put_markdown("""<font color=tomato>**在当前房间，你仅能观看比赛**</font>""")], size='auto 1fr')

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
        o.put_markdown(f"""**当前比分：{player_info[0]} 🟨:&nbsp;&nbsp;&nbsp;{game_field.players_score[0]}&nbsp;&nbsp;&nbsp;VS&nbsp;&nbsp;&nbsp;{game_field.players_score[1]}&nbsp;&nbsp;&nbsp;:🟢 {player_info[1]}**""")
        o.put_table(table)
    
    # 显示棋盘
    show_board()
    # 当游戏没有结束时
    abnormal_exit = False
    while not game_field.check_end():
        # 检查玩家是否退出
        if player_info[0] is not None and player_info[1] is not None:
            if player_info[0] not in room_player or player_info[1] not in room_player:
                o.put_markdown("""<font color=red>**有玩家退出了房间，当前游戏结束！**</font>""")
                abnormal_exit = True
                break
        with o.use_scope('msg', clear=True):
            # 记录当前轮次
            current_round_copy = game_field.round
            # 如果当前轮次是我的轮次
            if current_round_copy == my_turn:
                o.put_markdown(f"""**你的回合!**""")
            # 如果当前轮次不是我的轮次
            else:
                # 进入等待阶段，放置一个loading的图标
                if my_turn is not None:
                    o.put_row([o.put_markdown(f"""**你对手的回合, 请等待...**"""), o.put_loading().style('width:1.5em; height:1.5em')], size='auto 1fr')
            # 等待下一步操作
            while game_field.round == current_round_copy and not session.get_current_session().closed() and (player_info[0] in room_player and player_info[1] in room_player):
                time.sleep(0.2)
            # 更新棋盘
            if game_field.loc == 0:
                o.toast("你获得任意放置棋子的机会！", color='success')
            show_board()
    
    # 游戏异常中断
    if abnormal_exit:
        with o.use_scope('msg', clear=True):
            o.put_markdown(f"""**游戏未正常结束，本局游戏不计分！**""")
            o.put_markdown(f"""**刷新页面开始新的一局游戏**""")
            refresh = True
    # 游戏结束，显示获胜者信息
    else:
        with o.use_scope('msg', clear=True):
            score = pd.read_csv("/root/WORK/GameAI/TicTacToe/score.csv",index_col=0)
            if game_field.players_score[0] > game_field.players_score[1]:
                winner = '🟨 %s'%(player_info[0])
                score = update_score(score,player_info[0],win=True,mode="PvP")
                score = update_score(score,player_info[1],win=False,mode="PvP")
            else:
                winner = '🟢 %s'%(player_info[1])
                score = update_score(score,player_info[0],win=False,mode="PvP")
                score = update_score(score,player_info[1],win=True,mode="PvP")
            o.put_markdown(f"""**游戏结束. 获胜方为 {winner}!**""")
            o.put_markdown(f"""**刷新页面开始一局游戏**""")
            score.to_csv("/root/WORK/GameAI/TicTacToe/score.csv")
            refresh = True

if __name__ == '__main__':
    pywebio.start_server(main, debug=True, port=9900)