# 超级井字棋的主页index
from email import header
import pywebio
from pywebio import output as o
from pywebio import input as i
from pywebio import session
import pandas as pd
import time


# 主函数入口
def main():
    # 设置页面
    o.put_html("""\
    <style> \
        table th, table td { padding: 0px !important;} \
        button {padding: .75rem!important; margin:0!important} \
    </style>""")

    # 游戏title
    o.put_markdown(f"""## 超级井字棋""")
    o.put_markdown(f"""### 游戏规则""")
    o.put_markdown(f""">1 棋盘被分为9个大宫格，每个大宫格又是一个小的九宫格""")
    o.put_markdown(f""">2 先手玩家可以在任意位置放置棋子""")
    o.put_markdown(f""">3 之后的每一步棋子都需要放置在对手落棋位置对应的大宫格内""")
    o.put_markdown(f""">4 如果对应大宫格内无空位，则当前玩家获得一次任意放置棋子的机会""")
    o.put_markdown(f""">5 直到棋盘被占满时，游戏结束，双方统计每个大宫格内<font color=tomato>**连成3颗**</font>的数目（<font color=royalblue>**包括水平、竖直和左右对角线**</font>）跨过不同大宫格的3颗棋子不参与计数""")
    o.put_markdown(f""">6 <font color=tomato>**得分高者获胜**</font>""")
    o.put_row(
        [o.put_html(""" <style>
            .button1 {
                -webkit-transition-duration: 0.4s;
                transition-duration: 0.4s;
                padding: 16px 40px;
                text-align: center;
                background-color: #007AFF;
                color: white;
                border: 1px solid white;
                border-radius: 3px;
            }
            .button1:hover {
                background-color: #0064D1;
                color: white;
            }
            </style>
            <a href="http://47.100.64.248:%d/TicTacToeWeb"><button class="button1">随机对战</button></a>
        """%(8990)),
        o.put_html(""" <style>
            .button1 {
                -webkit-transition-duration: 0.4s;
                transition-duration: 0.4s;
                padding: 16px 40px;
                text-align: center;
                background-color: #007AFF;
                color: white;
                border: 1px solid white;
                border-radius: 3px;
            }
            .button1:hover {
                background-color: #0064D1;
                color: white;
            }
            </style>
            <a href="http://47.100.64.248:%d/TicTacToeAI"><button class="button1">挑战AI</button></a>
        """%(8990))]
    ,size='auto 1fr')

    score = pd.read_csv("score.csv",index_col=0)
    score.sort_values(by="综合胜率",ascending=False,inplace=True)
    
    header = [
        o.put_text("昵称").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
        o.put_text("PvP场次").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
        o.put_text("PvP胜率").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
        o.put_text("PvE场次").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
        o.put_text("PvE胜率").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
        o.put_text("最高难度AI").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
        o.put_text("综合胜率").style("width:100px; height: 40px; text-align: center; line-height: 40px"),
    ]
    tdata = [header]
    for s in score.head(5).values:
        tdata.append([
            o.put_text(s[0]).style("width:100px; height: 40px; text-align: center; line-height: 40px"), 
            o.put_text(s[1]).style("width:100px; height: 40px; text-align: center; line-height: 40px"), 
            o.put_text("%.2f"%(s[2]*100) + "%").style("width:100px; height: 40px; text-align: center; line-height: 40px"), 
            o.put_text(s[3]).style("width:100px; height: 40px; text-align: center; line-height: 40px"), 
            o.put_text("%.2f"%(s[4]*100) + "%").style("width:100px; height: 40px; text-align: center; line-height: 40px"), 
            o.put_text(s[5]).style("width:100px; height: 40px; text-align: center; line-height: 40px"), 
            o.put_text("%.2f"%(s[6]*100) + "%").style("width:100px; height: 40px; text-align: center; line-height: 40px") 
        ])
    o.put_markdown("""### 排行榜""")
    o.put_table(
        tdata=tdata,
    )


if __name__ == '__main__':
    pywebio.start_server(main, debug=True, port=9901)