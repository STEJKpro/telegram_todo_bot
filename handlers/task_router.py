from aiogram import Router, F, Bot
from aiogram.utils.markdown import hbold
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButtonRequestUser,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
    
)
from db_connection import session
from models import User, Task
from aiogram.utils.keyboard import (InlineKeyboardBuilder, ReplyKeyboardBuilder)

from typing import List
from bot.types import Album
from sqlalchemy import delete
from datetime import datetime


task_router=Router()

class Form(StatesGroup):
    author = State()
    executor = State()
    discription = State()
    deadline = State()
    priority = State()
    file = State()
    
#Начало создание задачи
@task_router.message(Command("new_task"))
@task_router.message(F.text.casefold() == "new_task")
async def command_task(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.executor)
    await state.update_data (author=message.from_user.id)    
    users = session.query(User).filter(User.chat_id != message.from_user.id)
    
    builder = ReplyKeyboardBuilder()
    for user_obj in users:
        builder.add(
            KeyboardButton(
                text = f"\n{user_obj.id}. {user_obj.name} {user_obj.surname}",  
            )
                    )
    await message.answer(
        "Выбери того, кто должен выполнить работу?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


#Вывод списка созданых задач пользователем
@task_router.message(Command("task_list"))
@task_router.message(F.text.casefold() == "task_list")
async def command_task(message: Message) -> None:
    tasks = list(session.query(Task).filter(Task.author_id == message.from_user.id, Task.status != 'Выполнено'))
    if not tasks:
        return await message.answer(
                "Нет актуальных созданых вами задач",
                reply_markup=ReplyKeyboardRemove()
            )
    # task_list = str()
    # for task in tasks:
    #     task_list+=  f"{tasks.index(task)+1}. {task.discription}({task.priority})\n"
    # await message.answer(
    #     task_list,
    #     reply_markup=ReplyKeyboardRemove()
    # )

    # """ /list - Получение списка всех задач """
    # tasks = get_tasks_by_id(message.from_user.id)
    for task in tasks:
        delete_button = InlineKeyboardButton(text='Удалить ❌', callback_data=f'delete_task {task.id}')
        # done_button = InlineKeyboardButton(text='Выполнено', callback_data=f'done_task {task.id}')
        await message.answer(f'<b>ID:</b> {task.id}\n'
                             f'<b>Описание задачи:</b> {task.discription}\n'
                             f'<b>Приоритет:</b> {task.priority}\n'
                             f'<b>Дедлайн:</b> {task.deadline.strftime("%d.%m.%Y")}\n'
                             f'<b>Статус задачи:</b> {task.status}\n'
                             f'<b>Исполнитель:</b> {session.query(User).filter(User.chat_id == task.executor_id).one().name}'
                             ,
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[delete_button]]))



#Вывод список задач на исполнении
@task_router.message(Command("todo"))
@task_router.message(F.text.casefold() == "todo")
async def todo_list(message: Message,) -> None:
    tasks = list(session.query(Task).filter(Task.executor_id == message.from_user.id, Task.status != 'Выполнено'))
    if not tasks:
        return await message.answer(
                "Нет актуальных задач",
                reply_markup=ReplyKeyboardRemove()
            )
    for task in tasks:
        done_button = InlineKeyboardButton(text='Выполнено ✅', callback_data=f'done_task {task.id}')
        await message.answer(f'<b>ID:</b> {task.id}\n'
                             f'<b>Описание задачи:</b> {task.discription}\n'
                             f'<b>Приоритет:</b> {task.priority}\n'
                             f'<b>Дедлайн:</b> {task.deadline.strftime("%d.%m.%Y")}\n'
                             f'<b>Статус задачи:</b> {task.status}\n'
                             f'<b>Автор:</b> {session.query(User).filter(User.chat_id == task.author_id).one().name}',
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[done_button]]),)
        
        
#Сохраняем исполнителя и запрашиваем описание
@task_router.message(Form.executor)
# @task_router.message()
async def process_executor(message: Message, state: FSMContext) -> None:
    await state.update_data(executor=message.text.split('.')[0])
    await state.set_state(Form.discription)
    await message.answer(
        "Напиши что надо сделать)",
        reply_markup=ReplyKeyboardRemove(),
    )

#Сохраняем описание и запрашиваем файл
@task_router.message(Form.discription)
async def process_discription(message: Message, state: FSMContext) -> None:
    await state.update_data(discription=message.text)
    await state.set_state(Form.file)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Пропустить",
        callback_data="skip_file",
        ),
    )
    await message.answer(
        f"Выберите файл, или нажмите пропустить",
        reply_markup=builder.as_markup(),
    )
    
#Сохраняем дедлайн и запрашиваем приоритет
@task_router.message(Form.deadline)
async def process_deadline(message: Message, state: FSMContext) -> None:
    try:
        deadline = datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError:
        await message.answer("Дата введена неверно! Попробуйте еще раз!\n <b>ДД.ММ.ГГГГ</b>")
        return
        
    await state.update_data(deadline=deadline)
    await state.set_state(Form.priority)
    await message.answer(
        f"Какой приоритет у этой задачи?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Высокий"),
                    KeyboardButton(text="Средний"),
                    KeyboardButton(text="Низкий"),
                    
                ],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ),
    )
    
#Обрабатываем отмену файла и запрашиваем дедлайн
@task_router.callback_query(Form.file)
async def process_skip_file(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.update_data(file = None)
    await state.set_state(Form.deadline)
    await bot.edit_message_text(
        text = "Загрузка файла пропущена",
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id, 
        reply_markup=None
    )
    await callback.message.answer(
        f"Когда нужно сделать эту задачу? \nФормат даты(ДД.ММ.ГГГГ)",
        reply_markup=ReplyKeyboardRemove(),
    )
    
# Обрабатываем файл и запрашиваем дедлайн

@task_router.message(Form.file, ~F.media_group_id, F.document)
async def process_file(message: Message, state: FSMContext,) -> None:
    if message.document:
        await state.update_data( file = {
                                        'document_id' : message.document.file_id})
        await state.set_state(Form.deadline)
        await message.answer(
            f"файл получен. Когда нужно сделать эту задачу? \nФормат даты(ДД.ММ.ГГГГ)",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            f"Отправьте файл.",
            reply_markup=ReplyKeyboardRemove(),
        )


#Обрабатываем файлы и запрашиваем дедлайн
@task_router.message(Form.file, F.media_group_id)
async def process_file(message: Message, album: Album, state: FSMContext,) -> None:
    await state.update_data(file = {'media_group': album.as_media_group})
    await state.set_state(Form.deadline)
    return await message.answer(
            f"файлы получен. Когда нужно сделать эту задачу? \nФормат даты(ДД-ММ-ГГГГ)",
            reply_markup=ReplyKeyboardRemove(),
        )
  
  
#Обрабатываем приоритет и создаем задачу
@task_router.message(Form.priority)
async def process_priority(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(priority=message.text)
    data = await state.get_data()
    executor_chat_id = session.query(User).filter_by(id=data["executor"]).one_or_none().chat_id
    await state.clear()
    task = Task(
        discription = data["discription"],
        priority = data["priority"],
        author_id = message.from_user.id,
        executor_id = executor_chat_id,
        deadline=  data["deadline"],
        status = "Новая задача",
        )

    session.add(task)
    session.commit()
    await bot.send_message(
        chat_id=executor_chat_id, 
        text= 
            f"<b>Вам пришла задача</b>\n"
            f"<b>Приоритет</b>: {data['priority']}\n"
            f"<b>Дедлайн</b>: {data['deadline']}\n"
            f"<b>Задача:</b> {data['discription']}\n"
            f'<b>Автор:</b> {session.query(User).filter(User.chat_id == task.author_id).one().name}',
    )
    if data.get("file"):
        if data["file"].get("media_group"):
            await bot.send_media_group(chat_id=data["executor"], media=data["file"]["media_group"])
        else:
            await bot.send_document(chat_id=data["executor"], document=data["file"]["document_id"])
    await message.answer(
        f"Красота, задача создана и отправлена исполнителю\n"
            f"Приоритет: {data['priority']}\n"
            f"Дедлайн: {data['deadline']}\n"
            f"Задача: {data['discription']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    

@task_router.callback_query(F.data.startswith('delete_task'))
async def delete_task_button_press(callback: CallbackQuery,  bot: Bot):
    """ Удаление задачи кнопкой """
    task_id = callback.data.split(' ')[-1]
    task = session.query(Task).get(task_id)
    session.delete(task)
    session.commit()
    await bot.send_message(
        chat_id=task.executor_id, 
        text=   f'<b>❌ ЗАДАЧА УДАЛЕНА!</b> {task.id}\n'
                f'<b>ID:</b> {task.id}\n'
                f'<b>Описание задачи:</b> {task.discription}\n'
                f'<b>Приоритет:</b> {task.priority}\n'
                f'<b>Дедлайн:</b> {task.deadline.strftime("%d.%m.%Y")}\n'
                f'<b>Статус задачи:</b> {task.status}\n'
                f'<b>Автор:</b> {session.query(User).filter(User.chat_id == task.author_id).one().name}'
    )
    await callback.message.edit_text(
         f'<b>❌ ЗАДАЧА УДАЛЕНА!</b> {task.id}\n'
                f'<b>ID:</b> {task.id}\n'
                f'<b>Описание задачи:</b> {task.discription}\n'
                f'<b>Приоритет:</b> {task.priority}\n'
                f'<b>Дедлайн:</b> {task.deadline.strftime("%d.%m.%Y")}\n'
                f'<b>Статус задачи:</b> {task.status}\n'
                f'<b>Исполнитель:</b> {session.query(User).filter(User.chat_id == task.executor_id).one().name}'
    )
    
    
@task_router.callback_query(F.data.startswith('done_task'))
async def delete_task_button_press(callback: CallbackQuery,  bot: Bot):
    """ Отметка задачи о выполнении """
    task_id = callback.data.split(' ')[-1]
    task = session.query(Task).get(task_id)
    task.status = 'Выполнено'
    session.commit()
    await bot.send_message(chat_id=task.author_id, text=f"<b>✅ Задача выполнена!</b> \n{task.discription}")
    await callback.message.edit_text(f'<b>✅ Задача отмечена как выполненая</b>\n{task.discription}] ')