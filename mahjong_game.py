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
            color = BLUE if self.selected_tile == idx else WHITE
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            text = FONT.render(tile, True, BLACK)
            text_rect = text.get_rect(center=(x + TILE_WIDTH/2, y + TILE_HEIGHT/2))  # 居中显示文字
            self.screen.blit(text, text_rect)
        # 操作按钮
        btns = ['出牌', '吃', '碰', '杠', '胡', '重开']
        self.btn_rects = []
        for i, label in enumerate(btns):
            bx = 60 + i * 90
            by = SCREEN_HEIGHT - 220  # 将按钮移到更高的位置，在弃牌区和手牌区之间
            rect = pygame.Rect(bx, by, 80, 30)
            pygame.draw.rect(self.screen, GRAY, rect)
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
        # 电脑家手牌和弃牌
        for i in range(1, 4):
            self.screen.blit(SMALL_FONT.render(f'电脑{i}手牌: {len(self.hands[i])} 张', True, BLACK), (700, 60 + i*60))
            for idx, tile in enumerate(self.discards[i]):
                x = 800 + idx * (TILE_WIDTH//2 + 2)  # 增加间隔
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
        pygame.display.flip()

    def handle_mouse(self, pos):
        # 选择手牌
        hand = sorted(self.hands[0])
        for idx, tile in enumerate(hand):
            x = 60 + idx * (TILE_WIDTH + TILE_GAP)
            y = SCREEN_HEIGHT - TILE_HEIGHT - 40
            rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
            if rect.collidepoint(pos):
                self.selected_tile = idx
                return
        # 操作按钮
        for rect, label in self.btn_rects:
            if rect.collidepoint(pos):
                if label == '出牌':
                    self.play_tile()
                elif label == '吃':
                    self.info_msg = '暂未实现吃的判定逻辑'
                elif label == '碰':
                    self.info_msg = '暂未实现碰的判定逻辑'
                elif label == '杠':
                    self.info_msg = '暂未实现杠的判定逻辑'
                elif label == '胡':
                    self.info_msg = '暂未实现胡的判定逻辑'
                elif label == '重开':
                    self.reset_game()
                return

    def play_tile(self):
        if self.selected_tile is None:
            self.info_msg = '请选择要出的牌'
            return
        hand = sorted(self.hands[0])
        tile = hand[self.selected_tile]
        self.hands[0].remove(tile)
        self.discards[0].append(tile)
        self.selected_tile = None
        self.info_msg = ''
        self.next_turn()

    def next_turn(self):
        # 电脑家操作（空实现）
        for i in range(1, 4):
            self.computer_action(i)
        # 用户摸牌
        if self.tiles:
            self.hands[0].append(self.tiles.pop())

    def computer_action(self, idx):
        pass

    def run(self):
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
