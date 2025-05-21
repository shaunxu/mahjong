import pygame
import sys
import random
import argparse
import platform
from pygame.font import get_fonts

# 定义麻将牌
SUITS = ['万', '条', '筒']
RANKS = list(range(1, 10))
HONORS = ['东', '南', '西', '北', '中', '发', '白']
ALL_TILES = [f"{r}{s}" for s in SUITS for r in RANKS for _ in range(4)] + [h for h in HONORS for _ in range(4)]

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
GRAY = (200, 200, 200)
BLUE = (0, 120, 255)

# 屏幕尺寸
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
TILE_WIDTH = 50  # 增加牌的宽度
TILE_HEIGHT = 70  # 增加牌的高度
TILE_GAP = 10  # 增加牌之间的间隔

def get_available_chinese_font():
    # 常见的中文字体名称
    chinese_fonts = [
        'PingFang SC', 'Microsoft YaHei', 'SimHei', 'WenQuanYi Micro Hei',
        'Noto Sans CJK SC', 'Noto Sans CJK TC', 'Hiragino Sans GB',
        'STHeiti', 'STSong', 'STFangsong', 'Arial Unicode MS'
    ]
    available_fonts = pygame.font.get_fonts()
    
    # 首先尝试系统特定的默认字体
    system_default = None
    if platform.system() == 'Darwin':  # macOS
        system_default = 'pingfang sc'
    elif platform.system() == 'Windows':
        system_default = 'microsoft yahei'
    elif platform.system() == 'Linux':
        system_default = 'wenquanyi micro hei'
    
    if system_default and system_default in available_fonts:
        return system_default
        
    # 然后尝试其他中文字体
    for font in chinese_fonts:
        font_lower = font.lower().replace(' ', '')
        if font_lower in available_fonts:
            return font_lower
            
    # 如果找不到中文字体，返回系统默认字体
    return None

pygame.init()
# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--font', type=str, default=None, help='指定中文字体名称')
args, _ = parser.parse_known_args()

if args.font:
    font_name = args.font
else:
    font_name = get_available_chinese_font()

try:
    if font_name:
        FONT = pygame.font.SysFont(font_name, 24)
        SMALL_FONT = pygame.font.SysFont(font_name, 18)
    else:
        # 如果没有找到合适的字体，尝试加载系统默认字体
        font_path = pygame.font.get_default_font()
        FONT = pygame.font.Font(font_path, 24)
        SMALL_FONT = pygame.font.Font(font_path, 18)
except Exception as e:
    print(f"加载字体失败: {e}")
    print("尝试使用系统默认字体")
    font_path = pygame.font.get_default_font()
    FONT = pygame.font.Font(font_path, 24)
    SMALL_FONT = pygame.font.Font(font_path, 18)

class MahjongGamePygame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('麻将游戏')
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.tiles = ALL_TILES.copy()
        random.shuffle(self.tiles)
        self.hands = [[] for _ in range(4)]
        self.discards = [[] for _ in range(4)]
        self.selected_tile = None
        self.deal_tiles()
        self.running = True
        self.info_msg = ''
        # 初始化吃牌相关的状态
        self.chi_mode = False
        self.chi_selected = []  # 存储用户选择的要吃牌的两张手牌
        self.chi_groups = []  # 存储已经吃的牌组

    def deal_tiles(self):
        for _ in range(13):
            for i in range(4):
                self.hands[i].append(self.tiles.pop())
        self.hands[0].append(self.tiles.pop())

    def draw(self):
        self.screen.fill(GREEN)
        # 用户手牌
        hand = sorted(self.hands[0])
        for idx, tile in enumerate(hand):
            x = 60 + idx * (TILE_WIDTH + TILE_GAP)
            y = SCREEN_HEIGHT - TILE_HEIGHT - 40
            rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
            color = BLUE if (self.selected_tile == idx or 
                           (self.chi_mode and tile in self.chi_selected)) else WHITE
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            text = FONT.render(tile, True, BLACK)
            text_rect = text.get_rect(center=(x + TILE_WIDTH/2, y + TILE_HEIGHT/2))
            self.screen.blit(text, text_rect)
            
        # 显示吃的组合
        start_x = SCREEN_WIDTH - 250
        start_y = SCREEN_HEIGHT - TILE_HEIGHT - 40
        for group_idx, chi_group in enumerate(self.chi_groups):
            for tile_idx, tile in enumerate(chi_group):
                x = start_x + tile_idx * (TILE_WIDTH + 5)
                y = start_y - group_idx * (TILE_HEIGHT + 5)
                rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                text = FONT.render(tile, True, BLACK)
                text_rect = text.get_rect(center=(x + TILE_WIDTH/2, y + TILE_HEIGHT/2))
                self.screen.blit(text, text_rect)

        # 操作按钮
        btns = ['摸牌', '出牌', '吃', '碰', '杠', '胡', '重开']
        self.btn_rects = []
        for i, label in enumerate(btns):
            bx = 60 + i * 90
            by = SCREEN_HEIGHT - 220
            rect = pygame.Rect(bx, by, 80, 30)
            # 设置按钮颜色
            if label == '出牌' and self.selected_tile is not None and len(self.hands[0]) > 13:
                btn_color = (150, 255, 150)  # 浅绿色表示可以出牌
            elif label == '摸牌' and self.tiles and len(self.hands[0]) <= 13:
                btn_color = (150, 255, 150)  # 浅绿色表示可以摸牌
            elif label == '吃' and self.can_chi():
                btn_color = (150, 255, 150)  # 浅绿色表示可以吃牌
            elif label == '吃' and self.chi_mode:
                btn_color = (255, 255, 150)  # 黄色表示正在吃牌模式
            else:
                btn_color = GRAY
            pygame.draw.rect(self.screen, btn_color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            t = SMALL_FONT.render(label, True, BLACK)
            self.screen.blit(t, (bx+20, by+5))
            self.btn_rects.append((rect, label))

        # 用户弃牌
        self.screen.blit(SMALL_FONT.render('你的弃牌:', True, BLACK), (60, SCREEN_HEIGHT-180))
        for idx, tile in enumerate(self.discards[0]):
            x = 140 + idx * (TILE_WIDTH + 2)
            y = SCREEN_HEIGHT-180
            rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
            pygame.draw.rect(self.screen, WHITE, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            text = SMALL_FONT.render(tile, True, BLACK)
            text_rect = text.get_rect(center=(x + TILE_WIDTH/2, y + TILE_HEIGHT/2))  # 居中显示文字
            self.screen.blit(text, text_rect)
        # 电脑家弃牌
        for i in range(1, 4):
            # 绘制电脑名字
            self.screen.blit(SMALL_FONT.render(f'电脑{i}:', True, BLACK), (60, 60 + i*60))
            # 绘制弃牌
            for idx, tile in enumerate(self.discards[i]):
                x = 120 + idx * (TILE_WIDTH//2 + 2)  # 从电脑名字后面开始显示弃牌
                y = 60 + i*60
                rect = pygame.Rect(x, y, TILE_WIDTH//2, TILE_HEIGHT//2)
                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                text = SMALL_FONT.render(tile, True, BLACK)
                text_rect = text.get_rect(center=(x + (TILE_WIDTH//2)/2, y + (TILE_HEIGHT//2)/2))  # 居中显示文字
                self.screen.blit(text, text_rect)
        # 信息提示
        if self.info_msg:
            info = SMALL_FONT.render(self.info_msg, True, (200,0,0))
            self.screen.blit(info, (60, 30))
        # 显示当前选中的牌
        if self.selected_tile is not None:
            hand = sorted(self.hands[0])
            selected_info = f"当前选中: {hand[self.selected_tile]}"
            selected_text = SMALL_FONT.render(selected_info, True, BLUE)
            self.screen.blit(selected_text, (60, 60))
        pygame.display.flip()

    def handle_mouse(self, pos):
        # 选择手牌
        hand = sorted(self.hands[0])
        for idx, tile in enumerate(hand):
            x = 60 + idx * (TILE_WIDTH + TILE_GAP)
            y = SCREEN_HEIGHT - TILE_HEIGHT - 40
            rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
            if rect.collidepoint(pos):
                if self.chi_mode:
                    # 在吃牌模式下，选择要吃的牌
                    if tile in self.chi_selected:
                        self.chi_selected.remove(tile)
                        self.info_msg = "取消选择了一张牌"
                    elif len(self.chi_selected) < 2:
                        self.chi_selected.append(tile)
                        self.info_msg = f"选择了{len(self.chi_selected)}张牌"
                        if len(self.chi_selected) == 2:
                            self.complete_chi()
                else:
                    self.selected_tile = idx
                return

        # 操作按钮
        for rect, label in self.btn_rects:
            if rect.collidepoint(pos):
                if label == '摸牌':
                    self.draw_tile()
                elif label == '出牌':
                    self.play_tile()
                elif label == '吃':
                    if not self.chi_mode:
                        if self.can_chi():
                            self.handle_chi()
                        else:
                            self.info_msg = "当前无法吃牌"
                    else:
                        self.chi_mode = False
                        self.chi_selected = []
                        self.info_msg = "取消吃牌"
                elif label == '碰':
                    self.info_msg = '暂未实现碰的判定逻辑'
                elif label == '杠':
                    self.info_msg = '暂未实现杠的判定逻辑'
                elif label == '胡':
                    self.info_msg = '暂未实现胡的判定逻辑'
                elif label == '重开':
                    self.reset_game()
                return

    def get_total_hand_count(self, player_index):
        """计算玩家的总手牌数量，包括手牌和吃碰的牌"""
        total = len(self.hands[player_index])
        if player_index == 0:  # 只计算玩家的吃碰牌
            # 每个吃或碰组合都是3张牌
            total += len(self.chi_groups) * 3
            # TODO: 在后续实现碰牌时，也要计算碰牌的数量
        return total

    def draw_tile(self):
        """摸牌操作"""
        total_cards = self.get_total_hand_count(0)
        if total_cards >= 14:
            self.info_msg = '你已经有14张牌了（包括吃碰的牌），不能再摸牌'
            return
        if self.tiles:
            self.hands[0].append(self.tiles.pop())
            self.info_msg = '你摸了一张牌，请选择要打出的牌'
        else:
            self.info_msg = '游戏结束，牌堆已空'

    def play_tile(self):
        """出牌操作"""
        if self.selected_tile is None:
            self.info_msg = '请先选择要打出的牌'
            return
            
        total_cards = self.get_total_hand_count(0)
        if total_cards <= 13:
            self.info_msg = '你现在只有13张牌（包括吃碰的牌），需要先摸牌'
            return
            
        hand = sorted(self.hands[0])
        tile = hand[self.selected_tile]
        
        # 从手牌中移除选中的牌
        for t in self.hands[0]:
            if t == tile:
                self.hands[0].remove(t)
                break
                
        # 添加到弃牌区
        self.discards[0].append(tile)
        self.selected_tile = None
        self.info_msg = f'你打出了 {tile}'
        
        # 轮到电脑玩家的回合
        self.next_turn()

    def next_turn(self):
        # 电脑家操作
        for i in range(1, 4):
            # 先摸牌
            if self.tiles:
                self.hands[i].append(self.tiles.pop())
                self.info_msg = f'电脑{i}摸了一张牌'
                self.computer_action(i)
            else:
                self.info_msg = '游戏结束，牌堆已空'
                return

        self.info_msg = '轮到你的回合'

    def computer_action(self, idx):
        if not self.hands[idx]:  # 如果没有手牌，返回
            return
            
        # 始终打出第一张手牌（简单AI策略）
        tile = self.hands[idx][0]
        self.hands[idx].remove(tile)
        self.discards[idx].append(tile)
        self.info_msg = f'电脑{idx}打出了 {tile}'

    def can_chi(self):
        """检查是否可以吃牌"""
        if not self.discards or not self.discards[1]:  # 如果没有电脑玩家的弃牌，不能吃
            return False
        last_discard = self.discards[1][-1]  # 获取电脑玩家最后打出的牌
        
        # 只有数字牌可以吃，字牌不能吃
        if any(h == last_discard for h in HONORS):
            return False
            
        # 解析最后一张弃牌的数字和花色
        try:
            rank = int(last_discard[0])
            suit = last_discard[1]
        except (ValueError, IndexError):
            return False
        
        # 获取玩家手牌中同花色的牌
        try:
            hand_tiles = sorted([t for t in self.hands[0] if len(t) > 1 and t[1] == suit])
            if not hand_tiles:
                return False
        except (ValueError, IndexError):
            return False
            
        # 检查是否有连续的牌可以吃
        hand_ranks = [int(t[0]) for t in hand_tiles]
        # 检查三种吃牌方式：
        # 1. X-1,X,X+1
        # 2. X-2,X-1,X
        # 3. X,X+1,X+2
        target_combinations = [
            [rank-1, rank+1],  # 中间吃
            [rank-2, rank-1],  # 后面吃
            [rank+1, rank+2]   # 前面吃
        ]
        
        for combo in target_combinations:
            if all(r in hand_ranks for r in combo):
                return True
        return False
        
    def get_chi_combinations(self):
        """获取所有可能的吃牌组合"""
        if not self.discards or not self.discards[1]:
            return []
            
        last_discard = self.discards[1][-1]
        try:
            rank = int(last_discard[0])
            suit = last_discard[1]
        except (ValueError, IndexError):
            return []
        
        try:
            hand_tiles = [t for t in self.hands[0] if len(t) > 1 and t[1] == suit]
            hand_ranks = [int(t[0]) for t in hand_tiles]
        except (ValueError, IndexError):
            return []
        
        combinations = []
        
        # 检查三种吃牌方式
        if rank-1 in hand_ranks and rank+1 in hand_ranks:  # 中间吃
            combinations.append([f"{rank-1}{suit}", f"{rank+1}{suit}"])
        if rank-2 in hand_ranks and rank-1 in hand_ranks:  # 后面吃
            combinations.append([f"{rank-2}{suit}", f"{rank-1}{suit}"])
        if rank+1 in hand_ranks and rank+2 in hand_ranks:  # 前面吃
            combinations.append([f"{rank+1}{suit}", f"{rank+2}{suit}"])
            
        return combinations

    def handle_chi(self):
        """处理吃牌操作"""
        if not self.can_chi():
            self.info_msg = "现在不能吃牌"
            return
            
        # 获取所有可能的吃牌组合
        combinations = self.get_chi_combinations()
        if not combinations:
            self.info_msg = "没有可以吃的组合"
            return
            
        if not self.chi_mode:
            self.chi_mode = True
            self.chi_selected = []
            self.info_msg = "请选择要用来吃牌的两张牌"
        else:
            self.chi_mode = False
            self.chi_selected = []
            self.info_msg = "取消吃牌"
            
    def complete_chi(self):
        """完成吃牌操作"""
        if len(self.chi_selected) != 2:
            return
            
        if not self.discards or not self.discards[1]:
            self.info_msg = "没有可以吃的牌"
            self.chi_mode = False
            self.chi_selected = []
            return
            
        last_discard = self.discards[1][-1]
        chi_tiles = self.chi_selected + [last_discard]
        
        # 对牌组进行排序（按数字排序）
        chi_tiles.sort(key=lambda x: int(x[0]))
        
        # 验证是否是有效的吃牌组合
        ranks = [int(t[0]) for t in chi_tiles]
        suits = [t[1] for t in chi_tiles]
        
        if not (all(s == suits[0] for s in suits) and  # 检查花色相同
                max(ranks) - min(ranks) == 2 and       # 检查是否连续
                len(set(ranks)) == 3):                 # 检查是否有重复
            self.info_msg = "选择的牌不符合吃牌规则"
            self.chi_mode = False
            self.chi_selected = []
            return
            
        # 从手牌中移除选择的牌
        for tile in self.chi_selected:
            self.hands[0].remove(tile)
            
        # 从弃牌堆中移除被吃的牌
        self.discards[1].pop()
        
        # 添加到吃牌组合中
        self.chi_groups.append(chi_tiles)
        
        self.chi_mode = False
        self.chi_selected = []
        self.info_msg = f"吃牌成功：{''.join(chi_tiles)}"

    def run(self):
        """游戏主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse(event.pos)
            self.draw()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()
