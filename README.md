# Minecraft 红石音乐生成器

这是一个用于在 Minecraft 中自动生成红石音乐系统的 Python 工具，可以将 MIDI 文件转换为命令方块电路。

## 功能特性

- 支持将 MIDI 文件转换为 Minecraft 命令方块音乐
- 自动生成红石基础电路和脉冲系统
- 支持长音乐的折叠功能，避免生成过长的直线结构
- 提供测试模式，可只生成前几秒的音乐进行预览
- 实时进度显示和区块加载

## 依赖安装

```bash
pip install mcrcon pretty_midi
```

## 使用方法

1. 确保 Minecraft 服务器已启用 RCON（需要在 server.properties 中设置）
2. 修改脚本中的配置参数：
   - 起始坐标
   - RCON 连接信息
   - MIDI 文件路径
   - 玩家名称
3. 运行脚本：
   ```bash
   python redstone_music_builder.py
   ```
4. 按照提示选择是否启用测试模式

## 注意事项

- 脚本会自动生成大量命令方块，可能会对服务器性能产生影响
- 建议在空旷区域使用，避免与现有建筑冲突
- MIDI 文件应使用钢琴音轨（程序号 0-7）以获得最佳效果
- 生成的音乐系统区域较大，请确保有足够的空间

## 配置参数说明

- `start_x`, `start_y`, `start_z`: 音乐系统的起始坐标（沿x增长！）
- `rcon_ip`, `rcon_port`, `rcon_password`: Minecraft 服务器 RCON 连接信息
- `midi_file_path`: MIDI 文件的路径
- `player_name`: 用于加载区块的玩家名称
- `base_gen_speed`: 基座生成速度
- `fold_length`: 每段长度（超过后会自动折叠,不建议改，可能引发bug(折叠的逻辑我写的跟屎一样)，下面增加的高度同理）
- `fold_height_increase`: 每次折叠增加的高度

## 生成区域

生成的区域范围会在运行时显示，大致为：
```
从 start_x start_y start_z 到 start_x + max_tick start_y - 4 start_z + 10
```

其中 max_tick 取决于 MIDI 文件的时长。

## 运行思路

程序的核心运行流程如下：

1. **MIDI文件解析**：使用pretty_midi库加载MIDI文件，提取钢琴音轨（程序号0-7）的音符信息
2. **音符分组**：将音符按时间（0.05秒精度）分组，形成时间槽（time_slots）
3. **基础电路生成**：
   - 生成红石计时电路，每个时间单位对应一个红石中继器
   - 实现折叠机制，当电路长度超过fold_length时，自动向上折叠并继续生成
   - 在每个折叠处创建连接结构，确保信号连续传递
4. **命令方块生成**：
   - 为每个时间槽中的音符生成对应的命令方块
   - 命令方块使用summon指令生成下落的红石方块到指定位置
   - 通过计算不同的target_z值来触发不同音高的命令方块
