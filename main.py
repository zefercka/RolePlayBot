import discord
import sqlite3
import random
import asyncio

db = sqlite3.connect('server.db', check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    id INT,
    money INT,
    passport TEXT,
    level INT,
    level_ex INT,
    work_time INT
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS blackjack (
    id INT,
    money INT,
    on_hand TEXT,
    dealer TEXT,
    count_hand INT,
    count_dealer INT,
    game_status TEXT,
    message_id NULL
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS cards (
    id INT,
    name TEXT)""")

db.commit()




client = discord.Client(intents=discord.Intents().all())


async def money_sort(money):
    moneys = list(str(money))
    if money > 99999999:
        money = '$' + str(moneys[0] + moneys[1] + moneys[2] + '.' + moneys[3] + moneys[4]) + 'M'
    elif money > 9999999:
        money = '$' + str(moneys[0] + moneys[1] + '.' + moneys[2] + moneys[3]) + 'M'
    elif money > 999999:
        money = '$' + str(moneys[0] + '.' + moneys[1] + moneys[2]) + 'M'
    elif money > 99999:
        money = '$' + str(moneys[0] + moneys[1] + moneys[2] + '.' + moneys[3] + moneys[4]) + 'K'
    elif money > 9999:
        money = '$' + str(moneys[0] + moneys[1] + '.' + moneys[2] + moneys[3]) + 'K'
    elif money > 999:
        money = '$' + str(moneys[0] + '.' + moneys[1] + moneys[2]) + 'K'
    else:
        money = '$' + str(money)
    return money
    pass


async def level_check(level_ex_add, message):
    level = list(sql.execute(f'SELECT level FROM users WHERE id = {message.author.id}').fetchone())
    level = int(level[0])

    level_ex = list(sql.execute(f'SELECT level_ex FROM users WHERE id = {message.author.id}').fetchone())
    level_ex = int(level_ex[0])
    level_ex += level_ex_add

    if level_ex >= ((level + 1) * 1000):

        role = discord.utils.get(message.guild.roles, name=f'Уровень {level}')
        await message.author.remove_roles(role)

        role = discord.utils.get(message.guild.roles, name=f'Уровень {level+1}')
        await message.author.add_roles(role)

        lev = (f'UPDATE users SET level= {level + 1} WHERE id={message.author.id}')
        sql.execute(lev)
        db.commit()

        lev_ex = (f'UPDATE users SET level_ex= {level_ex - (level + 1) * 1000} WHERE id={message.author.id}')
        sql.execute(lev_ex)
        db.commit()

    else:
        lev_ex = (f'UPDATE users SET level_ex= {level_ex}')
        sql.execute(lev_ex)
        db.commit()


async def money_edit(message, money_add, add_or_not, money):
    ids = int(message.author.id)
    money = (f'UPDATE users SET money={money} WHERE id={ids}')
    sql.execute(money)
    db.commit()
    money = (sql.execute(f'SELECT money FROM users WHERE id = "{message.author.id}"')).fetchone()
    money = int(money[0])
    if add_or_not == '+':
        emb = discord.Embed(description=(f'**Имя:** {message.author.mention} \n'
                                         f'**Сумма:** {add_or_not}{await money_sort(money_add)} | '
                                         f'{await money_sort(money)} \n'
                                         f'**Чат:** {message.channel.mention}'),
                            color=0x66bb6a, timestamp=message.created_at)
        emb.set_author(icon_url=message.author.avatar_url, name='Изменение баланса')
    else:
        emb = discord.Embed(description=(f'**Имя:** {message.author.mention} \n'
                                         f'**Сумма:** {add_or_not}{await money_sort(money_add)} | '
                                         f'{await money_sort(money)} \n'
                                         f'**Чат:** {message.channel.mention}'),
                            color=0xef5350, timestamp=message.created_at)
        emb.set_author(icon_url=message.author.avatar_url, name='Изменение баланса')
    logs = client.get_channel(594060555518476329)
    await logs.send(embed=emb)


async def cards_count(hand, number_of_cards):
    hand_list = hand
    count_hand = 0
    for i in range(int(number_of_cards)):
        hand = hand_list[i]
        if '2' in hand:
            count_hand += 2
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '3' in hand:
            count_hand += 3
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '4' in hand:
            count_hand += 4
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '5' in hand:
            count_hand += 5
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '6' in hand:
            count_hand += 6
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '7' in hand:
            count_hand += 7
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '8' in hand:
            count_hand += 8
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '9' in hand:
            count_hand += 9
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif '0' in hand:
            count_hand += 10
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif 'J' in hand:
            count_hand += 10
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif 'Q' in hand:
            count_hand += 10
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif 'K' in hand:
            count_hand += 10
            if count_hand > 21 and 'A' in hand:
                count_hand -= 10
        elif 'A' in hand:
            if count_hand + 1 > 21:
                count_hand += 1
            elif count_hand + 11 > 21:
                count_hand += 1
            else:
                count_hand += 11
    return count_hand


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    chan = message.channel.name
    if chan != 'лог-канал':
        print('{0.channel.name} {0.author}: {0.content}'.format(message))
    if chan == 'вокзал🚂':
        user = [str(message.author), int(message.author.id), 100, 'No', 0, 0, 0]
        sql.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?);", user)
        db.commit()
        print("Новый пользователь: " + str(message.author))

    elif chan == '⚒лесорубка⚒' or chan == '📬курьер📬' or chan == '📦грузчик📦':
        if int((sql.execute(f'SELECT work_time FROM users WHERE id = "{message.author.id}"')).fetchone()[0]) == 0:
            money = (sql.execute(f'SELECT money FROM users WHERE id = "{message.author.id}"')).fetchone()
            money = int(money[0])
            money_add = int(random.uniform(10, 50))
            money += money_add

            await level_check(1, message)

            async with message.channel.typing():
                await message.delete()
            await money_edit(message, money_add, '+', money)
            work_t = (f'UPDATE users SET work_time="1" WHERE id="{message.author.id}"')
            sql.execute(work_t)
            db.commit()
            await asyncio.sleep(5)
            work_t = (f'UPDATE users SET work_time="0" WHERE id="{message.author.id}"')
            sql.execute(work_t)
            db.commit()
        else:
            async with message.channel.typing():
                await message.delete()

    elif chan == '📒паспортный-стол📒':
        if message.content == 'Сделать паспорт':
            pas = (sql.execute((f'SELECT passport FROM users WHERE id = "{message.author.id}"'))).fetchone()
            pas = str(pas[0])
            if pas == 'No':
                mon = (sql.execute((f'SELECT money FROM users WHERE id = "{message.author.id}"'))).fetchone()
                money = int(mon[0])
                if money >= 1000:
                    money -= 1000
                    ids = int(message.author.id)
                    await money_edit(message, 1000, '-', money)
                    pas = ('UPDATE users SET passport="Wait" WHERE id=' + str(ids))
                    sql.execute(pas)
                    db.commit()
                    async with message.channel.typing():
                        await message.channel.send(f'{message.author.name}, ваш паспорт будет готов через 5 минут',
                                                   delete_after=2)
                        await asyncio.sleep(2)
                        await message.delete()
                else:
                    async with message.channel.typing():
                        await message.channel.send(f'{message.author.name}, на вашем счету недостаточно средств',
                                                   delete_after=2)
                        await asyncio.sleep(2)
                        await message.delete()
            else:
                await message.channel.send(f'{message.author.name}, ваш паспорт уже готов',
                                           delete_after=2)
                await asyncio.sleep(2)
                await message.delete()
        elif message.content == 'Активировать паспорт':
            pas = (sql.execute((f'SELECT passport FROM users WHERE id = "{message.author.id}"'))).fetchone()
            pas = str(pas[0])
            if pas == 'Wait':
                ids = int(message.author.id)
                pas = (f'UPDATE users SET passport="Yes" WHERE id={ids}')
                sql.execute(pas)
                db.commit()
                role_passport = message.author.guild.get_role(594359486651695129)
                await message.author.add_roles(role_passport)
                async with message.channel.typing():
                    await message.channel.send(f'{message.author.name}, ваш паспорт успешно активирован.',
                                               delete_after=2)
                    await asyncio.sleep(2)
                    await message.delete()
            else:
                async with message.channel.typing():
                    await message.channel.send(f'{message.author.name}, вы ещё не сделали паспорт.',
                                               delete_after=2)
                    await asyncio.sleep(2)
                    await message.delete()

    elif chan == 'дб':
        user = [str(message.author), int(message.author.id), 100, 'No', 0, 0, 0]
        sql.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?);", user)
        db.commit()

        print("Новый пользователь: " + str(message.author))

    elif chan == '🎰игровой-автомат-1🎰' or chan == '🎰игровой-автомат-2🎰' or chan == '🎰игровой-автомат-3🎰':
        if 'слот' in message.content or 'Слот' in message.content:
            y = len(message.content)
            money_slot = ''
            z = message.content.split()
            for i in z:
                if i.isdigit():
                    money_slot += i
            try:
                money_slot = int(money_slot)
                money = (sql.execute(f'SELECT money FROM users WHERE id = "{message.author.id}"')).fetchone()
                money = int(money[0])
                if money_slot >= 50:
                    if money >= money_slot:
                        l = []
                        for i in range(3):
                            x = random.randint(1, 10)
                            if x == 1 or x == 4 or x == 7 or x == 9:
                                l.append('🍒')
                            elif x == 2 or x == 5 or x == 8 or x == 10:
                                l.append('🍉')
                            else:
                                l.append('🎲')

                        if str(l[0] + l[1] + l[2]) == '🎲🎲🎲':
                            money += (money_slot * 3)
                            await money_edit(message, money_slot * 2, '+', money)
                            emb = discord.Embed(title='Вы выиграли!', description=(f'{message.author.mention} \n '
                                                                                   f'{(l[0] + l[1] + l[2])} \n'
                                                                                   f'Выигрыш: {money_slot*3}'),
                                                color=0x2E8B57)
                        elif str(l[0] + l[1] + l[2]) == '🍒🍒🍒' or str(l[0] + l[1] + l[2]) == '🍉🍉🍉':
                            money += (money_slot * 2)
                            await money_edit(message, money_slot, '+', money)
                            emb = discord.Embed(title='Вы выиграли!', description=(f'{message.author.mention} \n \n '
                                                                                   f'{(l[0] + l[1] + l[2])} \n \n'
                                                                                   f'Выигрыш: {money_slot*2}'),
                                                color=0x2E8B57)
                        else:
                            money -= money_slot
                            await money_edit(message, money_slot, '-', money)
                            emb = discord.Embed(title='Вы проиграли!', description=(f'{message.author.mention} \n \n'
                                                                                    f'**{(l[0] + l[1] + l[2])}** \n\n'
                                                                                    f'Проигрыш: {money_slot}'),
                                                color=0xDc0f0f)

                        async with message.channel.typing():
                            await message.channel.send(embed=emb, delete_after=2)
                            await asyncio.sleep(2)
                            await message.delete()
                    else:
                        async with message.channel.typing():
                            emb = discord.Embed(title='Недостаточно средств', description=(f'{message.author.mention} \n '
                                                                                f'На вашем счету недостаточно средств'),
                                                color=0xdc0f0f)
                            await message.channel.send(embed=emb, delete_after=2)
                            await asyncio.sleep(2)
                            await message.delete()

                else:
                    emb = discord.Embed(title='Ошибка', description=(f'{message.author.mention} \n '
                                                                     f'Сумма слишком мала'),
                                        сolor=0xFF0000)
                    async with message.channel.typing():
                        await message.channel.send(embed=emb, delete_after=2)
                        await asyncio.sleep(2)
                        await message.delete()
            except:
                emb = discord.Embed(title='Ошибка', description=(f'{message.author.mention} \n '
                                                                 f'Неверный формат суммы'),
                                    сolor=0xFF0000)
                async with message.channel.typing():
                    await message.channel.send(embed=emb, delete_after=2)
                    await asyncio.sleep(2)
                    await message.delete()
        else:
            if str(message.author.id) != '807688473535840286':
                async with message.channel.typing():
                    await message.delete()
    
    elif chan == 'основной':
        for emoji in message.guild.emojis:
            print(emoji.id)
            print(emoji.name)
            id_card = [emoji.id, str(emoji.name)]
            sql.execute("INSERT INTO cards VALUES(?, ?);", id_card)
            db.commit()

    elif chan == '🃏блэкджек-1🃏' or chan == '🃏блэкджек-2🃏' or chan == '🃏блэкджек-3🃏' or chan == '🃏блэкджек-4🃏':
        if 'начать' in message.content or 'Начать' in message.content:
            async with message.channel.typing():
                await message.delete()
            game_status = (sql.execute(f'SELECT * FROM blackjack WHERE id = "{message.author.id}"')).fetchone()
            if game_status is None:
                money_blackjack = ''
                z = message.content.split()

                for i in z:
                    if i.isdigit():
                        money_blackjack += i

                try:
                    money_blackjack = int(money_blackjack)

                    money = (sql.execute(f'SELECT money FROM users WHERE id = "{message.author.id}"')).fetchone()
                    money = int(money[0])

                    if money_blackjack >= 150:
                        if money >= money_blackjack:

                            money -= money_blackjack

                            sql.execute(f'UPDATE users SET money="{money}" '
                                        f'WHERE id="{message.author.id}"')
                            db.commit()

                            cards_hand = []
                            cards_hand_id = []

                            while True:
                                row_number = random.randint(1, 52)
                                card = (sql.execute(f'SELECT name FROM cards WHERE rowid={row_number}')).fetchone()
                                if card[0] not in cards_hand:
                                    card_id = (sql.execute(f'SELECT id FROM cards WHERE rowid={row_number}')).fetchone()
                                    cards_hand.append(card[0])
                                    cards_hand_id.append(card_id[0])
                                    if len(cards_hand) == 2:
                                        break

                            cards_dealer = []
                            cards_dealer_id = []

                            while True:
                                row_number = random.randint(1, 52)
                                card = (sql.execute(f'SELECT name FROM cards WHERE rowid={row_number}')).fetchone()
                                if card[0] not in cards_dealer:
                                    card_id = (sql.execute(f'SELECT id FROM cards WHERE rowid={row_number}')).fetchone()
                                    cards_dealer_id.append(card_id[0])
                                    cards_dealer.append(card[0])
                                    if len(cards_dealer) == 2:
                                        break

                            count_dealer = await cards_count(cards_dealer, 2)
                            count_hand = await cards_count(cards_hand, 2)

                            if count_dealer < 21 and count_hand < 21:

                                desc = (f'Напишите `ещё` - взять ещё карту; `удвоить` - '
                                        f' удвоить; `стоп` - остановиться. \n'
                                        f'\n Ставка: {await money_sort(money_blackjack)}')

                                emb = discord.Embed(title=f'{message.author}',
                                                    description=str(desc),
                                                    color=0x81bdff)

                                em = client.get_emoji(cards_hand_id[0])
                                em1 = client.get_emoji(cards_hand_id[1])

                                emb.add_field(name="У вас:", value=f'{em} {em1} \n'
                                                                   f'\n Счёт: {count_hand}',
                                              inline=True)

                                count_dealer = await cards_count(cards_dealer, 1)

                                em = client.get_emoji(cards_dealer_id[0])

                                emb.add_field(name="У дилера:", value=f'{em} '
                                                                      f'<:empty:{int(809496866521088070)}>\n'
                                                                      f'\n Счёт: {count_dealer}',
                                              inline=True)
                                async with message.channel.typing():
                                    mes_bot = await message.channel.send(embed=emb, delete_after=300)

                                    count_dealer = await cards_count(cards_dealer, 2)
                                    user = [int(message.author.id), int(money_blackjack),
                                            f'{cards_hand[0]} {cards_hand[1]}',
                                            f'{cards_dealer[0]} {cards_dealer[1]}', count_hand, count_dealer, 'START',
                                            mes_bot.id]
                                    sql.execute("INSERT INTO blackjack VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user)
                                    db.commit()

                                    await asyncio.sleep(300)
                                    sql.execute(f'DELETE FROM blackjack WHERE id="{message.author.id}"')
                                    db.commit()

                            elif count_hand == 21:
                                count_dealer = await cards_count(cards_dealer, 1)

                                emb = discord.Embed(title=f'{message.author}', color=0x66bb6a,
                                                    description=f'\n Дилер потерял {await money_sort(money_blackjack)}'
                                                                f'\n')
                                emb.add_field(name="У вас:", value=f'<:{cards_hand[0]}:{cards_hand_id[0]}>'
                                                                   f'<:{cards_hand[1]}:{cards_hand_id[1]}> \n'
                                                                   f'\n Счёт: Блэкджек', inline=True)

                                emb.add_field(name="У дилера:", value=f'<:{cards_dealer[0]}:{cards_dealer_id[0]}> '
                                                                      f'<:empty:{int(809496866521088070)}>\n'
                                                                      f'\n Счёт: {count_dealer}',
                                              inline=True)
                                async with message.channel.typing():
                                    await message.channel.send(embed=emb)

                            elif count_dealer == 21:
                                emb = discord.Embed(title=f'{message.author}', color=0xef5350,
                                                    description=f'\n Вы потеряли {await money_sort(money_blackjack)}')
                                emb.add_field(name="У вас:", value=f'<:{cards_hand[0]}:{cards_hand_id[0]}>'
                                                                   f'<:{cards_hand[1]}:{cards_hand_id[1]}> \n'
                                                                   f'\n Счёт: {count_hand}', inline=True)

                                emb.add_field(name="У дилера:", value=f'<:{cards_dealer[0]}:{cards_dealer_id[0]}> '
                                                                      f'<:{cards_dealer[1]}:{cards_dealer_id[1]}> \n'
                                                                      f'\n Счёт: Блэкджек',
                                              inline=True)
                                async with message.channel.typing():
                                    await message.channel.send(embed=emb)

                            else:
                                emb = discord.Embed(title=f'{message.author}', color=0xff9d00, description='Ничья')
                                emb.add_field(name="У вас:", value=f'<:{cards_hand[0]}:{cards_hand_id[0]}>'
                                                                   f'<:{cards_hand[1]}:{cards_hand_id[1]}> \n'
                                                                   f'\n Счёт: Блэкджек', inline=True)

                                emb.add_field(name="У дилера:", value=f'<:{cards_dealer[0]}:{cards_dealer_id[0]}> '
                                                                      f'<:{cards_dealer[1]}:{cards_dealer_id[1]}> \n'
                                                                      f'\n Счёт: Блэкджек',
                                              inline=True)
                                async with message.channel.typing():
                                    await message.channel.send(embed=emb)

                        else:
                            async with message.channel.typing():
                                emb = discord.Embed(title='Недостаточно средств',
                                                    description=(f'{message.author.mention} \n '
                                                                 f'На вашем счету недостаточно средств'),
                                                    color=0xec2925)
                                await message.channel.send(embed=emb, delete_after=2)

                    else:
                        emb = discord.Embed(title='Ошибка', description=(f'{message.author.mention} \n '
                                                                         f'Сумма слишком мала'),
                                            сolor=0xec2925)
                        async with message.channel.typing():
                            await message.channel.send(embed=emb, delete_after=2)

                except:
                    emb = discord.Embed(title='Ошибка', description=(f'{message.author.mention} \n '
                                                                     f'Неверный формат суммы'),
                                        сolor=0xec2925)
                    async with message.channel.typing():
                        await message.channel.send(embed=emb, delete_after=2)

            else:
                emb = discord.Embed(title='Ошибка', description=(f'{message.author.mention} \n '
                                                                 f'**Игра уже идёт!**'),
                                    сolor=0xec2925)
                async with message.channel.typing():
                    await message.channel.send(embed=emb, delete_after=2)
                    await asyncio.sleep(2)

        elif message.content == 'ещё':
            async with message.channel.typing():
                await message.delete()
            game_status = (sql.execute(f'SELECT * FROM blackjack WHERE id = "{message.author.id}"')).fetchone()
            if game_status is not None:
                deck = ['2_C', '3_C', '4_C', '5_C', '6_C', '7_C', '8_C', '9_C', '0_C', 'J_C', 'Q_C', 'K_C',
                        'A_C',  # Червы

                        '2_B', '3_B', '4_B', '5_B', '6_B', '7_B', '8_B', '9_B', '0_B', 'J_B', 'Q_B', 'K_B',
                        'A_B',  # Буби

                        '2_T', '3_T', '4_T', '5_T', '6_T', '7_T', '8_T', '9_T', '0_T', 'J_T', 'Q_T', 'K_T',
                        'A_T',  # Крести

                        '2_P', '3_P', '4_P', '5_P', '6_P', '7_P', '8_P', '9_P', '0_P', 'J_P', 'Q_P', 'K_P',
                        'A_P']

                random.shuffle(deck)

                cards_on_hand = (sql.execute(f'SELECT on_hand FROM blackjack WHERE id="{message.author.id}"')).fetchone()

                card_on_hand = deck.pop()

                while card_on_hand in cards_on_hand[0]:
                    card_on_hand = deck.pop()

                cards_on_hand = cards_on_hand + ' ' + card_on_hand
                print(cards_on_hand)

                sql.execute(f'UPDATE blackjack SET on_hand="{cards_on_hand}" WHERE id="{message.author.id}"')
                db.commit()

                hand_value = (sql.execute(f'SELECT count_hand FROM blackjack WHERE id="{message.author.id}"')).fetchone()
                hand_value = hand_value[0]

                value_hand = await cards_count(card_on_hand, hand_value, cards_on_hand)

                cards_list = []

                cards_on_hand = list(cards_on_hand)

                for i in range(int((len(cards_on_hand) + 1) / 4)):
                    card = str(cards_on_hand[i * 4]) + str(cards_on_hand[i * 4 + 1]) + str(cards_on_hand[i * 4 + 2])
                    cards_list.append(card)

                hint = (f'Напишите `ещё` - взять ещё карту; `удвоить` - '
                        f' удвоить; `стоп` - остановиться. \n')

                desc = ''

                for i in range(len(cards_list)):
                    card = cards_list[i]

                    id_on_hand = sql.execute(f"SELECT id FROM cards WHERE name='{card}'").fetchone()
                    id_on_hand = int(id_on_hand[0])

                    em = client.get_emoji(id_on_hand)

                    desc = desc + str(f'{em}')

                card_dealer = sql.execute(f"SELECT dealer FROM blackjack WHERE id='{message.author.id}'").fetchone()
                card_dealer = (card_dealer[0])

                value_dealer = sql.execute(f"SELECT count_dealer FROM blackjack WHERE id='{message.author.id}'").fetchone()
                value_dealer = int(value_dealer[0]) - await cards_count(card_dealer[4] + card_dealer[5] + card_dealer[6],
                                                                        0, card_dealer)

                card_dealer = card_dealer[0] + card_dealer[1] + card_dealer[2]

                id_dealer = sql.execute(f"SELECT id FROM cards WHERE name='{card_dealer}'").fetchone()
                em = client.get_emoji(id_dealer[0])

                money_blackjack = sql.execute(
                    f'SELECT money FROM blackjack WHERE id="{message.author.id}"').fetchone()
                money_blackjack = money_blackjack[0]

                if value_hand < 21:
                    sql.execute(f'UPDATE blackjack SET count_hand="{value_hand}" '
                                f'WHERE id="{message.author.id}"')
                    db.commit()

                    emb = discord.Embed(title=f'{message.author}',
                                        description=str(hint) + f'\n Ставка: {await money_sort(money_blackjack)} \n',
                                        color=0x81bdff)

                    emb.add_field(name="У вас:", value=f'{desc} \n'
                                                       f'\n Счёт: {value_hand}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{em} '
                                                          f'<:empty:{int(809496866521088070)}>\n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    messages = (sql.execute(
                        f'SELECT message_id FROM blackjack WHERE id="{message.author.id}"')).fetchone()
                    messages = (messages[0])

                    messages = await message.channel.fetch_message(messages)

                    await messages.edit(embed=emb)

                elif value_hand == 21:

                    emb = discord.Embed(title=f'{message.author}',
                                        description=f'\n Дилер потерял {await money_sort(money_blackjack)} \n',
                                        color=0x66bb6a)

                    emb.add_field(name="У вас:", value=f'{desc} \n'
                                                       f'\n Счёт: {value_hand}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{em} '
                                                          f'<:empty:{int(809496866521088070)}>\n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    messages = (sql.execute(
                        f'SELECT message_id FROM blackjack WHERE id="{message.author.id}"')).fetchone()
                    messages = (messages[0])

                    messages = await message.channel.fetch_message(messages)

                    await messages.edit(embed=emb)

                    sql.execute(f'DELETE FROM blackjack WHERE id="{message.author.id}"')
                    db.commit()

                else:

                    emb = discord.Embed(title=f'{message.author}',
                                        description=f'\n Вы потеряли {await money_sort(money_blackjack)} \n',
                                        color=0xef5350)

                    emb.add_field(name="У вас:", value=f'{desc} \n'
                                                       f'\n Счёт: {value_hand}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{em} '
                                                          f'<:empty:{int(809496866521088070)}>\n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    messages = (sql.execute(
                        f'SELECT message_id FROM blackjack WHERE id="{message.author.id}"')).fetchone()
                    messages = (messages[0])

                    messages = await message.channel.fetch_message(messages)

                    await messages.edit(embed=emb)

                    sql.execute(f'DELETE FROM blackjack WHERE id="{message.author.id}"')
                    db.commit()

            else:
                emb = discord.Embed(title=f'{message.author}', color=0x9000, description='Чтобы начать игру напишите: \n'
                                                                                         '`Начать сумма`')
                async with message.channel.typing():
                    await message.channel.send(embed=emb)

        elif message.content == 'Удвоить' or message.content == 'удвоить':
            async with message.channel.typing():
                await message.delete()
            game_status = (sql.execute(f'SELECT * FROM blackjack WHERE id = "{message.author.id}"')).fetchone()
            if game_status is not None:
                hint = (f'Напишите `ещё` - взять ещё карту; `удвоить` - '
                        f' удвоить; `стоп` - остановиться. \n')

                money = (sql.execute(f'SELECT money FROM users WHERE id="{message.author.id}"')).fetchone()
                money_blackjack = (sql.execute(f'SELECT money FROM blackjack WHERE id="{message.author.id}"')).fetchone()

                if (money[0] - money_blackjack[0]) >= 0:

                    hand_value = (
                        sql.execute(f'SELECT count_hand FROM blackjack WHERE id="{message.author.id}"')).fetchone()

                    messages = (sql.execute(
                        f'SELECT message_id FROM blackjack WHERE id="{message.author.id}"')).fetchone()

                    card_dealer = sql.execute(f"SELECT dealer FROM blackjack WHERE id='{message.author.id}'").fetchone()
                    card_dealer = (card_dealer[0])

                    value_dealer = sql.execute(
                        f"SELECT count_dealer FROM blackjack WHERE id='{message.author.id}'").fetchone()
                    value_dealer = int(value_dealer[0]) - await cards_count(
                        card_dealer[4] + card_dealer[5] + card_dealer[6], 0, card_dealer)

                    messages = await message.channel.fetch_message(messages[0])

                    cards_on_hand = (
                        sql.execute(f'SELECT on_hand FROM blackjack WHERE id="{message.author.id}"')).fetchone()

                    cards_list = cards_on_hand[0].split(' ')

                    print(cards_list)

                    id_dealer = 0

                    desc = ''

                    for i in range(len(cards_list)):
                        card = cards_list[i]

                        id_on_hand = sql.execute(f"SELECT id FROM cards WHERE name='{card}'").fetchone()
                        id_on_hand = int(id_on_hand[0])

                        em = client.get_emoji(id_on_hand)

                        desc = desc + str(f'{em}')

                    em = client.get_emoji(id_dealer)

                    emb = discord.Embed(title=f'{message.author}',
                                        description=str(hint) + f'\n Ставка: {await money_sort(2*money_blackjack)} \n',
                                        color=0x81bdff)

                    emb.add_field(name="У вас:", value=f'{desc} \n'
                                                       f'\n Счёт: {hand_value[0]}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{em} '
                                                          f'<:empty:{int(809496866521088070)}>\n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    sql.execute(f'UPDATE blackjack SET money="{2*money_blackjack}" WHERE id="{message.author.id}"')
                    db.commit()

                    sql.execute(f'UPDATE users SET money="{money - money_blackjack}" WHERE id="{message.author.id}"')
                    db.commit()

                else:
                    emb = discord.Embed(title=f'Недостаточно средств', color=0x9000)

                    emb.add_field(name=f'{message.author.id}', value='На вашем счету недостаточно средств.')
                    async with message.channel.typing():
                        await message.channel.send(embed=emb)

            else:
                emb = discord.Embed(title=f'{message.author}', color=0x9000, description='Чтобы начать игру напишите: \n'
                                                                                         '`Начать сумма`')
                async with message.channel.typing():
                    await message.channel.send(embed=emb)

        elif message.content == 'стоп' or message.content == 'Стоп':
            game_status = (sql.execute(f'SELECT * FROM blackjack WHERE id = "{message.author.id}"')).fetchone()
            if game_status is not None:
                deck = ['2_C', '3_C', '4_C', '5_C', '6_C', '7_C', '8_C', '9_C', '0_C', 'J_C', 'Q_C', 'K_C',
                        'A_C',  # Червы

                        '2_B', '3_B', '4_B', '5_B', '6_B', '7_B', '8_B', '9_B', '0_B', 'J_B', 'Q_B', 'K_B',
                        'A_B',  # Буби

                        '2_T', '3_T', '4_T', '5_T', '6_T', '7_T', '8_T', '9_T', '0_T', 'J_T', 'Q_T', 'K_T',
                        'A_T',  # Крести

                        '2_P', '3_P', '4_P', '5_P', '6_P', '7_P', '8_P', '9_P', '0_P', 'J_P', 'Q_P', 'K_P',
                        'A_P']

                random.shuffle(deck)

                card_dealer = sql.execute(f"SELECT dealer FROM blackjack WHERE id='{message.author.id}'").fetchone()
                card_dealer = (card_dealer[0])

                cards_list_dealer = []

                cards_dealer = list(card_dealer)

                for i in range(int((len(cards_dealer) + 1) / 4)):
                    card = str(cards_dealer[i * 4]) + str(cards_dealer[i * 4 + 1]) + str(cards_dealer[i * 4 + 2])
                    cards_list_dealer.append(card)

                value_dealer = sql.execute(
                    f"SELECT count_dealer FROM blackjack WHERE id='{message.author.id}'").fetchone()
                value_dealer = int(value_dealer[0])

                a = 0
                while a == 0:
                    if (value_dealer >= 17) and (value_dealer < 19):
                        ran = random.randint(1, 2)
                        if ran == 1:
                            card = deck.pop()
                            value_dealer = await cards_count(card, value_dealer, card_dealer)
                            cards_list_dealer.append(card)

                    elif value_dealer < 17:
                        card = deck.pop()
                        value_dealer = await cards_count(card, value_dealer, card_dealer)
                        cards_list_dealer.append(card)
                    else:
                        a = 1

                desc = ''
                for i in range(len(cards_list_dealer)):
                    card = cards_list_dealer[i]

                    id_dealer = sql.execute(f"SELECT id FROM cards WHERE name='{card}'").fetchone()
                    id_dealer = int(id_dealer[0])

                    em = client.get_emoji(id_dealer)

                    desc = desc + str(f'{em}')

                card_hand = sql.execute(f"SELECT on_hand FROM blackjack WHERE id='{message.author.id}'").fetchone()
                card_hand = (card_hand[0])

                cards_list_hand = []

                cards_hand = list(card_hand)

                for i in range(int((len(cards_hand) + 1) / 4)):
                    card = str(cards_hand[i * 4]) + str(cards_hand[i * 4 + 1]) + str(cards_hand[i * 4 + 2])
                    cards_list_hand.append(card)

                desc1 = ''
                for i in range(len(cards_list_hand)):
                    card = cards_list_hand[i]

                    id_on_hand = sql.execute(f"SELECT id FROM cards WHERE name='{card}'").fetchone()
                    id_on_hand = int(id_on_hand[0])

                    em = client.get_emoji(id_on_hand)

                    desc1 = desc1 + str(f'{em}')

                value_hand = sql.execute(
                    f"SELECT count_hand FROM blackjack WHERE id='{message.author.id}'").fetchone()
                value_hand = value_hand[0]

                messages = (sql.execute(
                    f'SELECT message_id FROM blackjack WHERE id="{message.author.id}"')).fetchone()
                messages = (messages[0])

                messages = await message.channel.fetch_message(messages)

                money_blackjack = (sql.execute(f'SELECT money FROM blackjack WHERE id={message.author.id}')).fetchone()

                sql.execute(f'DELETE FROM blackjack WHERE id="{message.author.id}"')
                db.commit()

                if (value_hand > value_dealer) or (value_dealer > 21):
                    emb = discord.Embed(title=f'{message.author}',
                                        description=f'\n Дилер потерял {await money_sort(money_blackjack[0])}',
                                        color=0x66bb6a)

                    emb.add_field(name="У вас:", value=f'{desc1} \n'
                                                       f'\n Счёт: {value_hand}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{desc} \n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    await messages.edit(embed=emb)

                elif (value_hand < value_dealer) and (value_dealer <= 21):
                    emb = discord.Embed(title=f'{message.author}',
                                        description=f'\n Вы потеряли {await money_sort(money_blackjack[0])}',
                                        color=0xef5350)

                    emb.add_field(name="У вас:", value=f'{desc1} \n'
                                                       f'\n Счёт: {value_hand}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{desc} \n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    await messages.edit(embed=emb)

                else:
                    emb = discord.Embed(title=f'{message.author}',
                                        description='Ничья', color=0xff9d00)

                    emb.add_field(name="У вас:", value=f'{desc1} \n'
                                                       f'\n Счёт: {value_hand}', inline=True)

                    emb.add_field(name="У дилера:", value=f'{desc} \n'
                                                          f'\n Счёт: {value_dealer}',
                                  inline=True)

                    await messages.edit(embed=emb)

                async with message.channel.typing():
                    await message.delete()
                    await asyncio.sleep(5)
                    await messages.delete()

            else:
                emb = discord.Embed(title=f'{message.author}', color=0x9000,
                                    description='Чтобы начать игру напишите: \n'
                                                '`Начать сумма`')
                async with message.channel.typing():
                    await message.channel.send(embed=emb, delete_after=5)
                    await message.delete()

        else:
            if message.author.id != 807688473535840286:
                async with message.channel.typing():
                    await message.delete()

    elif chan == '💵банк💵':
        if message.content == 'баланс' or message.content == 'Баланс':
            if (sql.execute((f'SELECT money FROM users WHERE id={message.author.id}')).fetchone()) is not None:
                mon = list(sql.execute((f'SELECT money FROM users WHERE id={message.author.id}')).fetchone())
                money = int(mon[0])
                async with message.channel.typing():
                    emb = discord.Embed(title='Банкомат', description=(f'Имя: {message.author.mention} \n'
                                                                       f'Баланс: {await money_sort(money)}'),
                                        color=0x00ff00)
                    await message.channel.send(embed=emb, delete_after=2)
                    await asyncio.sleep(2)
                    await message.delete()
        else:
            if str(message.author.id) != '807688473535840286':
                async with message.channel.typing():
                    await message.delete()

    elif chan == '🏫мэрия🏫':
        if message.content == 'уровень' or message.content == 'Уровень':
            if (sql.execute((f'SELECT level FROM users WHERE id={message.author.id}')).fetchone()) is not None:
                level = list(sql.execute(f'SELECT level FROM users WHERE id={message.author.id}').fetchone())
                level = int(level[0])

                level_ex = list(sql.execute(f'SELECT level_ex FROM users WHERE id={message.author.id}').fetchone())
                level_ex = int(level_ex[0])

                emb = discord.Embed(title='Уровень',
                                    description=f'Уровень: {level} \n '
                                                f'Опыт: {level_ex} | {(level + 1) * 1000} <:Q_P:809042411941658634>',
                                    color=0x81bdff)

                async with message.channel.typing():
                    await message.channel.send(embed=emb, delete_after=2)
                    await asyncio.sleep(2)
                    await message.delete()
        else:
            if message.author.id != 807688473535840286:
                async with message.channel.typing():
                    await message.delete()


@client.event
async def on_member_remove(member):
    x = sql.execute(f'SELECT name FROM users WHERE id = "{member.id}"')
    print('Пользователь покинул сервер:' + str(x.fetchone()))
    sql.execute(f'DELETE FROM users WHERE id = "{member.id}"')
    db.commit()


client.run(('ODA3Njg4NDczNTM1ODQwMjg2.YB7ogg.f11Uk5M5AL6EkxxZwOJP4UdctKs'))
