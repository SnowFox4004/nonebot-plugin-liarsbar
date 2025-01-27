import asyncio

import nonebot_plugin_alconna.uniseg as uniseg
from arclet.alconna import MultiVar
from nonebot import get_plugin_config, logger
from nonebot.adapters import Bot, Event, Message
from nonebot_plugin_alconna import Alconna, Args, Match, on_alconna
from nonebot_plugin_alconna.uniseg import MsgTarget
from nonebot_plugin_uninfo import Uninfo

from ..config import Config
from . import definitions as defs

ROOMS: dict[str, defs.Room] = {}
PLAYERS: dict[str, defs.Player] = {}
CONFIG = get_plugin_config(Config)

create_room = on_alconna(
    Alconna(
        "createroom",
        Args["name", str | None],
    ),
    # rule=to_me,
    aliases={"创建房间", "开房间"},
    use_cmd_start=True,
    priority=10,
)

start_game = on_alconna(
    Alconna("startgame"),
    # rule=to_me,
    aliases={"开始游戏", "开始"},
    use_cmd_start=True,
    priority=10,
)

attend_room = on_alconna(
    Alconna(
        "attend",
        Args["room", str],
    ),
    # rule=to_me,
    aliases={"加入房间", "加入"},
    use_cmd_start=True,
    priority=10,
)

fp_cmd = on_alconna(
    Alconna("fp", Args["cards", MultiVar(int)]),
    # rule=to_me,
    aliases={"出牌"},
    use_cmd_start=True,
    priority=10,
)

zy_cmd = on_alconna(
    Alconna("zy"),
    # rule=to_me,
    aliases={"质疑"},
    use_cmd_start=True,
    priority=10,
)

help_cmd = on_alconna(
    Alconna("help", Args["target", str, "rule"]),
    # rule=to_me,
    aliases={"帮助"},
    use_cmd_start=True,
    priority=10,
)

quit_room = on_alconna(
    Alconna("quitroom"),
    # rule=to_me,
    aliases={"退出房间", "退出"},
    use_cmd_start=True,
    priority=10,
)

force_stop = on_alconna(
    Alconna("stopgame"), aliases={"停止游戏"}, use_cmd_start=True, priority=10
)

# test = on_alconna(
#     Alconna("test"),
#     # rule=to_me,
#     aliases={"test"},
#     use_cmd_start=True,
#     priority=10,
# )


# @test.handle()
# async def test_handler(event: Event, session: Uninfo, bot: Bot):
#     msg = uniseg.UniMessage("s")
#     # msg = Message("test")

#     mid = await msg.send(uniseg.Target("2956033883", private=True), bot)
#     logger.info(f"消息id {mid.msg_ids}")
#     await asyncio.sleep(1)
#     if mid.msg_ids is not None:
#         await bot.delete_msg(message_id=mid.msg_ids[0]["message_id"])


async def friend_test(room: defs.Room, bot: Bot):
    for player in room.players:
        try:
            msg = uniseg.UniMessage("机器人好友测试")
            mid = await msg.send(uniseg.Target(player.uid, private=True), bot)
            await asyncio.sleep(0.1)
            if mid.msg_ids is not None:
                await bot.delete_msg(message_id=mid.msg_ids[0]["message_id"])
        except:
            return False
    return True


async def load_user(uid: str, name: str | None = None) -> defs.Player:
    if uid in PLAYERS:
        return PLAYERS[uid]
    else:
        PLAYERS[uid] = defs.Player(uid, name)
        return PLAYERS[uid]


def docs(target: str = "rule"):
    rule_explanation = """
Liar's Bar:
- 游戏牌面组成：6张A、6张K、6张Q、2张王（王为特殊牌，可代替其他牌）。

- 开局设定：系统规定此轮应出牌的类型（如：Ace【A】）每次开局会随机掀起一张牌作为“目标牌”，每位玩家手中持有五张牌。

- 出牌规则：每轮玩家可以随意出任意多张牌，下家有权选择继续出牌或打开上家刚出的牌。

- 判断规则：如果上家出的牌不是全部都对应开局掀起的“目标牌”，则被开的玩家需要用“左轮手枪”朝自己“开一枪”；反之下家则需要用“左轮手枪”开自己一枪。

- 特殊牌：Joker牌可以替代任意牌，为游戏增添更多变数。

- 获胜条件：存活到最后的玩家胜利
    """

    command_help = """
创建房间：/createroom <ROOM-NAME>
加入房间：/attend <ROOM-NAME> (仅房主)
开始游戏：/startgame
出牌：/fp <CARD-Index> [CARD-Index...]
质疑：/zy
    """

    return rule_explanation if target == "rule" else command_help


@force_stop.handle()
async def force_stop_handler(bot: Bot, event: Event, session: Uninfo):
    uid = session.user.id
    player = await load_user(uid)

    if session.group is None:
        await force_stop.finish("❌: 请于群聊中使用此命令")
        return

    if player.in_room is None or player.in_game == False:
        await force_stop.finish("❌: 你没有在开始游戏的房间中")
    elif player.in_room is not None and player.in_room.owener != player:
        await force_stop.finish("❌: 你不是房主，无法强制停止游戏")

    room: defs.Room = player.in_room
    if room.gaming == False or room.game is None:
        await force_stop.finish("❌: 游戏尚未开始，无法强制停止游戏")
    else:
        room.game.cancel()
        await force_stop.finish("✔: 游戏已强制停止")


@quit_room.handle()
async def quit_room_handler(bot: Bot, event: Event, session: Uninfo):
    uid = session.user.id
    target_user = await load_user(uid)

    if target_user.in_game:
        await quit_room.finish("❌: 你正在游戏中，无法退出房间")

    if target_user.in_room is None:
        await quit_room.finish("❌: 你没有加入任何房间")

    if target_user.in_room is not None:
        res = target_user.in_room.on_remove_player(target_user)

        resp_msg = uniseg.UniMessage(
            f"退出房间 {target_user.in_room.room_name} 成功 "
        ).at(event.get_user_id())

        if res.status == defs.CallResultStatus.WARNING:
            resp_msg.text(f"\n⚠️: {res.msg}")
            ROOMS.pop(target_user.in_room.room_name)

        elif res.status == defs.CallResultStatus.SUCCESS:
            resp_msg.text(f"\n✔: {res.msg}")

        target_user.in_room = None
        await quit_room.finish(resp_msg)


@help_cmd.handle()
async def help_cmd_handler(target: Match[str]):
    await help_cmd.finish(docs(target.result))


@zy_cmd.handle()
async def zy_cmd_handler(bot: Bot, event: Event, session: Uninfo):
    uid = session.user.id
    # target_user = await load_user(uid)
    # logger.info(f"{msg}")
    if session.group is None:
        await zy_cmd.finish("Error: 请于群聊中使用此命令")
        return

    defs.input_store.input_store[f"{session.group.id}_{uid}"].set(
        event.get_message().extract_plain_text()
    )
    await zy_cmd.finish()


@fp_cmd.handle()
async def fp_cmd_handler(cards: Match[list], event: Event, session: Uninfo):
    uid = session.user.id
    send_card_indexes = cards.result
    # target_user = await load_user(uid)
    # logger.info(f"{msg}")
    if len(send_card_indexes) > 3:
        await fp_cmd.finish("❌: 一次最多出三张牌，请重新选择")
        return

    if session.group is None:
        await fp_cmd.finish("Error: 请于群聊中使用此命令")
        return

    defs.input_store.input_store[f"{session.group.id}_{uid}"].set(
        "/fp", indexs=send_card_indexes
    )
    await fp_cmd.finish()


@attend_room.handle()
async def attend_room_handler(
    room: Match[str], bot: Bot, event: Event, session: Uninfo
):
    uid = session.user.id
    target_user = await load_user(uid, session.user.name)

    if target_user.in_room is not None:
        await attend_room.finish(
            f"❌: 你已经在房间 {target_user.in_room.room_name} 中，不能再加入房间"
        )

    targer_room: defs.Room = ROOMS[room.result]
    targer_room.on_add_player(target_user)

    target_user.in_room = targer_room

    await attend_room.send(
        uniseg.UniMessage(f"加入房间 {targer_room.room_name} 成功")
        .at(event.get_user_id())
        .text(" (开始游戏命令: /startgame)")
    )


@create_room.handle()
async def create_room_handler(
    name: Match[str | None],
    bot: Bot,
    event: Event,
    target: MsgTarget,
    session: Uninfo,
):

    sender = event.get_user_id()
    # if sender not in PLAYERS:
    #     PLAYERS[sender] = defs.Player(sender, session.user.nick)

    logger.info(f"{session.user.name} 正在创建房间")
    # target = session.group
    # logger.debug(f"room is in {target}")
    try:
        room = defs.Room(
            await load_user(sender, session.user.name),
            session.group.id,  # type: ignore
            target,
            name.result if name.available else None,
        )
    except defs.LiarException as err:
        await create_room.finish(uniseg.UniMessage(f"创建房间失败: {err.msg}"))
    except AttributeError:
        await create_room.finish("Error: 请于群聊中使用此命令")

    if room.room_name in ROOMS:
        await create_room.finish(
            uniseg.UniMessage(f"房间 {room.room_name} 已存在, 请更改房间名")
        )

    ROOMS[room.room_name] = room
    await create_room.finish(
        uniseg.UniMessage(
            f"创建房间 {room.room_name} 成功，快邀请好友加入房间吧\n‼请注意开始游戏前要加机器人的好友，否则无法正常游戏\n"
        )
        .at(event.get_user_id())
        .text(" (加入房间命令: /attend <ROOM-NAME>)")
    )


@start_game.handle()
async def start_game_handler(bot: Bot, event: Event, session: Uninfo):
    sender = event.get_user_id()
    sender_player = await load_user(sender)
    target_room = sender_player.in_room
    if target_room is None:
        await start_game.finish("您不在任何房间中，无法开始游戏")

    friend_test_success = await friend_test(target_room, bot)
    if not friend_test_success:
        await start_game.finish(
            "❌: 玩家未通过好友验证(有玩家非bot好友，请先添加)，无法开始游戏"
        )

    target_room.attendable = False
    target_room.gaming = True

    notify_msg = uniseg.UniMessage()
    for player in target_room.players:
        notify_msg.at(player.uid)
    notify_msg.text("\n🐱‍🏍游戏即将开始，请做好准备")
    await start_game.send(notify_msg)
    await asyncio.sleep(1)

    game = defs.Game(target_room, bot)
    game_task = asyncio.create_task(game.start(CONFIG.liars_num_bullet))

    target_room.game = game_task
    await game_task

    target_room.attendable = True
    target_room.gaming = False
    del game
    await start_game.finish(
        f"🎉 游戏已结束, 可重新开始，房间内玩家: {[player.name or player.uid for player in target_room.players]}"
    )
