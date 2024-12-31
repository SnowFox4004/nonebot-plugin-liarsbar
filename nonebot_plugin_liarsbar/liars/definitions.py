import asyncio
import random as rnd
from collections import defaultdict
from enum import Enum
from hashlib import md5

import anyio
from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna.uniseg import Target, UniMessage


def get_random_roomname():
    return "".join(
        [rnd.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(4)]
    )


class LiarException(BaseException):
    def __init__(self, msg: str | None, *args):
        super().__init__(*args)
        self.msg = msg


class UserInputEvent:
    _event: anyio.Event
    _msg: str
    _info_dict: dict

    def __init__(self) -> None:
        self._event = anyio.Event()

    def set(self, msg: str, **kwargs) -> None:
        self._msg = msg
        self._info_dict = kwargs

        self._event.set()

    async def wait(self):
        await self._event.wait()
        return self._msg, self._info_dict

    def is_set(self):
        return self._event.is_set()


class _InputStore:
    def __init__(self):
        self.input_store = defaultdict(UserInputEvent)

    async def wait_input(self, gid, uid):
        key = gid + "_" + uid
        # logger.info(f"start waiting for {key}")

        if self.input_store[key].is_set():
            del self.input_store[key]

        return await self.input_store[key].wait()  # type: ignore


input_store = _InputStore()


class CallResultStatus(int, Enum):
    SUCCESS = 0
    ERROR = 1
    WARNING = 2


class CallResult:
    def __init__(self, status: CallResultStatus, msg: str):
        self.status = status
        self.msg = msg

    def __str__(self):
        return f"{self.status.name}: {self.msg}"


class Player:
    def __init__(self, uid: str, name: str | None):
        self.uid = uid
        self.name = name
        self.in_room: "Room | None" = None
        self.in_game: bool = False

        self.card = []
        self.gun = []

    def __str__(self):
        return f"{self.name if self.name else self.uid}"

    async def send(self, msg: UniMessage, bot: Bot):
        await msg.send(Target(self.uid, private=True), bot)

    def __eq__(self, value: "Player"):
        return self.uid == value.uid

    def __hash__(self):
        return int(md5(self.uid.encode()).hexdigest(), base=16)

    def attend_room(self, room: "Room"):
        if self.in_room:
            return CallResult(
                CallResultStatus.ERROR,
                f"❌ {self.name} 已经在房间 {self.in_room.room_name} 中, 请先退出此房间",
            )

        self.in_room = room
        return CallResult(CallResultStatus.SUCCESS, f"🚗 {self.name} 加入房间")

    def exit_room(self):
        if self.in_room is None:
            return CallResult(
                CallResultStatus.ERROR,
                f"❌ {self.name} 没有加入任何房间",
            )

        self.in_room = None
        return CallResult(CallResultStatus.SUCCESS, f"🛫 {self.name} 退出房间")


class Room:
    def __init__(
        self,
        owner: Player,
        gid: str,
        target: Target,
        room_name: None | str = None,
    ):
        self.target = target
        self.attendable = True
        self.gid = gid
        self.owener = owner

        if room_name is None:
            self.room_name = get_random_roomname()
        else:
            self.room_name = room_name

        result = owner.attend_room(self)
        if result.status == CallResultStatus.ERROR:
            raise LiarException(result.msg)

        self.players: list[Player] = [self.owener]

    def on_add_player(self, player: Player):
        if not self.attendable:
            return CallResult(
                CallResultStatus.ERROR, "❌ 房间已不能加入，请新开房间或等待房间"
            )

        if player in self.players:
            return CallResult(CallResultStatus.ERROR, f"❌ {player} 已经在房间中")

        self.players.append(player)
        return CallResult(CallResultStatus.SUCCESS, f"✔ {player} 加入房间")

    def on_remove_player(self, player: Player):
        self.players.remove(player)
        if len(self.players) == 0:
            self.attendable = False
            return CallResult(CallResultStatus.WARNING, "✔ 房间人数少于1，已关闭")

        if self.owener == player:
            self.owener = self.players[0]

            return CallResult(
                CallResultStatus.SUCCESS,
                f"✔ {player} 退出房间, 房主更换为: {self.owener.name}",
            )

        return CallResult(CallResultStatus.SUCCESS, f"✔ {player} 退出房间")

    def on_get_players(self):
        return CallResult(
            CallResultStatus.SUCCESS,
            f"👀 房间内玩家：\n\t{'\n\t'.join([str(player) for player in self.players])}",
        )

    async def on_start_game(self, event: Event, bot: Bot):
        msg = UniMessage().text("游戏开始\n")
        for player in self.players:
            msg = msg.at(player.uid)

        await msg.send(event, bot)

    def __hash__(self):
        return int(md5(self.room_name.encode()).hexdigest(), base=16)

    def __eq__(self, other: "Room"):
        return self.room_name == other.room_name


class Game:
    def __init__(self, room: Room, bot: Bot):
        self.room: Room = room
        self.status: str = "stopped"
        self.cards = []
        self.bot = bot

        # self.current_player = None

        self.player_states = {player.uid: "alive" for player in room.players}

        self.cur_player_idx = 0

        self.last_player = None
        self.last_cards = []

    @staticmethod
    def generate_cards():
        types = ["Q", "K", "A", "Joker"]
        nums = [6, 6, 6, 2]

        cards = [types[i] for i in range(len(types)) for j in range(nums[i])]
        cur_need = rnd.choice(types[:-1])

        return cards, cur_need

    def get_alive(self):
        return [
            player
            for player in self.room.players
            if self.player_states[player.uid] == "alive"
        ]

    async def load_bullets(self, num_real: int = 1):
        for player in self.room.players:
            player.gun = [0] * (6 - num_real) + [1] * num_real
            rnd.shuffle(player.gun)
            # logger.info(f"player {player.name}'s gun is like {player.gun}")

    async def start(self, num_real_bullet: int = 1):
        self.cur_player_idx = 0
        for player in self.room.players:
            player.card = []
            player.in_game = True

        await self.load_bullets(num_real_bullet)
        await UniMessage().text(
            f"游戏开始！本次每人枪内装有 {num_real_bullet} 颗子弹"
        ).send()
        game_round = 0

        while len(self.get_alive()) > 1:
            game_round += 1

            self.cards, cur_need = Game.generate_cards()
            # logger.debug(self.cards)
            rnd.shuffle(self.cards)

            tasks: list[asyncio.Task] = []

            broadcast_msg = UniMessage().text("本轮需要出的牌是：").text(cur_need)
            await broadcast_msg.send(self.room.target, self.bot)

            for player in self.get_alive():
                sent_cards = []
                for _ in range(5):  # 1人5张
                    sent_cards.append(self.cards.pop())
                msg = (
                    UniMessage()
                    .text(f"🎴 本局游戏第 {game_round} 次发牌...\n")
                    .text("🎴 您抽到了: \n\t")
                    .text(" | ".join(sent_cards))
                    .text("\n\t")
                    .text(" | ".join(("①", "②", "③", "④", "⑤")))
                    .text("\n\n🎴 请输入牌的序号发牌\n (e.g. /fp 1 2 3)")
                )
                player.card = sent_cards
                # await player.send(msg, self.bot)
                tasks.append(asyncio.create_task(player.send(msg, self.bot)))

            done, pending = await asyncio.wait(tasks)
            assert len(pending) == 0, "消息发送失败"
            tasks.clear()

            self.last_cards = []
            self.last_player = None
            self.small_round = True
            while self.small_round:
                for _ in range(len(self.get_alive())):

                    alive_players = self.get_alive()
                    cur = alive_players[self.cur_player_idx]
                    if len(cur.card) == 0:
                        self.cur_player_idx = (self.cur_player_idx + 1) % len(
                            alive_players
                        )
                        continue

                    if not self.small_round:
                        break

                    if await self.check_last_player_with_card(cur):
                        await self.shoot_player(cur, "其他存活玩家手中的牌都已出完")
                        break

                    if len(cur.card) == 0:
                        continue

                    # self.current_player = cur
                    await self.acknowledge_action(cur)

                    player_action, info_dict = await input_store.wait_input(
                        self.room.gid, cur.uid
                    )  # type: ignore
                    res = await self.handle_player_action(
                        cur, player_action, cur_need, info_dict
                    )
                    while res == -1:
                        player_action, info_dict = await input_store.wait_input(
                            self.room.gid, cur.uid
                        )  # type: ignore
                        res = await self.handle_player_action(
                            cur, player_action, cur_need, info_dict
                        )

        await UniMessage().text(f"{self.get_alive()[0].name} 赢了！").send(
            self.room.target, self.bot
        )
        for player in self.room.players:
            player.in_game = False

    async def check_last_player_with_card(self, cur):
        zero_cards = 0

        for player in self.get_alive():
            if player == cur:
                continue
            else:
                if len(player.card) == 0:
                    zero_cards += 1

        return zero_cards == len(self.get_alive()) - 1

    async def get_player_fp(self, cur: Player, target_cards: list):
        # target_cards = map(int, action.split(" ")[1:])
        cards_info = [cur.card[(i - 1) % len(cur.card)] for i in target_cards]
        for _ in cards_info:
            cur.card.remove(_)

        return cards_info

    async def handle_player_action(
        self,
        cur: Player,
        player_action: str,
        cur_need: str,
        info_dict: dict,
    ):
        if player_action.startswith("/fp"):
            # 玩家出牌
            player_fp_index = info_dict.get("indexs")
            assert player_fp_index is not None, "玩家输入错误"

            self.cur_player_idx = (self.cur_player_idx + 1) % len(self.get_alive())

            cards_info = await self.get_player_fp(cur, player_fp_index)
            cards_info = [card.replace("Joker", cur_need) for card in cards_info]

            dbg_msg = UniMessage().text("您出的牌是: \n\t")
            for card in cards_info:
                dbg_msg.text(card)
            dbg_msg.text(
                " (Joker 为万能牌，自动替换为当前所需出的牌) \n剩余手牌：\n\t"
            ).text("|".join(cur.card)).text("\n\t").text(
                "|".join(("①", "②", "③", "④", "⑤")[: len(cur.card)])
            )

            await cur.send(dbg_msg, self.bot)

            broadcast_msg = (
                UniMessage()
                .text(f"玩家 {cur.name} (")
                .at(cur.uid)
                .text(f") 打出了 {len(cards_info)} 张牌，并宣称这都是 {cur_need}")
            )
            await broadcast_msg.send(self.room.target, self.bot)

            self.last_cards = cards_info
            self.last_player = cur
        else:
            # 质疑！

            if len(self.last_cards) == 0 or self.last_player is None:
                msg = UniMessage().text("❌ 上家没有出牌，无法质疑 请直接出牌")
                await msg.send(self.room.target, self.bot)
                await asyncio.sleep(0.5)

                return -1
                # continue

            # dbg_msg = (
            #     UniMessage()
            #     .text(
            #         f"您质疑了上家 {self.last_player.name}，他出的牌为 {self.last_cards}"
            #     )
            #     .text(
            #         f"质疑是否成功？： {not all(card == cur_need for card in self.last_cards)}"
            #     )
            # )
            # await cur.send(dbg_msg, self.bot)

            if not all(card == cur_need for card in self.last_cards):
                broadcast_msg = UniMessage().text(
                    f"{cur.name} 质疑 {self.last_player.name} 成功！他出的牌为 {self.last_cards}"
                )
                shoot_target = self.last_player
                delta_player = -1
                reason = "被质疑成功"
            else:
                broadcast_msg = UniMessage().text(
                    f"{cur.name} 质疑 {self.last_player.name} 失败！他出的牌为 {self.last_cards}"
                )
                shoot_target = cur
                delta_player = 0
                reason = "质疑上家失败"

            await broadcast_msg.send(self.room.target, self.bot)
            await self.shoot_player(shoot_target, reason)
            self.cur_player_idx = (self.cur_player_idx + delta_player) % len(
                self.get_alive()
            )

    async def acknowledge_action(self, cur: Player):
        # logger.debug(f"{cur.name} 开始操作")
        msg = (
            UniMessage()
            .at(cur.uid)
            .text(f" 现在轮到{cur.name}操作了！\n(可选择: /fp 出牌 || /zy 质疑)")
        )
        await msg.send(self.room.target, self.bot)

    async def shoot_player(self, player: Player, reason: str = "质疑上家失败"):
        self.small_round = False  # 开枪，即需要重发牌

        cur_bullet = player.gun.pop()
        await UniMessage().text(
            f"由于 {reason}, {player.name or player.uid} 需要开一次枪..."
        ).send(self.room.target, self.bot)
        await asyncio.sleep(3)

        if cur_bullet == 1:
            # 死了
            broadcast_msg = UniMessage().text(
                f"{player.name or player.uid} 射出了一颗真的子弹然后死了"
            )
            self.player_states[player.uid] = "dead"
        else:
            # 没死
            broadcast_msg = UniMessage().text(
                f"{player.name or player.uid} 并未射出子弹"
            )
        broadcast_msg.text(f"\n他的枪已射击 {6 - len(player.gun)} 次")
        await broadcast_msg.send(self.room.target, self.bot)
        await asyncio.sleep(2)

    def stop(self):
        pass
