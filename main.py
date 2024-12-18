from sqlalchemy import *
from sqlalchemy.orm import *
import telebot, urllib.parse, uuid, os.path, json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


#Параметры для подключения к серверу MySQL
DB_NAME = 'u1510415_wp832'
DB_USER = 'u1510415_wp832'
DB_PASSWORD = 'yZ1gV6kH6lzD2cQ3'
IP_SERVER = '31.31.198.8'

#Подключение к серверу
engine = create_engine(f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{IP_SERVER}/{DB_NAME}")
engine.connect()

#Подключение к серверу телеграмм
TOKEN = "8004480548:AAGeFHwzOoYhnmatO7F_Dlq-4vsvR13d3r0"
bot = telebot.TeleBot(TOKEN)

#Создание схемы базы данных. Данный класс помогает структурировать данные в результате запроса.
class wpts_user_activity_log(declarative_base()):
    __tablename__ = 'wpts_user_activity_log'
    id = Column(primary_key=True)
    user_id = Column()
    ip = Column()
    created = Column()
    timestamp = Column()
    date_time = Column()
    referred = Column()
    agent = Column()
    platform = Column()
    version = Column()
    model = Column()
    device = Column()
    UAString = Column()
    location = Column()
    page_id = Column()
    url_parameters = Column()
    page_title = Column()
    type = Column()
    last_counter = Column()
    hits = Column()
    honeypot = Column()
    reply = Column()
    page_url = Column()

    def __init__(self,id,
                    user_id,
                    ip,
                    created,
                    timestamp,
                    date_time,
                    referred,
                    agent,
                    platform,
                    version,
                     model,
                     device,
                     UAString,
                     location,
                     page_id,
                     url_parameters,
                     page_title,
                      type,
                      last_counter,
                       hits,
                       honeypot,
                        reply,
                        page_url
                    ):
        self.id = id
        self.user_id = user_id
        self.ip = ip
        self.created = created
        self.timestamp = timestamp
        self.date_time = date_time
        self.referred = referred
        self.agent = agent
        self.platform = platform
        self.version = version
        self.model = model
        self.device = device
        self.UAString = UAString
        self.location = location
        self.page_id = page_id
        self.url_parameters = url_parameters
        self.page_title = page_title
        self.type = type
        self.last_counter = last_counter
        self.hits = hits
        self.honeypot = honeypot
        self.reply = reply
        self.page_url = page_url


    def __repr__(self):
        return f"({self.id})" \
               f"({self.name})" \
               f"({self.path})" \
               f"({self.user_address})" \
               f"({self.special_notes})" \
               f"({self.sender})" \
               f"({self.resolution})" \
               f"({self.receive_flag})" \
               f"({self.read_flag})" \
               f"({self.owner})" \
               f"({self.output_date})" \
               f"({self.number_output})" \
               f"({self.number_input})" \
               f"({self.log})" \
               f"({self.date_upload})" \
               f"({self.in_date})" \
               f"({self.address_flag})" \
               f"({self.archive_flag})"
#Создаём сессию запроса
session = sessionmaker(bind=engine)
session.configure(bind=engine)
session = session()

#Функция поиска отелей по названию
def search_item(hotel_name):
    session = sessionmaker(bind=engine)
    session.configure(bind=engine)
    session = session()
    ids = list()
    for item in session.query(wpts_user_activity_log).filter(
            wpts_user_activity_log.url_parameters.contains(f"%utm_content={hotel_name}&%")).all():
       ids.append(item.id)
    session.close()
    return ids

#Функция получения информации о записи по ID
def get_item(id):
    session = sessionmaker(bind=engine)
    session.configure(bind=engine)
    session = session()
    result = session.query(wpts_user_activity_log).filter(wpts_user_activity_log.id == id).first()
    session.close()
    return result

#Обработчик для текстовых сообщений
@bot.message_handler()
def new_mess(message):
    if message.text == "/start":
        bot.send_message(chat_id=message.from_user.id,
                         text=f"Добро пожаловать! Введите название отеля:")

        #Создание файла для истории
        if os.path.exists(f"{message.from_user.id}_history.txt"):
            pass
        else:
            new_file = open(f"{message.from_user.id}_history.txt", "w")
            new_file.close()
    else:
        try:
            if len(search_item(message.text))==0:
                bot.send_message(chat_id=message.from_user.id, text="По данному запросу не найдено не одной записи.")
            else:
                markup_rep = InlineKeyboardMarkup()
                markup_rep.add(
                    InlineKeyboardButton(f"+ (след. страница)", callback_data=f"next_{message.from_user.id}"))
                history_data = {"last_count": 0, "ids": search_item(message.text)}

                #Cоздаём файл с историей запроса для запоминания выбора пользователя
                history_file = open(f"{message.from_user.id}_history.txt", "w")
                history_file.write(json.dumps(history_data))
                history_file.close()
                new_item_start_char = "\n"
                bot.send_message(chat_id=message.from_user.id,
                                 text=f"По запросу '{message.text}' найдено: {len(search_item(message.text))} записей\n\n"
                                      f"------------ 1 запись ------------\n"
                                      f"Дата: {get_item(history_data['ids'][0]).date_time}\n"
                                      f"Данные:\n{(new_item_start_char).join(urllib.parse.unquote(get_item(history_data['ids'][0]).url_parameters).split('&')).replace('=',': ')}",

                                 reply_markup=markup_rep)
        except:
            bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка, попробуйте снова!")

#Обработчик Inlint
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if "next" in call.data:
            id_item = (call.data).split("_")[-1]
            file_history = open(f"{id_item}_history.txt","r").read()
            file_history_data = json.loads(file_history)
            file_history_count = file_history_data['last_count']
            file_history_count_new = file_history_data['last_count']+1
            file_history_data['last_count']=file_history_count_new
            history_file = open(f"{call.from_user.id}_history.txt", "w")
            history_file.write(json.dumps(file_history_data))
            history_file.close()
            new_item_start_char = "\n"
            markup_rep = InlineKeyboardMarkup()
            if(file_history_count_new <= len(file_history_data['ids'])):
                markup_rep.add(
                    InlineKeyboardButton(f"+ (след. страница)", callback_data=f"next_{call.message.chat.id}"))
            markup_rep.add(
                InlineKeyboardButton(f"- (пред. страница)", callback_data=f"back_{call.message.chat.id}"))
            bot.send_message(chat_id=call.message.chat.id,
                             text= f"Для нового поиска просто напишите название отеля\n\n"
                                   f"------------ {int(file_history_count_new)+1} запись ------------\n"
                                      f"Дата: {get_item(file_history_data['ids'][int(file_history_count_new)]).date_time}\n"
                                      f"Данные:\n{(new_item_start_char).join(urllib.parse.unquote(get_item(file_history_data['ids'][int(int(file_history_count_new)+1)]).url_parameters).split('&')).replace('=',': ')}\n"
                                      f"Страница: {get_item(file_history_data['ids'][int(int(file_history_count_new)+1)]).page_url}",
                             reply_markup=markup_rep)
    if "back" in call.data:
            id_item = (call.data).split("_")[-1]
            file_history = open(f"{id_item}_history.txt","r").read()
            file_history_data = json.loads(file_history)
            file_history_count = file_history_data['last_count']
            if not file_history_count-1<0:
                file_history_count_new = file_history_count - 1
            file_history_data['last_count']=file_history_count_new
            history_file = open(f"{call.from_user.id}_history.txt", "w")
            history_file.write(json.dumps(file_history_data))
            history_file.close()
            new_item_start_char = "\n"
            markup_rep = InlineKeyboardMarkup()
            markup_rep.add(
                InlineKeyboardButton(f"+ (след. страница)", callback_data=f"next_{call.message.chat.id}"))
            if(file_history_count_new > 0):
                markup_rep.add(
                    InlineKeyboardButton(f"- (пред. страница)", callback_data=f"back_{call.message.chat.id}"))


            bot.send_message(chat_id=call.message.chat.id,
                             text= f"Для нового поиска просто напишите название отеля\n\n"
                                   f"------------ {int(file_history_count_new)+1} запись ------------\n"
                                      f"Дата: {get_item(file_history_data['ids'][int(file_history_count_new)]).date_time}\n"
                                      f"Данные:\n{(new_item_start_char).join(urllib.parse.unquote(get_item(file_history_data['ids'][int(file_history_count_new)]).url_parameters).split('&')).replace('=',': ')}\n"
                                      f"Страница: {get_item(file_history_data['ids'][int(int(file_history_count)+1)]).page_url}",
                             reply_markup=markup_rep)





if __name__ == "__main__":
    bot.polling()