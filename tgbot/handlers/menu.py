#
# # def register_start(dp: Dispatcher, db: Pool):
# # register_user_db = partial(register_user, db=db)
# # register_greeting_db = partial(register_greeting, db=db)
#
# # dp.register_message_handler(register_greeting_db, _commands=["start"], state="*")
# dp.register_message_handler(register_user_db, state=RegState.user_name)
