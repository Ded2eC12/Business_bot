        #Импорт модулей

from random import randrange, choice
from time import time, sleep
import sqlite3
import disnake
from disnake.ext import commands
with sqlite3.connect("database.db") as db:
    cursor = db.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS reg(
    name INTEGER,
    balance INTEGER,
    time_user INTEGER,
    time_crime INTEGER,
    time_job INTEGER
    );
    CREATE TABLE IF NOT EXISTS base(
    channel TEXT,
    channels TEXT
    )"""
    cursor.executescript(query)

    bot = commands.Bot(command_prefix="_", intents=disnake.Intents.all())
    bot.remove_command('help')
            #Появление бота

    @bot.event
    async def on_ready():
        print(f"Бот {bot.user.name}, запущен!")

        channel_list_name = []
        channel_list = ""
        cursor.execute("SELECT channels FROM base")
        if cursor.fetchone() is None:
            for guild in bot.guilds:
                for channel in str(guild.text_channels):
                    channel_list += channel
                channel_list_split = channel_list.split()
                for channel in channel_list_split:
                    if "name" in channel:
                        channel_list_name.append(channel)

            nice_channel = []
            for i in channel_list_name:
                nice_channel.append((i.replace("name=", "")).replace("'", ""))
            for i in nice_channel:
                cursor.execute("INSERT INTO base(channels) VALUES(?)", [i])

        db.commit()
        cursor.execute("SELECT * FROM base")


    @bot.slash_command()
    @commands.has_permissions(administrator=True)
    async def ch(ctx, channel_name: str):
        """Выбор основного канала"""

            # Получения списка всех каналов
        author_name = ctx.author.name
        cursor.execute("SELECT channels FROM base")
        channel_list_name = []
        if len(channel_list_name) == 0:
            for tup in cursor:
                world = ""
                for word in range(len(tup)):
                    if tup[word] not in ["(", ")", "'"]:
                        world += tup[word]
                channel_list_name.append(world)

        cursor.execute("SELECT channel FROM base")

            # Обновление канала в базу данных

        if cursor.fetchone() is not None and channel_name in channel_list_name:
            cursor.execute("UPDATE base SET channel = ?", [channel_name])
            db.commit()
            embed = disnake.Embed(title="Новый основной канал выбран!",
                                  description=f"канал обновлён пользователем {author_name}",
                                  color=0x00FF00)
            await ctx.send(embed=embed)

        else:
            embed = disnake.Embed(title="Канал не найден!",
                                  description=f"{author_name}, пожалуйста введите имя канала корректно!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)

    @ch.error
    async def ch_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("У вас недостаточно прав для выполнения этой команды.")

    @bot.command()
    async def work(ctx):

        """Создание переменных для получения основного канала из базы данных"""

        mane_channel = []
        mane_channel1 = ""
        cursor_channel = []
        cursor.execute("SELECT channel FROM base")

        """Получение основного канала"""

        for cur in cursor:
            cursor_channel.append(cur[0])

        if None not in cursor_channel:
            for chan in cursor_channel:
                if len(mane_channel) == 0:
                    mane_channel.append(chan)
            for i in mane_channel:
                mane_channel1 += i

            """Основной канал получен"""
            guild = ctx.guild
            channel = disnake.utils.get(guild.channels, name=mane_channel1)

            """Создание переменных для работы с командой work и таймером на неё"""

            money = randrange(40, 150)
            cursor.execute("SELECT name FROM reg")
            current_time = time()
            time_now = time()
            author_id = ctx.author.id
            author_name = ctx.author.name

            """Условие для первого запуска и сохранения в базу данных"""

            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO reg(name, balance, time_user) VALUES(?, ?, ?)", [
                    author_id, money, current_time
                ])
                db.commit()
                cursor.execute("SELECT balance FROM reg")

                embed = disnake.Embed(title="Зарплата пришла!!",
                                      description=f"Пользователь: {author_name}\n"
                                                  f"Пополнение на: {money} 💵!",
                                      color=0x00FF00)
                await channel.send(embed=embed)
                try:
                    await ctx.message.delete()
                except disnake.errors.NotFound:
                    pass

                """Условие для последующих запусков"""

            else:

                """Получение списка участников для проверки"""

                cursor.execute("SELECT name FROM reg")
                name_id = []
                for i in cursor:
                    name_id.append(i[0])

                """Регистрация новых участников"""

                if author_id not in name_id:
                    cursor.execute("INSERT INTO reg(name, balance, time_user) VALUES(?, ?, ?)", [
                        author_id, money, current_time
                    ])
                    db.commit()
                    cursor.execute("SELECT balance FROM reg")

                    embed = disnake.Embed(title="Зарплата пришла!!",
                                          description=f"Пользователь: {author_name}\n"
                                                      f"Пополнение на: {money} 💵!",
                                          color=0x00FF00)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass

                    """Условие для работы раз в 600 секунд"""

                else:
                    cursor.execute("SELECT * FROM reg")
                    for i in cursor:
                        if i[0] == author_id:
                            if i[2] is None or i[2] + 300 < time_now:
                                balance = i[1] + money
                                cursor.execute("UPDATE reg SET balance = ?, time_user = ? WHERE name = ?", [
                                    balance, time_now, author_id
                                ])
                                db.commit()

                                embed = disnake.Embed(title="Зарплата пришла!!",
                                                      description=f"Пользователь: {author_name}\n"
                                                                  f"Пополнение на: {money} 💵!",
                                                      color=0x00FF00)
                                await channel.send(embed=embed)
                                try:
                                    await ctx.message.delete()
                                except disnake.errors.NotFound:
                                    pass
                            else:
                                embed = disnake.Embed(title="Ожидайте!",
                                                      description=f"Пользователь: {author_name}\n"
                                                                  f"Время: {round(i[2] + 300 - time_now)} секунд!",
                                                      color=0xFF0000)
                                await channel.send(embed=embed)
                                try:
                                    await ctx.message.delete()
                                except disnake.errors.NotFound:
                                    pass

        else:
            embed = disnake.Embed(title="Не выбран основной канал!!",
                                  description=f"Пожалуйста введите команду '/ch' и выберите основной канал!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass


    @bot.command()
    async def balance(ctx):

        """Создание переменных для получения основного канала из базы данных"""

        mane_channel = []
        mane_channel1 = ""
        cursor_channel = []
        cursor.execute("SELECT channel FROM base")

        """Получение основного канала"""

        for cur in cursor:
            cursor_channel.append(cur[0])

        if None not in cursor_channel:
            for chan in cursor_channel:
                if len(mane_channel) == 0:
                    mane_channel.append(chan)
            for i in mane_channel:
                mane_channel1 += i

            """Основной канал получен"""

            guild = ctx.guild
            channel = disnake.utils.get(guild.channels, name=mane_channel1)

            """Создание переменных для работы с балансом пользователя"""

            cursor.execute("SELECT balance, name FROM reg")
            balance_user = 0
            user_id = ctx.author.id

            """Условие для выбора баланса"""

            for i in cursor:
                if user_id == i[1]:
                    balance_user += i[0]

            embed = disnake.Embed(title=f"Баланс {ctx.author.name}:",
                                  description=f"Ваш баланс: {balance_user} 💵",
                                  color=0x00FF00)
            await channel.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass

        else:
            embed = disnake.Embed(title="Не выбран основной канал!!",
                                  description=f"Пожалуйста введите команду '/ch' и выберите основной канал!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass

    @bot.command()
    async def crime(ctx):

        """Создание переменных для получения основного канала из базы данных"""

        mane_channel = []
        mane_channel1 = ""
        cursor_channel = []
        cursor.execute("SELECT channel FROM base")

        """Получение основного канала"""

        for cur in cursor:
            cursor_channel.append(cur[0])

        if None not in cursor_channel:
            for chan in cursor_channel:
                if len(mane_channel) == 0:
                    mane_channel.append(chan)
            for i in mane_channel:
                mane_channel1 += i

            """Основной канал получен"""

            guild = ctx.guild
            channel = disnake.utils.get(guild.channels, name=mane_channel1)

            """Создание переменных для работы с функцией 'CRIME'"""

            cursor.execute("SELECT name, balance FROM reg")
            chance = randrange(0, 101)
            user_id_list = []
            user_id = ctx.author.id
            balance_user = 0
            balance_random = 0

            """Цикл для расспаковки name и balance"""

            for b in cursor:
                if b[0] != user_id:
                    user_id_list.append(b[0])
                if b[0] == user_id:
                    balance_user = b[1]

            """Цикл для расспаковки name и balance рандомного usera"""

            random_user = ctx.author.id
            for i in range(10000):
                if random_user != ctx.author.id:
                    break
                else:
                    random_user = choice(user_id_list)

            cursor.execute("SELECT name, balance FROM reg")
            for b in cursor:
                if b[0] == random_user:
                    balance_random = b[1]

            user_rand = await bot.fetch_user(random_user)

            time_now = round(time())

            """Цикл для расспаковки времени для таймера"""

            cursor.execute("SELECT time_crime FROM reg")
            stop = 0
            time_u = 0
            for i in cursor:
                if None not in i:
                    if stop == 0:
                        time_u += i[0]
                        stop += 1

            """Условие при котором прошло 32 часа с момента ограбления"""

            if time_now >= time_u + 115200:

                embed = disnake.Embed(title="Ожидание!",
                                      description=f"Пользователь: {ctx.author.name}\n"
                                                  f"Статус: ожидание",
                                      color=0x808000)
                await channel.send(embed=embed)

                sleep(3)

                """Условие для победы или поражения в ограблении"""

                if chance >= 80:
                    cursor.execute("UPDATE reg SET balance = ?, time_crime = ? WHERE name = ?", [
                        balance_user + 3000, time_now, ctx.author.id
                    ])
                    db.commit()
                    sleep(3)
                    embed = disnake.Embed(title="Успех!",
                                          description=f"Пользователь: {ctx.author.name}\n"
                                                      f"Сумма: 3000",
                                          color=0x00FF00)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass
                else:
                    cursor.execute("UPDATE reg SET balance = ?, time_crime = ? WHERE name = ?", [
                        balance_random + 1000, time_now, random_user
                    ])
                    db.commit()
                    sleep(3)
                    embed = disnake.Embed(title="Провал!",
                                          description=f"Пользователь: {user_rand.name}\n"
                                                      f"Сумма: 1000",
                                          color=0xFF0000)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass

            else:

                """Переменные для вывода остатка времени"""

                seconds = time_u + 115200 - time_now
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = (seconds % 3600) % 60

                embed = disnake.Embed(title="Ожидайте!!",
                                      description=f"Время до начала 'ограбления'\n"
                                                  f": {hours} чаc(ов), {minutes} минут(ы), {seconds} секунд(ы) !",
                                      color=0xFF0000)
                await channel.send(embed=embed)
                try:
                    await ctx.message.delete()
                except disnake.errors.NotFound:
                    pass

            """else для if в котором не выбран основной канал!"""

        else:
            embed = disnake.Embed(title="Не выбран основной канал!!",
                                  description=f"Пожалуйста введите команду '/ch' и выберите основной канал!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass

    @bot.command()
    async def tr(ctx, member: disnake.Member, amount: int):

        mane_channel = []
        mane_channel1 = ""
        cursor_channel = []
        cursor.execute("SELECT channel FROM base")

        """Получение основного канала"""

        for cur in cursor:
            cursor_channel.append(cur[0])

        if None not in cursor_channel:
            for chan in cursor_channel:
                if len(mane_channel) == 0:
                    mane_channel.append(chan)
            for i in mane_channel:
                mane_channel1 += i

            """Основной канал получен"""

            guild = ctx.guild
            channel = disnake.utils.get(guild.channels, name=mane_channel1)

            cursor.execute("SELECT name FROM reg")
            member_id = 0
            name_list = []
            for i in cursor:

                user_name = await bot.fetch_user(i[0])
                name_list.append(user_name.name)

                if user_name.name == member.name:
                    member_id = i[0]
            if member.name in name_list:
                cursor.execute("SELECT balance FROM reg WHERE name = ?", [ctx.author.id])
                balance_ctx = 0
                for i in cursor:
                    balance_ctx = i[0]

                cursor.execute("SELECT balance FROM reg WHERE name = ?", [member_id])
                balance_member = 0
                for i in cursor:
                    balance_member = i[0]

                if balance_ctx >= amount:
                    cursor.execute("UPDATE reg SET balance = ? WHERE name = ?", [
                        balance_ctx - amount, ctx.author.id
                        ])
                    db.commit()

                    cursor.execute("UPDATE reg SET balance = ? WHERE name = ?", [
                        balance_member + amount, member_id
                    ])
                    db.commit()

                    embed = disnake.Embed(title=f"Перевод!",
                                          description=f"Перевёл: {ctx.author.name}\n"
                                                      f"Получил: {member.name}\n"
                                                      f"Сумма: {amount}\n"
                                                      f"Статус: успех!",
                                          color=0x00FF00)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass

                else:
                    embed = disnake.Embed(title=f"Ошибка!",
                                          description=f"Пользователь: {ctx.author.name}\n"
                                                      f"Статус: недостаточно средств!",
                                          color=0xFF0000)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass

            else:
                embed = disnake.Embed(title=f"Не найден {member.mention}!",
                                      description=f"Пользователь: {member.name}\n"
                                                  f"Статус: не зарегистрирован!",
                                      color=0xFF0000)
                await channel.send(embed=embed)
                try:
                    await ctx.message.delete()
                except disnake.errors.NotFound:
                    pass

        else:
            embed = disnake.Embed(title="Не выбран основной канал!!",
                                  description=f"Пожалуйста введите команду '/ch' и выберите основной канал!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass


    @bot.command()
    async def job(ctx):

        """Создание переменных для получения основного канала из базы данных"""

        mane_channel = []
        mane_channel1 = ""
        cursor_channel = []
        cursor.execute("SELECT channel FROM base")

        """Получение основного канала"""

        for cur in cursor:
            cursor_channel.append(cur[0])

        if None not in cursor_channel:
            for chan in cursor_channel:
                if len(mane_channel) == 0:
                    mane_channel.append(chan)
            for i in mane_channel:
                mane_channel1 += i

            """Основной канал получен"""
            guild = ctx.guild
            channel = disnake.utils.get(guild.channels, name=mane_channel1)

            """Создание переменных для работы с командой work и таймером на неё"""

            money = randrange(400, 601)
            cursor.execute("SELECT name FROM reg")
            current_time = time()
            time_now = time()
            author_id = ctx.author.id
            author_name = ctx.author.name

            """Условие для первого запуска и сохранения в базу данных"""

            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO reg(name, balance, time_job) VALUES(?, ?, ?)", [
                    author_id, money, current_time
                ])
                db.commit()
                cursor.execute("SELECT balance FROM reg")

                embed = disnake.Embed(title="Зарплата пришла!!",
                                      description=f"Пользователь: {author_name}\n"
                                                  f"Пополнение на: {money} 💵!",
                                      color=0x00FF00)
                await channel.send(embed=embed)
                try:
                    await ctx.message.delete()
                except disnake.errors.NotFound:
                    pass

                """Условие для последующих запусков"""

            else:

                """Получение списка участников для проверки"""

                cursor.execute("SELECT name FROM reg")
                name_id = []
                for i in cursor:
                    name_id.append(i[0])

                """Регистрация новых участников"""

                if author_id not in name_id:
                    cursor.execute("INSERT INTO reg(name, balance, time_job) VALUES(?, ?, ?)", [
                        author_id, money, current_time
                    ])
                    db.commit()
                    cursor.execute("SELECT balance FROM reg")

                    embed = disnake.Embed(title="Зарплата пришла!!",
                                          description=f"Пользователь: {author_name}\n"
                                                      f"Пополнение на: {money} 💵!",
                                          color=0x00FF00)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass

                    """Условие для работы раз в 600 секунд"""

                else:

                    cursor.execute("SELECT * FROM reg")
                    for i in cursor:
                        if i[0] == author_id:
                            if i[4] is None or i[4] + 14400 < time_now:

                                balance_user = i[1] + money
                                cursor.execute("UPDATE reg SET balance = ?, time_job = ? WHERE name = ?", [
                                    balance_user, time_now, author_id
                                ])
                                db.commit()

                                embed = disnake.Embed(title="Зарплата пришла!!",
                                                      description=f"Пользователь: {author_name}\n"
                                                                  f"Пополнение на: {money} 💵!",
                                                      color=0x00FF00)
                                await channel.send(embed=embed)
                                try:
                                    await ctx.message.delete()
                                except disnake.errors.NotFound:
                                    pass
                            else:
                                seconds = round(i[4] + 14400 - time_now)
                                hours = seconds // 3600
                                minutes = (seconds % 3600) // 60
                                seconds = (seconds % 3600) % 60
                                embed = disnake.Embed(title="Ожидайте!",
                                                      description=f"Пользователь: {author_name}\n"
                                                                  f"Время: {hours} час(ов), {minutes} минут(ты), "
                                                                  f"{seconds} секунд(ы)!",
                                                      color=0xFF0000)
                                await channel.send(embed=embed)
                                try:
                                    await ctx.message.delete()
                                except disnake.errors.NotFound:
                                    pass

        else:
            embed = disnake.Embed(title="Не выбран основной канал!!",
                                  description=f"Пожалуйста введите команду '/ch' и выберите основной канал!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass


    @bot.command()
    async def shop(ctx, role_name: disnake.Role):

        """Создание переменных для получения основного канала из базы данных"""

        mane_channel = []
        mane_channel1 = ""
        cursor_channel = []
        cursor.execute("SELECT channel FROM base")

        """Получение основного канала"""

        for cur in cursor:
            cursor_channel.append(cur[0])

        if None not in cursor_channel:
            for chan in cursor_channel:
                if len(mane_channel) == 0:
                    mane_channel.append(chan)
            for i in mane_channel:
                mane_channel1 += i

            """Основной канал получен"""

            guild = ctx.guild
            channel = disnake.utils.get(guild.channels, name=mane_channel1)

            cursor.execute("SELECT balance FROM reg WHERE name = ?", [ctx.author.id])

            balance_user = 0

            for i in cursor:
              balance_user = i[0]

            roles_id_list = [1120643251708383332, 1120643319073091584, 1138844851341906002]

            correct_balance = 0
            if role_name.id == roles_id_list[0]:
                correct_balance = balance_user - 2000
            elif role_name.id == roles_id_list[1]:
                correct_balance = balance_user - 3000
            elif role_name.id == roles_id_list[2]:
                correct_balance = balance_user - 4000

            if role_name.id in roles_id_list:
                if balance_user >= balance_user - correct_balance:
                    role = disnake.utils.get(ctx.author.roles, name=role_name.name)

                    if role is None:

                        cursor.execute("UPDATE reg SET balance = ? WHERE name = ?", [
                            correct_balance, ctx.author.id
                        ])
                        db.commit()

                        role_id = disnake.utils.get(ctx.guild.roles, id=role_name.id)
                        await ctx.author.add_roles(role_id)

                        embed = disnake.Embed(title="Успешная покупка!",
                                              description=f"Пользователь: {ctx.author.name}\n"
                                                          f"Роль: {role_name.mention}\n"
                                                          f"Цена: {balance_user - correct_balance} 💵",
                                              color=0x00FF00)
                        await channel.send(embed=embed)
                        try:
                            await ctx.message.delete()
                        except disnake.errors.NotFound:
                            pass

                    else:
                        embed = disnake.Embed(title=f"{ctx.author.name}",
                                              description=f"Роль: {role_name.mention}\n"
                                                          f"Статус: уже есть!",
                                              color=0xFF0000)
                        await channel.send(embed=embed)
                        try:
                            await ctx.message.delete()
                        except disnake.errors.NotFound:
                            pass

                else:
                    embed = disnake.Embed(title=f"{ctx.author.name}",
                                          description=f"Роль: {role_name.mention}\n"
                                                      f"Цена: {balance_user - correct_balance} 💵\n"
                                                      f"Статус: недостаточно 💵!",
                                          color=0xFF0000)
                    await channel.send(embed=embed)
                    try:
                        await ctx.message.delete()
                    except disnake.errors.NotFound:
                        pass

            else:
                role_list = [
                    disnake.utils.get(ctx.guild.roles, id=1120643251708383332),
                    disnake.utils.get(ctx.guild.roles, id=1120643319073091584),
                    disnake.utils.get(ctx.guild.roles, id=1138844851341906002)
                ]
                embed = disnake.Embed(title=f"{ctx.author.name}",
                                      description=f"Вы можете купить только:\n"
                                                  f"{role_list[0].mention} - 2000 💵\n"
                                                  f"{role_list[1].mention} - 3000 💵\n"
                                                  f"{role_list[2].mention} - 4000 💵",
                                      color=0xFF0000)
                await channel.send(embed=embed)
                try:
                    await ctx.message.delete()
                except disnake.errors.NotFound:
                    pass

        else:
            embed = disnake.Embed(title="Не выбран основной канал!!",
                                  description=f"Пожалуйста введите команду '/ch' и выберите основной канал!",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            try:
                await ctx.message.delete()
            except disnake.errors.NotFound:
                pass

"""bot.run(Your token)"""