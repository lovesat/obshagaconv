from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

bot = Bot(token="")
dp = Dispatcher(bot, storage=MemoryStorage())

tech_help = ""

class UserInput(StatesGroup):
    waiting_for_last_name = State()
    waiting_for_first_name = State()
    waiting_for_block_number = State()
    waiting_for_room_number = State()
    waiting_for_block_to_choose = State()
    waiting_for_room_to_choose = State()
    waiting_for_message_text = State()
    waiting_for_response = State()
