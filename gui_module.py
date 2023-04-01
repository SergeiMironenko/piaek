import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from program import alg_fedorova
from program import save_plan_plot
import threading
import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


dpg.create_context()
dpg.create_viewport(title='Var15', width=1000, height=600)


stop_global = False
log_data = ''
plan = []
plan0 = []


# Размер изображения с графиком. По умолчанию черная картинка.
plot_width = 640
plot_height = 480
plot_channels = 4
data = [0] * plot_width * plot_height * plot_channels


# Динамическая текстура графика
with dpg.texture_registry(show=False):
    dpg.add_dynamic_texture(width=640, height=480, default_value=data, tag="opt_plan_texture")
    dpg.add_dynamic_texture(width=640, height=480, default_value=data, tag="start_plan_texture")


# Пользовательский шрифт (joystix, basis33, bedstead, basica)
with dpg.font_registry():
    with dpg.font(tag='custom_font', file=resource_path('fonts/anonymous_pro.ttf'), size=20):
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font('custom_font')


# Тема неактивной кнопки
with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvButton, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 50, 50])
        dpg.add_theme_color(dpg.mvThemeCol_Button, [80, 80, 80])


# Установка неактивной темы
def set_disabled_theme(sender):
    dpg.configure_item(sender, enabled=False)


# Установка активной темы
def set_enabled_theme(sender):
    dpg.configure_item(sender, enabled=True)


# Начало алгоритма
def start_algorithm(sender, app_data, user_data):
    set_disabled_theme('show_plot')
    set_disabled_theme(sender)
    threads = [threading.Thread(target=thread_task)]
    threads[0].start()


# Выполнение алгоритма Федорова в отдельном потоке
def thread_task():
    global stop_global, log_data, plan, plan0
    g = alg_fedorova(N=int(dpg.get_value('N')), delta_big=float(dpg.get_value('delta')))
    log_data = ''
    plan0 = []
    plan = []
    continue_while = True
    while not stop_global and continue_while:
        try:
            val = next(g)
            if isinstance(val, str):
                log_data += f'{val}'
                dpg.set_value('text', log_data)
            else:
                plan0, plan = val[0], val[1]
        except StopIteration:
            continue_while = False
    stop_global = False
    set_enabled_theme('start_btn')
    set_enabled_theme('show_plot')
    print('end task')


# Остановить алгоритм, не дожидаясь окончания
def stop_algorithm(sender, app_data, user_data):
    global stop_global
    if not stop_global:
        stop_global = True
    set_enabled_theme('start_btn')


# Показать график без сохранения
def show_plot():
    global plan0, plan
    if len(plan) != 0 and len(plan0) != 0:
        plot_path = save_plan_plot(plan, 21, dpg.get_value('N'), 'optimal_tmp')
        width, height, channels, data = dpg.load_image(plot_path)
        os.remove(plot_path)
        dpg.set_value('opt_plan_texture', data)

        plot0_path = save_plan_plot(plan0, 21, dpg.get_value('N'), 'start_tmp')
        width, height, channels, data = dpg.load_image(plot0_path)
        os.remove(plot0_path)
        dpg.set_value('start_plan_texture', data)

        plot_state = dpg.get_item_configuration('plot')['show']
        dpg.configure_item('plot', show=not plot_state)


# Сохранить график в png
def save_plot():
    global plan0, plan
    if len(plan) != 0 and len(plan0) != 0:
        save_plan_plot(plan0, 21, dpg.get_value('N'), 'start')
        save_plan_plot(plan, 21, dpg.get_value('N'), 'optimal')


# Сохранить данные в файлик txt
def save_data():
    global log_data, plan, plan0
    with open('log.txt', 'w+') as f:
        f.write(log_data)
    with open('points0.txt', 'w+') as f2:
        for item in plan0[0]:
            f2.write(f'x = ({item[0]:+.4f}, {item[1]:+.4f})\n')
    with open('points.txt', 'w+') as f3:
        for item in plan[0]:
            f3.write(f'x = ({item[0]:+.4f}, {item[1]:+.4f})\n')


with dpg.window(label='Mywindow', tag="primary_window"):
    with dpg.menu_bar():
        with dpg.menu(label='Данные'):
            dpg.add_menu_item(label='Сохранить данные', callback=save_data)
            dpg.add_menu_item(label='Сохранить графики', callback=save_plot)
    with dpg.group(horizontal=True, horizontal_spacing=50):
        dpg.add_combo(tag='N', label='N', items=('20', '30', '40'), width=80, default_value='20')
        dpg.add_combo(tag='delta', label='delta', items=('0.5', '0.4', '0.3', '0.2'), width=80, default_value='0.2')
        dpg.add_button(tag='start_btn', label='Начать', callback=start_algorithm, enabled=True)
        dpg.add_button(tag='stop_btn', label='Остановить', callback=stop_algorithm, enabled=True)
        dpg.add_button(tag='show_plot', label='Показать/скрыть график', callback=show_plot, enabled=False)
    with dpg.child_window(menubar=False):
        dpg.add_collapsing_header(leaf=True, label="Вывод")
        dpg.add_menu_bar()
        dpg.add_text(tag='text', default_value='')
    with dpg.window(tag='plot', show=False, no_collapse=True, label='Графики'):
        with dpg.tab_bar():
            with dpg.tab(label="График начального плана"):
                dpg.add_image("start_plan_texture")
            with dpg.tab(label="График оптимального плана"):
                dpg.add_image("opt_plan_texture")


dpg.bind_item_theme('start_btn', disabled_theme)
dpg.bind_item_theme('show_plot', disabled_theme)
# demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("primary_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
