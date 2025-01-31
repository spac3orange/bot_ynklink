from aiogram.types import BotCommand


async def set_commands_menu(bot):
    """
        Set up the main menu commands for the bot.
        Args:
            bot (telegram.Bot): The Telegram bot instance.
        Returns:
            None
        """
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Главное меню'),
        BotCommand(command='/privacy_policy',
                   description='Политика конфиденциальности'),
        BotCommand(command='/oferta',
                   description='Договор оферта'),
        BotCommand(command='/payment',
                   description='Описание процедуры оплаты'),
        BotCommand(command='/support',
                   description='Техническая Поддержка')
    ]

    await bot.set_my_commands(main_menu_commands)
