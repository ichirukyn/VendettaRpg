from aiogram.dispatcher.filters.state import StatesGroup, State


class RegState(StatesGroup):
    user_name = State()
    select_race = State()
    select_race_confirm = State()

    select_class = State()
    select_class_confirm = State()
    entry = State()


class BattleState(StatesGroup):
    battle = State()
    user_turn = State()
    user_sub_turn = State()
    select_target = State()
    select_technique = State()
    select_skill = State()
    select_skill_confirm = State()
    user_escape_confirm = State()
    battle_start = State()
    revival = State()
    load = State()


class HuntState(StatesGroup):
    select_location = State()
    hunter_diary = State()
    hunting = State()
    hunting_action = State()


class CharacterState(StatesGroup):
    train = State()
    equip = State()
    inventory = State()
    inventory_items = State()
    inventory_action = State()
    skills = State()
    skill_fix = State()
    distribution = State()
    distribution_menu = State()


class EquipState(StatesGroup):
    weapon = State()
    inventory = State()


class ShopState(StatesGroup):
    # items = State()
    buy = State()


class LocationState(StatesGroup):
    home = State()
    select_enemy = State()
    character = State()
    store = State()
    top = State()

    town = State()
    tower = State()
    hunt = State()
    arena = State()
    team = State()


class TowerState(StatesGroup):
    arena = State()
    select_enemy = State()
    select_floor = State()


class ArenaState(StatesGroup):
    select_type = State()
    team_battle = State()
    solo_battle = State()
    accept_invite = State()


class TeamState(StatesGroup):
    main = State()

    add = State()
    add_name = State()
    add_private = State()

    team_list = State()
    send_invite = State()  # Проверка на то, есть ли игрок в группе, мало ли 3 заявки подряд отправил..
    accept_invite = State()
    accept_leader = State()  # URL

    change_name = State()
    change_leader = State()
    change_private = State()
    team_delete = State()

    change_confirm = State()

    select_target = State()

    teammate_list = State()
    teammate_menu = State()

    kik = State()
    kik_confirm = State()

    out = State()
    out_confirm = State()


class AdminState(StatesGroup):
    main = State()
    hero_stats = State()
    hero_inventory = State()
    hero_id = State()
    value = State()
    bd_set = State()
