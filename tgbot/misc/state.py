from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup


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
    select_technique_confirm = State()
    select_spell = State()
    select_spell_confirm = State()
    user_escape_confirm = State()
    user_pass_confirm = State()
    battle_start = State()
    revival = State()
    load = State()
    end = State()


class CharacterState(StatesGroup):
    train = State()
    equip = State()
    inventory = State()
    inventory_items = State()
    inventory_action = State()
    skills = State()
    skill_fix = State()
    techniques = State()
    technique_fix = State()
    spells = State()
    spell_fix = State()
    distribution = State()
    distribution_menu = State()
    all_stats = State()
    flat_stats = State()

    info_menu = State()


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
    fortress = State()
    arena = State()
    team = State()


class TowerState(StatesGroup):
    arena = State()
    select_enemy = State()
    select_floor = State()


class CampusState(StatesGroup):
    select_floor = State()
    select_enemy = State()


class FortressState(StatesGroup):
    map_nav = State()
    select_floor = State()
    select_enemy = State()
    town = State()
    battle = State()
    battle_exit = State()


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
