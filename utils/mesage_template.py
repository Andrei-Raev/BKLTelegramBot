from telebot.formatting import escape_markdown

EMPTY_INVITE = escape_markdown(
    "Добро пожаловать в бота XPEvent!\nПройдите регистрацию на турнир, следуя инструкциям.")

ENTER_NAME = escape_markdown("Введите ваше имя и фамилию:")

INCORRECT_NAME = escape_markdown("Некорректное имя. Попробуйте ещё раз.")

EA_ID_IS_NOT_EXIST = escape_markdown("Похоже, этот EA ID не существует. Попробуйте ещё раз.")

SUCCESS_REGISTRATION = escape_markdown("Вы успешно зарегистрировались!")

ENTER_EA_ID = escape_markdown("Введите ваш EA ID:")

ENTER_PLATFORM = escape_markdown("Выберите платформу")

SELECTED_VALUE = "\nВыбрано: *{}*"  # Имеется одно поле для ввода

INCORRECT_INPUT = escape_markdown("Ввод не выглядит корректным. Попробуйте ещё раз.")

ASK_POLICY = escape_markdown(
    "Для продолжения вы должны согласиться с политикой конфиденциальности и обработки персональных данных\\.")

ACCEPT_POLICY = "\n\nВы *приняли политику*"
DENY_POLICY = ("\n\nВы *отказались от политики*\n"
               "К сожалению, вы не сможете зарегистрироваться\\. Для перезапуска бота нажмите /start")

USER_INFO = "Ваши данные:\n        Telegram: *@{}*\n        Имя: *{}*\n        Платформа: *{}*\n        EA ID: *{}*"
CONFIRM_ACCEPT = "\n\n✅"
