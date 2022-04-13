import curses
import _curses
from collections import defaultdict

# 操纵键盘
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq\n']
# 对应的相应按钮
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions * 2 + ['Enter']))

# 从键盘获取用户操作
def get_user_action(keyboard : _curses.window):
    char = 'N'
    while char not in actions_dict:
        # 返回按下键的 ascii 码值
        char = keyboard.getch()

    return actions_dict[char]

class ListNode:
    def __init__(self, val) -> None:
        self.val = val
        self.next = None
        self.last = None

# 定义游戏界面
class GameField:
    def __init__(self):
        # 棋盘的高和宽
        self.height = 9
        self.width = 9
        # 玩家1和玩家2的游戏分数
        self.player1_score = 0
        self.player2_score = 0
        # 这一轮该谁
        self.round = 1 # Player 1先手
        # 当前定位格
        self.loc = 0 # 默认等于0，可以从任意位置开始
        self.choice = [4,4] # 默认棋子在棋盘中心
        # 统计棋盘上的棋子数量
        self.count = 0
        self.mode = 'PvP' # 游戏模式
        self.modes = {
            "PvP": ListNode("PvP"),
            "PvE": ListNode("PvE"),
            "Rules": ListNode("Rules")
        }
        self.modes["PvP"].next = self.modes["PvE"]
        self.modes["PvP"].last = self.modes["Rules"]
        self.modes["PvE"].next = self.modes["Rules"]
        self.modes["PvE"].last = self.modes["PvP"]
        self.modes["Rules"].next = self.modes["PvP"]
        self.modes["Rules"].last = self.modes["PvE"]
        # 棋盘初始化
        self.reset()
    
    # 选择模式
    def choose_mode(self, screen : _curses.window, action : str=None):
        # 显示信息
        def cast(string : str):
            screen.addstr(string + '\n')
        welcome = 'TicTacToe'
        PvP = ['   ','Two Players Game (PvP)']
        PvE = ['   ','Challenge AI (PvE) [Not finished yet!]']
        help = ['   ','Game Rules']
        help_string1 = '(WS)Choose Mode (Enter)Confirm (Q)Exit'
        # 绘制
        screen.clear()
        cast(welcome)
        if self.mode == "PvP":
            PvP[0] = ' > '
        elif self.mode == 'PvE':
            PvE[0] = ' > '
        else:
            help[0] = ' > '
        cast(''.join(PvP))
        cast(''.join(PvE))
        cast(''.join(help))
        cast(help_string1)
        if action == 'Up':
            self.mode = self.modes[self.mode].last.val
        if action == "Down":
            self.mode = self.modes[self.mode].next.val
    
    def Rules(self, screen : _curses.window):
        # 显示信息
        def cast(string : str):
            screen.addstr(string + '\n')
        rule0 = 'The entire 9 * 9 chessboard is divided into NINE 3 * 3 sub regions, \n\
which we call A. each sub region A is a 3 * 3 grid'
        rule1 = '> RULES 1: The first player can place pieces anywhere in the 9 * 9 grid'
        rule2 = '> RULES 2: For each subsequent step, you need to: '
        rule2_1 = "\t> RULES 2.1: Consider which location the opponent's last move is in that tends to sub region A"
        rule2_2 = "\t> RULES 2.2: Your next chess piece can only be placed in the corresponding sub region A"
        rule2_3 = '\t> RULES 2.3: If there is no space in the corresponding sub area A, you will get a chance to place the chess pieces anywhere you want'
        rule3 = '> RULES 3: When all empty spaces are filled, the score is counted: '
        rule3_1 = "\t> RULES 3.1: Each player's pieces are connected into 3 pieces (including horizontal, vertical, diagonal and anti diagonal) in each sub area A, 1 point will be obtained"
        rule3_2 = "\t> RULES 3.2: Even if the pieces crossing sub area A are connected into 3 pieces, they will not participate in the counting"
        rule4 = "> RULES 4: The one with the highest score wins"
        note = "If you find the rules hard to understand, just try to play!"
        help_string1 = '(Q)Exit'
        screen.clear()
        cast(rule0)
        cast(rule1)
        cast(rule2)
        cast(rule2_1)
        cast(rule2_2)
        cast(rule2_3)
        cast(rule3)
        cast(rule3_1)
        cast(rule3_2)
        cast(rule4)
        cast(note)
        cast(help_string1)

    # 重置界面
    def reset(self):
        # 玩家1和玩家2的游戏分数
        self.player1_score = 0
        self.player2_score = 0
        # 棋盘
        self.field = [['#' for _ in range(self.width)] for _ in range(self.height)]
        self.round = 1 # Player 1先手
        # 当前定位格
        self.loc = 0 # 默认等于0，可以从任意位置开始
        self.choice = [4,4] # 默认棋子在棋盘中心
        self.count = 0

    # 是否游戏是否还能进行    
    def can_move(self):
        if self.choice[0] == self.choice[1] == -1:
            return False
        return True
    
    # 检查游戏是否已经结束
    def end(self):
        if self.count == 81:
            return True
        return False

    # 获得任意选择的机会
    def arbitrary_opportunity(self):
        # 找到第一个可以放置棋子的坐标
        for x in range(9):
            for y in range(9):
                if self.field[x][y] == '#':
                    self.choice = [x,y]
        self.loc = 0

    # 更新分数
    def update_score(self):
        piece = '□' if self.round == 1 else '+'
        # 获取当前网格范围
        r1 = 3*( (self.loc-1) // 3)
        r2 = r1 + 3
        c1 = 3*( (self.loc-1) % 3)
        c2 = c1 + 3
        # 检验横轴
        cnt = 0
        for i in range(c1,c2):
            if self.field[self.choice[0]][i] == piece:
                cnt += 1
        if cnt == 3:
            if self.round == 1:
                self.player1_score += 1
            else:
                self.player2_score += 1
        # 检验纵轴
        cnt = 0
        for i in range(r1,r2):
            if self.field[i][self.choice[1]] == piece:
                cnt += 1
        if cnt == 3:
            if self.round == 1:
                self.player1_score += 1
            else:
                self.player2_score += 1
        # 检验对角线
        diag = [[r1 + i,c1 + i] for i in range(3)]
        anti_diag = [[r1 + i,c2 - 1 - i] for i in range(3)]
        if self.choice in diag:
            cnt = 0
            for x,y in diag:
                if self.field[x][y] == piece:
                    cnt += 1
            if cnt == 3:
                if self.round == 1:
                    self.player1_score += 1
                else:
                    self.player2_score += 1
        if self.choice in anti_diag:
            cnt = 0
            for x,y in anti_diag:
                if self.field[x][y] == piece:
                    cnt += 1
            if cnt == 3:
                if self.round == 1:
                    self.player1_score += 1
                else:
                    self.player2_score += 1

    def update_choice(self):
        r1 = 3*( (self.loc-1) // 3)
        r2 = r1 + 3
        c1 = 3*( (self.loc-1) % 3)
        c2 = c1 + 3
        for x in range(r1,r2):
            for y in range(c1,c2):
                # 如果是空位
                if self.field[x][y] == '#':
                    return [x,y]
        # 无法找到任何空位
        return [-1,-1]

    # 绘制界面
    def draw(self, screen : _curses.window):
        help_string1 = '  (WASD)Control Move (Enter)Confirm'
        help_string2 = "         (R)Restart, (Q)Exit"
        player1_win = '            Player 1 WIN'
        player2_win = '            Player 2 WIN'
        drew_string = '          it ends in a draw'

        # 显示信息
        def cast(string : str):
            screen.addstr(string + '\n')

        # 绘制水平分割线
        def draw_hor_separator(mode : str='boundary'):
            line = '+' + ('+---+---+---' * 3 + '+')[1:]
            boundary = '+' + ('+===+===+===' * 3 + '+')[1:]
            if mode == 'boundary':
                cast(boundary)
            if mode == 'line':
                cast(line)

        # 绘制每一行
        def draw_row(row_idx : int, row : list):
            show = ['‖',' ',' ',' ','|',' ',' ',' ','|',' ',' ',' '] * 3 + ["‖"]
            # 为对应位置添加棋子
            for i,piece in enumerate(row):
                # '#‘表示空棋子
                if piece != '#':
                    show[4*i+2] = piece
            # 绘制当前的移动棋子
            if row_idx == self.choice[0]:
                piece = '□' if self.round == 1 else '+'
                show[self.choice[1]*4 + 2] = piece
                show[self.choice[1]*4 + 1] = '>'
                show[self.choice[1]*4 + 3] = '<'
            show = "".join(show)
            cast(show)

        # 清空屏幕
        screen.clear()
        cast('')
        cast('P1 SCORE: %-7d VS %7d P2 SCORE'%(self.player1_score,self.player2_score))
        cast('           ROUND: Player %d'%(self.round))
        
        # 绘制棋盘
        for i,row in enumerate(self.field):
            mode = 'boundary' if i % 3 == 0 else 'line'
            draw_hor_separator(mode)
            draw_row(i,row)
        draw_hor_separator('boundary')
        # 无法继续移动棋子
        if not self.can_move():
            # 判断胜负情况
            if self.player1_score > self.player2_score:
                cast(player1_win)
            elif self.player1_score == self.player2_score:
                cast(drew_string)
            else:
                cast(player2_win)
        # 还可以继续移动棋子
        else:
            cast(help_string1)
        cast(help_string2)
    # 每一次操作的移动
    def move(self, action):
        if action in ['Up', 'Left', 'Down', 'Right', 'Enter']:
            # 移动棋子
            if action != 'Enter':
                if action == 'Up':
                    bound = 3*( (self.loc-1) // 3) if self.loc != 0 else 0
                    self.choice[0] = self.choice[0] - 1 if self.choice[0] > bound else self.choice[0]
                elif action == 'Down':
                    bound = 3*( (self.loc-1) // 3) + 2 if self.loc != 0 else 8
                    self.choice[0] = self.choice[0] + 1 if self.choice[0] < bound else self.choice[0]
                elif action == 'Left':
                    bound = 3*( (self.loc-1) % 3) if self.loc != 0 else 0
                    self.choice[1] = self.choice[1] - 1 if self.choice[1] > bound else self.choice[1]
                else:
                    bound = 3*( (self.loc-1) % 3) + 2 if self.loc != 0 else 8
                    self.choice[1] = self.choice[1] + 1 if self.choice[1] < bound else self.choice[1]
            # 确认下棋
            else:
                # 确认下棋
                if self.field[self.choice[0]][self.choice[1]] == '#':
                    piece = '□' if self.round == 1 else '+'
                    self.field[self.choice[0]][self.choice[1]] = piece
                    self.count += 1
                    # 更新分数
                    if self.loc == 0:
                        self.loc = 3 * (self.choice[0] % 3) + (self.choice[1] % 3) + 1
                    self.update_score()
                    # 更新下棋位置
                    self.loc = 3 * (self.choice[0] % 3) + (self.choice[1] % 3) + 1
                    self.choice = self.update_choice()
                    # 交换轮次
                    self.round = 2 if self.round == 1 else 1
            return True
        # 不在有效操作中，返回False
        return False

# 定义状态机
def main(stdscr : _curses.window):
    def mode():
        # 选择游戏模式
        game_field.choose_mode(stdscr)
        # 读取用户输入得到action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        if action == 'Enter':
            if game_field.mode != 'Rules':
                return 'Init'
            else:
                return 'Rules'
        elif action in ["Up",'Down']:
            game_field.choose_mode(stdscr,action)
        elif action == "Exit":
            return "Exit"
        return 'Mode'
    
    def rules():
        # 展示游戏规则
        game_field.Rules(stdscr)
        # 读取用户输入得到action，判断是重启游戏还是结束游戏
        action = 'N'
        while action != 'Exit':
            action = get_user_action(stdscr)
        return 'Mode'

    def init():
        # 重置游戏棋盘
        game_field.reset()
        return 'Game'

    # 游戏结束
    def not_game(state):
        # 绘制结束画面
        game_field.draw(stdscr)
        # 读取用户输入得到action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        # 默认是当前状态，没有行为就会一直在当前界面循环
        responses = defaultdict(lambda: state)
        # 对应不同的行为转换到不同的状态
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'  
        return responses[action]

    # 游戏中
    def game():
        # 画出当前棋盘状态
        game_field.draw(stdscr)
        # 读取用户输入得到action
        action = get_user_action(stdscr)
        # 重启游戏
        if action == 'Restart':
            return 'Init'
        # 退出游戏
        if action == 'Exit':
            return 'Exit'
        # 移动棋子
        if game_field.move(action):
            # 无法在指定格子内继续移动
            if not game_field.can_move():
                # 如果所有格子已经填满，游戏结束
                if game_field.end():
                    return 'End'
                # 否则当前玩家获得一次任意选择的机会
                else:
                    game_field.arbitrary_opportunity()
        return 'Game'

    # 状态定义
    state_actions = {
        'Mode': mode,
        'Rules': rules,
        'Init': init,
        'End': lambda: not_game('End'),
        'Game': game
    }

    curses.use_default_colors()

    # 设置终结状态最大数值为 32
    game_field = GameField()
    # 初始状态
    state = 'Mode'
    # 状态机开始循环
    while state != 'Exit':
        try:
            state = state_actions[state]()
        except:
            state = 'Exit'
            print("当前窗口太小，无法显示所有内容，请确保运行游戏的窗口已经最大化！")

curses.wrapper(main)