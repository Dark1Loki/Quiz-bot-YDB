from aiogram import types, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from service import generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index, quiz_data
from database import get_score, update_score, reset_quiz_state, load_quiz_data


router = Router()

@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    global quiz_data

    try:
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e


    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1

    score = get_score(callback.from_user.id)
    update_score(callback.from_user.id, score + 1)

    await update_quiz_index(callback.from_user.id, current_question_index)

    if not quiz_data:
        quiz_data = await load_quiz_data()

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        score = get_score(callback.from_user.id)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершён!\nВы набрали {score} баллов.")

  
@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    global quiz_data

    try:
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e


    if not quiz_data:
        quiz_data = await load_quiz_data()
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        from database import get_score  # если ещё не импортирован
        score = get_score(callback.from_user.id)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершён!\nВы набрали {score} баллов.")



# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    reset_quiz_state(message.from_user.id)

    await message.answer_photo(
        photo="https://storage.yandexcloud.net/quiz-assets/cover.png",
        caption="Добро пожаловать в квиз!"
    )

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
    

