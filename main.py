import flet as ft 
from db import main_db


def main(page: ft.Page):
    page.title = 'todo list'
    page.theme_mode = ft.ThemeMode.LIGHT
    task_list = ft.Column(spacing=15)
    error_text = ft.Text(value='Можно вводить максимум 100 символов!', color=ft.Colors.RED, visible=False)

    filter_type = 'all'

    def load_task():
        task_list.controls.clear()
        for task_id, task_text, completed in main_db.get_task(filter_type):
            task_list.controls.append(create_task_row(task_id=task_id, task_text=task_text, completed=completed))
        page.update()

    def create_task_row(task_id, task_text, completed):

        checkbox = ft.Checkbox(value=bool(completed), on_change=lambda e: toggle_task(task_id, e.control.value))

        def enable_edit(_):
            task_field.read_only = False
            task_field.update()

        edit_button = ft.IconButton(icon=ft.Icons.EDIT, on_click=enable_edit)

        def save_task(_):
            main_db.update_task(task_id=task_id, new_task=task_field.value)
            task_field.read_only = True
            task_field.update()

        save_button = ft.IconButton(icon=ft.Icons.SAVE_ALT_ROUNDED, on_click=save_task)

        def delete_task(_):
            main_db.delete_task(task_id=task_id)
            load_task()
            
        delete_button = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=delete_task)

        task_field = ft.TextField(value=task_text, read_only=True, expand=True, on_submit=save_task)

        return ft.Row([checkbox, task_field, edit_button, save_button, delete_button])
    
    def task_maximum(_):
        if len(task_input.value) >= 100:
            error_text.visible = True
        else:
            error_text.visible = False
        page.update()

    def toggle_task(task_id, is_completed):
        print(f'{task_id} - {is_completed}')
        main_db.update_task(task_id=task_id, completed=int(is_completed))
        load_task()

    def add_task(_):
        if task_input.value:
            task = task_input.value
            task_id = main_db.add_task(task)
            task_list.controls.append(create_task_row(task_id=task_id, task_text=task, completed=None))
            print(f'Запись сохранена! ID задачи - {task_id}')
            task_input.value = None
            page.update()

    task_input = ft.TextField(label='Введите задачу', expand=True, max_length=100, on_change=task_maximum, on_submit=add_task)
    task_input_button = ft.IconButton(icon=ft.Icons.SEND, on_click=add_task)

    main_objects = ft.Row([task_input, task_input_button])

    def set_filter(filter_value):
        nonlocal filter_type
        filter_type = filter_value
        load_task()

    filter_buttons = ft.Row([
        ft.ElevatedButton('Все задачи', on_click=lambda e: set_filter('all'), icon=ft.Icons.ALL_INBOX, icon_color=ft.Colors.YELLOW),
        ft.ElevatedButton('Ожидают', on_click=lambda e: set_filter('uncompleted'), icon=ft.Icons.WATCH_LATER, icon_color=ft.Colors.RED),
        ft.ElevatedButton('Готово', on_click=lambda e: set_filter('completed'), icon=ft.Icons.CHECK_BOX, icon_color=ft.Colors.GREEN)
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    def delete_completed(_):
        main_db.delete_task()
        load_task()
    
    delete_button = ft.ElevatedButton('Очистить выполненные', icon=ft.Icons.DELETE_SWEEP, icon_color=ft.Colors.RED, on_click=delete_completed)

    page.add(main_objects, filter_buttons, error_text, task_list, delete_button)
    load_task()


if __name__ == '__main__':
    main_db.init_db()
    ft.app(target=main)