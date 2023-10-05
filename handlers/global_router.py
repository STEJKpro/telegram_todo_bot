import logging
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove

global_router=Router()


@global_router.message(Command("cancel"))
@global_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )