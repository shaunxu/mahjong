# 麻将游戏

一个简单的控制台麻将游戏，包含一名玩家和三个电脑玩家。游戏会随机分配东南西北座位，并为每位玩家发放初始手牌。

## 功能特点

- 随机分配东南西北座位
- 自动发放初始手牌（每人13张）
- 控制台界面，无需图形界面
- 支持标准的麻将牌（万、筒、条、风、箭）

## 系统要求

- Python 3.12 或更高版本

## 安装方法

```bash
# 克隆仓库
git clone https://github.com/yourusername/mahjong.git
cd mahjong

# 安装依赖
pip install -e .
```

## 使用方法

```bash
# 直接运行游戏
python main.py
```

## 游戏规则

- 游戏开始时，系统会随机为玩家和三个电脑分配东南西北座位
- 每位玩家初始获得13张手牌
- 玩家可以看到自己的手牌，但看不到电脑的具体手牌

## 项目结构

```
mahjong/
├── game.py         # 游戏核心逻辑
├── main.py         # 游戏启动脚本
├── README.md
└── pyproject.toml
```

## 许可证

[MIT](LICENSE)