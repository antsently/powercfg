import ctypes
import sys
import subprocess
import re
from colorama import Fore, init

init(autoreset=True)

def is_admin():
    """Проверяем, запущен ли скрипт с правами администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_power_plans():
    """Получаем список всех доступных планов электропитания."""
    result = subprocess.run(['powercfg', '/LIST'], capture_output=True, text=True, encoding='cp866')
    plans = {}
    for line in result.stdout.splitlines():
        # Универсальный шаблон для GUID и названия плана
        match = re.search(r'GUID.*: ([\w-]+)\s+\((.+?)\)', line)
        if match:
            guid, name = match.groups()
            plans[name] = guid
    return plans

def get_active_power_plan():
    """Получаем текущий активный план электропитания."""
    result = subprocess.run(['powercfg', '/GETACTIVESCHEME'], capture_output=True, text=True, encoding='cp866')
    match = re.search(r'GUID.*: ([\w-]+)\s+\((.+?)\)', result.stdout)
    if match:
        return match.groups()
    return None

def set_power_plan(guid):
    """Устанавливаем выбранный план электропитания."""
    subprocess.run(['powercfg', '/S', guid])

def main():
    if not is_admin():
        print(Fore.RED + "Ошибка: Запустите скрипт от имени администратора.")
        sys.exit(1)

    plans = get_power_plans()
    active_plan = get_active_power_plan()

    print(Fore.CYAN + "Доступные планы электропитания:\n")
    for i, (name, guid) in enumerate(plans.items(), 1):
        status = " (Выбран)" if active_plan and active_plan[0] == guid else ""
        print(f"{i}. {name} - {Fore.YELLOW}{guid}{status}")

    print("\nВыберите номер плана для его активации:")

    try:
        choice = int(input("> "))
        if 1 <= choice <= len(plans):
            selected_plan = list(plans.items())[choice - 1]
            if active_plan and active_plan[0] == selected_plan[1]:
                print(Fore.RED + "Ошибка: Этот план уже активен!")
            else:
                set_power_plan(selected_plan[1])
                print(Fore.GREEN + f"План '{selected_plan[0]}' успешно активирован!")
        else:
            print(Fore.RED + "Некорректный выбор!")
    except ValueError:
        print(Fore.RED + "Ошибка: Введите числовое значение.")

    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        main()
