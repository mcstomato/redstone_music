from mcrcon import MCRcon
import pretty_midi
import time

# 关键：钢琴沿着z轴铺设 起始最低音21的方块坐标31 -49 -41, 沿着z正方向增长
def test(mcr,pitch,x,y,z):
    target_z = -40.50 - 21 + pitch
    mcr.command(f'setblock {x} {y} {z} minecraft:command_block[conditional=false,facing=up]{{Command:"summon minecraft:falling_block 31.50 0 {target_z} {{BlockState:{{Name:\\"minecraft:redstone_block\\"}},Time:1}}"}}')

# 输入坐标
start_x = -100
start_y = -46
start_z = 80

# 输入rcon密码和IP
rcon_ip = '127.0.0.1'
rcon_port = 25575
rcon_password = '123456'

# 输入MIDI文件路径
midi_file_path = 'QBY.mid'

# 输入玩家名称
player_name = 'MC_Stomato'

# 基座生成速度
base_gen_speed = 1


def time_to_ticks(seconds):
    """将秒数转换为红石刻数（1刻=0.05秒）"""
    rounded_seconds = round(seconds, 2)
    return max(1, int(rounded_seconds * 20))


if __name__ == '__main__':
    # 加载MIDI文件
    print("加载MIDI文件...")
    midi_data = pretty_midi.PrettyMIDI(midi_file_path)

    # === 添加测试模式 ===
    test_mode = input("是否启用测试模式？(y/n): ").lower().strip()
    if test_mode == 'y':
        max_test_time = float(input("测试时长(秒): "))
        print(f"测试模式：只生成前{max_test_time}秒的音乐")
    else:
        max_test_time = None
    # === 测试模式结束 ===

    # 收集所有音符
    all_notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            # 只处理钢琴音轨（程序号0-7通常是钢琴类）
            if instrument.program in range(0, 8):
                # === 添加时间过滤 ===
                if max_test_time is not None and note.start > max_test_time:
                    continue
                # === 时间过滤结束 ===
                all_notes.append(note)

    if not all_notes:
        print("未找到钢琴音轨！")
        exit()

    # 按开始时间排序并分组
    all_notes.sort(key=lambda x: x.start)

    # 将音符按时间分组（0.05秒精度）
    time_slots = {}
    for note in all_notes:
        time_key = round(note.start, 2)  # 四舍五入到0.05秒

        if time_key == 0 and note.start > 0:
            time_key = 0.05

        if time_key not in time_slots:
            time_slots[time_key] = []
        time_slots[time_key].append(note)

    # 计算最大时间
    max_time = max(time_slots.keys()) if time_slots else 0
    max_tick = int(max_time * 20)  # 转换为0.05秒单位的tick

    print("==========================注意事项==========================")
    print("生成脉冲命令方块音乐系统")
    print("每个红石中继器延迟为1刻(0.05秒)")
    print(f"预计生成的区域范围为")
    print(f"从 {start_x} {start_y} {start_z} 到 {start_x + max_tick} {start_y - 4} {start_z + 10}")
    print("===========================================================")

    # 使用RCON连接服务器
    with MCRcon(rcon_ip, rcon_password, port=rcon_port) as mcr:
        mcr.command('say Rcon连接成功！')
        mcr.command('say ===============自动生成命令方块音乐===============')
        mcr.command('say 版本：2.0 - 脉冲命令方块版')
        mcr.command(f'say 总时长：{max_time:.1f}秒')
        mcr.command(f'say 音符数量：{len(all_notes)}')
        mcr.command(f'say 时间槽数量：{len(time_slots)}')

        print("\n程序将在3秒后开始生成")
        mcr.command(f'say 程序将在3秒后开始生成')
        time.sleep(3)

        # 第一步：生成基础红石电路
        print("生成基础红石电路...")
        speed_count = 0
        last_time = 0

        mcr.command(
            f"fill {start_x-1} {start_y - 4} {start_z} {start_x-1} {start_y - 4} {start_z + 10} minecraft:stone")
        mcr.command(
            f"fill {start_x-1} {start_y - 3} {start_z} {start_x-1} {start_y - 3} {start_z + 10} minecraft:redstone_wire")
        mcr.command(
            f"setblock {start_x-2} {start_y - 2} {start_z} minecraft:observer[facing=down]"
        )
        mcr.command(
            f"setblock {start_x-2} {start_y - 4} {start_z} minecraft:stone"
        )
        mcr.command(
            f'setblock {start_x-2} {start_y - 1} {start_z} minecraft:command_block[conditional=false,facing=up]{{Command:"tp @p 0 -20 0 -90 30"}}'
        )

        # 添加折叠相关参数
        fold_length = 200  # 每200格折叠一次
        fold_height_increase = 5  # 每次折叠增加的高度

        for tick in range(0, max_tick + 1):
            # 计算折叠后的实际坐标
            fold_index = tick // fold_length
            tick_in_fold = tick % fold_length

            # 判断是正向还是反向
            if fold_index % 2 == 0:  # 偶数次折叠：正向
                actual_x = start_x + tick_in_fold
            else:  # 奇数次折叠：反向
                actual_x = start_x + (fold_length - 1 - tick_in_fold)

            actual_y = start_y + fold_index * fold_height_increase

            # 在每次折叠开始时创建折叠结构（除了第0次）
            if tick_in_fold == 0 and fold_index > 0:
                print(f"创建第{fold_index}次折叠结构...")
                # 上一段的最后一个X坐标
                if (fold_index - 1) % 2 == 0:  # 上一段是正向
                    prev_end_x = start_x + fold_length - 1
                    prev_facing = 'west'
                else:  # 上一段是反向
                    prev_end_x = start_x
                    prev_facing = 'east'

                # 当前段的方向
                current_facing = 'east' if fold_index % 2 == 1 else 'west'

                # 为每个轨道创建折叠结构 (z坐标从0到10)
                for z_offset in range(0, 11):
                    z = start_z + z_offset
                    prev_y = start_y + (fold_index - 1) * fold_height_increase

                    # 计算正确的起始高度（与中继器对齐）
                    start_height = prev_y - 4  # 与中继器同一层

                    if prev_facing == 'west':  # 从右向左的折叠
                        positions = [
                            # (玻璃坐标), (红石坐标)
                            ((prev_end_x + 1, start_height, z), (prev_end_x + 1, start_height + 1, z)),
                            ((prev_end_x + 2, start_height, z), (prev_end_x + 2, start_height + 1, z)),
                            ((prev_end_x + 3, start_height + 1, z), (prev_end_x + 3, start_height + 2, z)),
                            ((prev_end_x + 2, start_height + 2, z), (prev_end_x + 2, start_height + 3, z)),
                            ((prev_end_x + 3, start_height + 3, z), (prev_end_x + 3, start_height + 4, z)),
                            ((prev_end_x + 2, start_height + 4, z), (prev_end_x + 2, start_height + 5, z)),
                            ((prev_end_x + 1, start_height + 5, z), (prev_end_x + 1, start_height + 6, z))
                        ]
                    else:  # 从左向右的折叠（反向）
                        positions = [
                            # (玻璃坐标), (红石坐标)
                            ((prev_end_x - 1, start_height, z), (prev_end_x - 1, start_height + 1, z)),
                            ((prev_end_x - 2, start_height, z), (prev_end_x - 2, start_height + 1, z)),
                            ((prev_end_x - 3, start_height + 1, z), (prev_end_x - 3, start_height + 2, z)),
                            ((prev_end_x - 2, start_height + 2, z), (prev_end_x - 2, start_height + 3, z)),
                            ((prev_end_x - 3, start_height + 3, z), (prev_end_x - 3, start_height + 4, z)),
                            ((prev_end_x - 2, start_height + 4, z), (prev_end_x - 2, start_height + 5, z)),
                            ((prev_end_x - 1, start_height + 5, z), (prev_end_x - 1, start_height + 6, z))
                        ]

                    for glass_pos, redstone_pos in positions:
                        glass_x, glass_y, glass_z = glass_pos
                        redstone_x, redstone_y, redstone_z = redstone_pos
                        mcr.command(f"setblock {glass_x} {glass_y} {glass_z} minecraft:glass replace")
                        mcr.command(f"setblock {redstone_x} {redstone_y} {redstone_z} minecraft:redstone_wire")

                    # 在折叠终点连接到新段的起点
                    mcr.command(f"setblock {actual_x} {actual_y - 2} {z} minecraft:observer[facing=down] replace")
                    mcr.command(
                        f"setblock {actual_x} {actual_y - 3} {z} minecraft:repeater[facing={current_facing},delay=1] replace")

            if time.time() > last_time:
                progress = (tick / max_tick) * 100 if max_tick > 0 else 0
                direction = "正向" if fold_index % 2 == 0 else "反向"
                print(f"生成基座进度：{progress:.1f}% - 第{fold_index}段({direction})")
                last_time = time.time() + 1

            # 生成当前tick的基础电路（使用实际坐标）
            facing = 'east' if fold_index % 2 == 1 else 'west'
            mcr.command(
                f"fill {actual_x} {actual_y - 2} {start_z} {actual_x} {actual_y - 2} {start_z + 10} minecraft:observer[facing=down] replace")
            mcr.command(
                f"fill {actual_x} {actual_y - 4} {start_z} {actual_x} {actual_y - 4} {start_z + 10} minecraft:stone_bricks replace")
            mcr.command(
                f"fill {actual_x} {actual_y - 3} {start_z} {actual_x} {actual_y - 3} {start_z + 10} minecraft:repeater[facing={facing},delay=1] replace")

            # 传送玩家以加载区块
            mcr.command(f"tp {player_name} {actual_x} {actual_y + 10} {start_z}")

        # 修改命令方块生成部分：
        print("生成命令方块...")
        total_commands = len(all_notes)
        current_command = 0

        for time_key, notes in time_slots.items():
            tick = int(time_key * 20)

            # 计算折叠后的实际坐标（与上面相同的逻辑）
            fold_index = tick // fold_length
            tick_in_fold = tick % fold_length

            if fold_index % 2 == 0:  # 正向
                actual_x = start_x + tick_in_fold
            else:  # 反向
                actual_x = start_x + (fold_length - 1 - tick_in_fold)

            actual_y = start_y + fold_index * fold_height_increase

            for i, note in enumerate(notes):
                z = start_z + i % 11  # 0-10共11个轨道
                y = actual_y - 1  # 命令方块放在实际高度的-1层

                # 使用您提供的test函数放置命令方块
                test(mcr, note.pitch, actual_x, y, z)

                current_command += 1
                if current_command % 50 == 0:
                    progress = (current_command / total_commands) * 100
                    print(f"生成命令方块进度：{progress:.1f}%")

                # 传送玩家以加载区块
                mcr.command(f"tp {player_name} {actual_x} {actual_y + 10} {z}")

        # 第三步：激活系统
        print("激活音乐系统...")
        mcr.command('say 音乐系统生成完毕！已激活！')

    print("生成完毕，已断开Rcon连接")
