import flet as ft
import sqlite3
import bkn_fn
# Constants
TEXT_SIZE = 14
FIELD_HEIGHT = 40


def containers(page):
    page.fonts = bkn_fn.pagefonts
    # Fetch initial data from database
    course_data = bkn_fn.Exec_Sql("SELECT * FROM Course ORDER BY ID DESC")
    
    # State variables
    editing_index = None
    filtered_data = course_data.copy()  # For filtering
    table = None  # Define table as a nonlocal variable

    # Define refresh_table
    def refresh_table():
        nonlocal table

        table = build_table()  # Update table
        table_container.content = table
        page.update()

    # Toggle Add Container visibility
    def toggle_add_container(e):
        add_button.visible = False
        add_container.visible = True
        page.update()

    def hide_add_container(e):
        add_button.visible = True
        add_container.visible = False
        page.update()

    # Add new record function
    def save_new_record(e):
        nonlocal editing_index
        max_id_result = bkn_fn.Exec_Sql("SELECT MAX(ID) as max_id FROM Course")
        max_id = max_id_result[0]["max_id"] if max_id_result and max_id_result[0]["max_id"] is not None else 0
        new_id = str(max_id + 1)
        
        new_record = {
            "ID": new_id,
            "C_ID": c_id_field.value,
            "Class": class_field.value,
            "Day": day_field.value,
            "Period": period_field.value,
            "Subject": subject_field.value,
            "Cost": cost_field.value,
        }
        sql = f"INSERT INTO Course (ID, C_ID, Class, Day, Period, Subject, Cost) VALUES ('{new_id}', '{new_record['C_ID']}', '{new_record['Class']}', '{new_record['Day']}', '{new_record['Period']}', '{new_record['Subject']}', '{new_record['Cost']}')"
        bkn_fn.Exec_Sql(sql)
        
        course_data.insert(0, new_record)
        filtered_data.insert(0, new_record)
        c_id_field.value = ""
        class_field.value = ""
        day_field.value = ""
        period_field.value = ""
        subject_field.value = ""
        cost_field.value = ""
        hide_add_container(e)
        refresh_table()

    # Filter function
    def filter_records(e):
        nonlocal filtered_data
        filter_text = filter_field.value.lower()
        if filter_text:
            filtered_data = [
                item for item in course_data
                if filter_text in item["C_ID"].lower() or filter_text in item["Class"].lower()
            ]
        else:
            filtered_data = course_data.copy()
        refresh_table()

    # Edit, Delete, Duplicate functions
    def edit_record(e, index):
        nonlocal editing_index
        editing_index = index
        refresh_table()

    def save_edit_record(e, index):
        nonlocal editing_index, table
        filtered_data[index]["C_ID"] = table.rows[index].cells[0].content.value
        filtered_data[index]["Class"] = table.rows[index].cells[1].content.value
        filtered_data[index]["Day"] = table.rows[index].cells[2].content.value
        filtered_data[index]["Period"] = table.rows[index].cells[3].content.value
        filtered_data[index]["Subject"] = table.rows[index].cells[4].content.value
        filtered_data[index]["Cost"] = table.rows[index].cells[5].content.value
        sql = f"UPDATE Course SET C_ID = '{filtered_data[index]['C_ID']}', Class = '{filtered_data[index]['Class']}', Day = '{filtered_data[index]['Day']}', Period = '{filtered_data[index]['Period']}', Subject = '{filtered_data[index]['Subject']}', Cost = '{filtered_data[index]['Cost']}' WHERE ID = '{filtered_data[index]['ID']}'"
        bkn_fn.Exec_Sql(sql)
        for i, item in enumerate(course_data):
            if item["ID"] == filtered_data[index]["ID"]:
                course_data[i] = filtered_data[index].copy()
                break
        editing_index = None
        refresh_table()

    def delete_record(e, index):
        deleted_item = filtered_data.pop(index)
        sql = f"DELETE FROM Course WHERE ID = '{deleted_item['ID']}'"
        bkn_fn.Exec_Sql(sql)
        course_data[:] = [item for item in course_data if item["ID"] != deleted_item["ID"]]
        refresh_table()

    def duplicate_record(e, index):
        max_id_result = bkn_fn.Exec_Sql("SELECT MAX(ID) as max_id FROM Course")
        max_id = max_id_result[0]["max_id"] if max_id_result and max_id_result[0]["max_id"] is not None else 0
        new_id = str(max_id + 1)
        
        new_record = filtered_data[index].copy()
        new_record["ID"] = new_id
        new_record["C_ID"] = f"{new_record['C_ID']}_COPY"
        sql = f"INSERT INTO Course (ID, C_ID, Class, Day, Period, Subject, Cost) VALUES ('{new_id}', '{new_record['C_ID']}', '{new_record['Class']}', '{new_record['Day']}', '{new_record['Period']}', '{new_record['Subject']}', '{new_record['Cost']}')"
        bkn_fn.Exec_Sql(sql)
        
        course_data.insert(0, new_record)
        filtered_data.insert(0, new_record)
        refresh_table()

    # Build the table
    def build_table():
        nonlocal editing_index
        return ft.DataTable(
            column_spacing=5,
            columns=[
                ft.DataColumn(ft.Text("รหัส", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("ห้องเรียน", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("วันเรียน", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("ช่วงเวลา", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("วิชา", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("จำนวนเงิน", size=TEXT_SIZE)),
                ft.DataColumn(ft.Row([ft.Text("    ", size=TEXT_SIZE),ft.Text("Actions", size=TEXT_SIZE,text_align=ft.TextAlign.CENTER)])),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.TextField(value=item["C_ID"], text_size=TEXT_SIZE, height=FIELD_HEIGHT) if i == editing_index else ft.Text(item["C_ID"], size=TEXT_SIZE)),
                        ft.DataCell(ft.TextField(value=item["Class"], text_size=TEXT_SIZE, height=FIELD_HEIGHT) if i == editing_index else ft.Text(item["Class"], size=TEXT_SIZE)),
                        ft.DataCell(ft.TextField(value=item["Day"], text_size=TEXT_SIZE, height=FIELD_HEIGHT) if i == editing_index else ft.Text(item["Day"], size=TEXT_SIZE)),
                        ft.DataCell(ft.TextField(value=item["Period"], text_size=TEXT_SIZE, height=FIELD_HEIGHT) if i == editing_index else ft.Text(item["Period"], size=TEXT_SIZE)),
                        ft.DataCell(ft.TextField(value=item["Subject"], text_size=TEXT_SIZE, height=FIELD_HEIGHT) if i == editing_index else ft.Text(item["Subject"], size=TEXT_SIZE)),
                        ft.DataCell(ft.TextField(value=item["Cost"], text_size=TEXT_SIZE, height=FIELD_HEIGHT) if i == editing_index else ft.Text(item["Cost"], size=TEXT_SIZE)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.SAVE if i == editing_index else ft.Icons.EDIT,
                                        on_click=lambda e, idx=i: save_edit_record(e, idx) if idx == editing_index else edit_record(e, idx),
                                        icon_size=TEXT_SIZE,
                                        tooltip="Save" if i == editing_index else "Edit",
                                    ),
                                    ft.IconButton(
                                        ft.Icons.CONTENT_COPY,
                                        on_click=lambda e, idx=i: duplicate_record(e, idx),
                                        icon_size=TEXT_SIZE,
                                        tooltip="Duplicate"
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE,
                                        on_click=lambda e, idx=i: delete_record(e, idx),
                                        icon_size=TEXT_SIZE,
                                        tooltip="Delete",
                                        icon_color="red"
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                ) for i, item in enumerate(filtered_data)
            ],
        )

    # Add new course fields with labels
    c_id_field = ft.TextField(label="C_ID", text_size=TEXT_SIZE, height=FIELD_HEIGHT, expand= True)
    class_field = ft.TextField(label="Class", text_size=TEXT_SIZE, height=FIELD_HEIGHT, expand= True)
    day_field = ft.TextField(label="Day", text_size=TEXT_SIZE, height=FIELD_HEIGHT, width=100)
    period_field = ft.TextField(label="Period", text_size=TEXT_SIZE, height=FIELD_HEIGHT, expand= True)
    subject_field = ft.TextField(label="Subject", text_size=TEXT_SIZE, height=FIELD_HEIGHT, expand= True)
    cost_field = ft.TextField(label="Cost", text_size=TEXT_SIZE, height=FIELD_HEIGHT, expand= True)

    # Add button and container
    add_button = ft.ElevatedButton("Add Course", on_click=toggle_add_container, bgcolor=bkn_fn.navy_blue,icon=ft.Icons.ADD ,icon_color=bkn_fn.yellow, color=bkn_fn.yellow)
    add_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Add New Course", size=16),
                ft.Row(
                    [
                        c_id_field,
                        class_field,
                        day_field,
                    ],
                    spacing=10,
                ),
                ft.Row(
                    [
                        period_field,
                        subject_field,
                        cost_field,
                        ft.ElevatedButton("Save",icon=ft.Icons.SAVE,width=100,icon_color=bkn_fn.yellow , on_click=save_new_record, bgcolor=bkn_fn.navy_blue, color=bkn_fn.yellow),
                    ],
                    spacing=10,
                ),
            ],
            spacing=5,
        ),
        border=ft.border.all(1, "#E0E0E0"),
        padding=10,
        visible=False,
    )

    # Filter field with on_change filtering
    filter_field = ft.TextField(hint_text="Filter by C_ID or Class", text_size=TEXT_SIZE, height=FIELD_HEIGHT, width=200, on_change=filter_records)

    # Table container
    table_container = ft.Container(content=build_table(), expand=True)

    # Main container layout

    return ft.Column(controls=[
        ft.Container(
            margin=ft.margin.only(10,0,10,0),
            border_radius=15,
            bgcolor=bkn_fn.grey,
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=bkn_fn.navy_blue,
                        height=40,
                        content=ft.Row(
                        [ft.Text("::: การจัดการคอร์สเรียน :::", color=bkn_fn.yellow, size=22,font_family=bkn_fn.menu_font)],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ),
                    add_button,
                    add_container,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                
            ),
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=bkn_fn.yellow,
                        height=40,
                        content=ft.Row(
                        [ft.Text("::: ข้อมูลคอร์สเรียน :::", color=bkn_fn.navy_blue, size=22,font_family=bkn_fn.menu_font)],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ),
                    ft.Row([filter_field], spacing=10),

                    ft.Column([table_container], scroll="auto", height=300) ,

                    
                    ft.Text(f"     Showing 1-{len(filtered_data)} of {len(course_data)} records", size=12, color="#757575"),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.only(0,0,0,10),
            margin=ft.margin.only(10,0,10,0),
            border_radius=15,
            bgcolor=bkn_fn.grey,
        )
    ])

def main(page: ft.Page):
    page.title = "Course Management"
    page.bgcolor = "#F5F5F5"
    page.add(containers(page))

if __name__ == "__main__":
    ft.app(target=main)