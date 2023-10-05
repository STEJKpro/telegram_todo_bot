from aiogram import Router
from aiogram.utils.markdown import hbold
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from db_connection import session
from models import User

class Registration(StatesGroup):
    name = State()
    surname  = State()


registration_router = Router()


@registration_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    user = session.query(User).filter_by(chat_id = message.from_user.id).one_or_none()
    if not user:
        await state.set_state(Registration.name)
        await message.answer(f"Доброго времени суток, {hbold(message.from_user.full_name)}!\nДля дальнейшего удобства использовани, пройдите, пожалуйста, регистрацию.\nКак вас зовут?")
    else:
        await message.answer(f"Приветствуем Вас, {hbold(user.name)}!\nЗдесь ты можешь оставить задачу и потом получить уведомление о её выполнении. Для того чтобы начать воспользуйся кнопкой \"меню\"")
        
    

@registration_router.message(Registration.name)
async def handle_surname(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Registration.surname)
    await message.answer(
        "Напишите вашу фамилию, пожалуйста!",
        reply_markup=ReplyKeyboardRemove(),
    )
    

@registration_router.message(Registration.surname)
async def handle_name(message: Message, state: FSMContext) -> None:
    await state.update_data(surname=message.text)
    data = await state.get_data()
    await state.clear()

    user = User(
        name=data["name"],
        surname=data["surname"],
        chat_id = message.from_user.id, 
        username = message.from_user.username
        )

    session.add(user)
    session.commit()
    
    await message.answer(
        f"Пользователь создан, спасибо за регистрацию {user.surname} {user.name}\nТеперь вы можете создавать задачи, а так же получать. Для того, чтобы создать новую задачу воспользуйтесь командой /new_task\nБольше команд можно найти в меню.",
        reply_markup=ReplyKeyboardRemove(),
    )

