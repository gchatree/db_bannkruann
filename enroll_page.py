import flet as ft
import sqlite3
import json
import student_page
import bkn_fn
import payment_page

def containers(page,cur_stu_id):

    page.fonts = bkn_fn.pagefonts
    # Define color scheme
    navy_blue = bkn_fn.navy_blue
    yellow = bkn_fn.yellow
    grey = bkn_fn.grey
    white = "#FFFFFF"


    # Constants for text size and field height
    txt_size = 13
    field_height = 40

    # Fetch student and course data
    student_sql = "SELECT S_ID, Name, SurName, Nick FROM Student ORDER BY S_ID DESC"
    student_data = bkn_fn.Exec_Sql(student_sql)
    last_student = student_data
    if cur_stu_id[0] == 1 :
        last_student = bkn_fn.max_id(student_data, "S_ID") if student_data else None
    else :
        sql = f'SELECT S_ID, Name, SurName, Nick FROM Student WHERE S_ID = "{cur_stu_id[0]}"'
        result_sql = bkn_fn.Exec_Sql(sql)
        last_student = result_sql[0]

    course_sql = "SELECT C_ID, Class, Day, Period, Subject, Cost FROM Course ORDER BY C_ID"
    course_data = bkn_fn.Exec_Sql(course_sql)
    filtered_course_data = course_data.copy()

    # UI elements for student info
    student_id_text = ft.Text(
        str(last_student["S_ID"]) if last_student else "1234", color=navy_blue, size=txt_size
    )
    name_text = ft.Text(
        last_student["Name"] if last_student else "เด็กชาย", color=navy_blue, size=txt_size
    )
    surname_text = ft.Text(
        last_student["SurName"] if last_student else "นามสกุล", color=navy_blue, size=txt_size
    )
    nickname_text = ft.Text(
        last_student["Nick"] if last_student else "ชื่อเล่น", color=navy_blue, size=txt_size
    )

    # Search functionality
    search_input = ft.TextField(
        label="ค้นหา: ชื่อ นามสกุล หรือ ชื่อเล่น", bgcolor=white, visible=False,
        on_change=lambda e: update_search_results(e.control.value)
    )
    search_results = ft.Column(visible=False, scroll="auto", height=150)


    # Dropdowns for filtering
    class_options = sorted(list(set(course["Class"] for course in course_data if course["Class"])))
    day_options = sorted(list(set(course["Day"] for course in course_data if course["Day"])))
    class_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("ทั้งหมด")] + [ft.dropdown.Option(opt) for opt in class_options],
        bgcolor=white, expand=True, width=250, label="ห้องเรียน", value="ทั้งหมด",
        on_change=lambda e: filter_courses()
    )
    day_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("ทั้งหมด")] + [ft.dropdown.Option(opt) for opt in day_options],
        bgcolor=white, expand=True, width=250, label="วันเรียน", value="ทั้งหมด",
        on_change=lambda e: filter_courses()
    )

    # Course table
    course_table = ft.ListView(
        controls=[ft.DataTable(
            column_spacing=5,
            columns=[
                ft.DataColumn(ft.Checkbox(value=False, on_change=lambda e: toggle_all_selections(e))),
                ft.DataColumn(ft.Text("รหัสคอร์ส", size=txt_size)),
                ft.DataColumn(ft.Text("ห้องเรียน", size=txt_size)),
                ft.DataColumn(ft.Text("วัน", size=txt_size)),
                ft.DataColumn(ft.Text("ช่วงเวลา", size=txt_size)),
                ft.DataColumn(ft.Text("วิชา", size=txt_size)),
                ft.DataColumn(ft.Text("ราคา", size=txt_size)),
            ],
            rows=[]
        )],
        expand=True, height=240, auto_scroll=False
    )

    # Text fields to update
    selected_courses_info = ft.TextField(
        label="ข้อมูลสรุปการเลือก", text_size=txt_size, height=field_height, expand=True
    )
    total_cost = ft.TextField(
        label="Total Cost", text_size=txt_size, height=field_height, expand=False, width=250
    )
    discounted_total = ft.TextField(
        label="Discounted Total Cost", text_size=txt_size, height=field_height, width=250
    )
    discount_radio_group = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="5", label="5%"),
            ft.Radio(value="10", label="10%"),
            ft.Radio(value="15", label="15%"),
            ft.Radio(value="other", label="อื่น"),
        ], spacing=0),
        on_change=lambda e: apply_discount()
    )
    other_discount = ft.TextField(
        expand=1, label="ระบุส่วนลด (บาท)", on_change=lambda e: apply_discount(),
        visible=False, text_size=txt_size, height=field_height
    )
    extranote = ft.TextField(
        expand=True, label="บันทึกเพิ่มเติม", text_size=txt_size, height=field_height
    )
    selected_cid = ft.TextField(
        text_size=txt_size, height=field_height, visible=False, expand=True
    )

    # Track selected courses
    selected_course_ids = set()
    enroll_data = bkn_fn.Exec_Sql("SELECT * FROM Enroll")

    # Helper functions
    def toggle_search_panel():
        search_input.visible = not search_input.visible
        search_results.visible = not search_results.visible
        if search_input.visible:
            search_input.value = ""
            update_search_results("")
        else:
            search_results.controls.clear()
        page.update()

    def update_search_results(search_text):
        search_results.controls.clear()
        if not student_data:
            search_results.controls.append(ft.Text("ไม่มีข้อมูลนักเรียนในฐานข้อมูล"))
        else:
            filtered_students = [
                s for s in student_data
                if (search_text.lower() in str(s["Name"]).lower() or
                    search_text.lower() in str(s["SurName"]).lower() or
                    search_text.lower() in str(s["Nick"]).lower())
            ]
            if not filtered_students:
                search_results.controls.append(ft.Text("ไม่พบนักเรียนที่ตรงกับการค้นหา"))
            else:
                for student in filtered_students:
                    search_results.controls.append(
                        ft.TextButton(
                            text=f"{student['Name']} {student['SurName']} ({student['Nick']}) - ID: {student['S_ID']}",
                            on_click=lambda e, s_id=student["S_ID"]: select_student(s_id)
                        )
                    )
        page.update()

    def select_student(s_id):
        cur_stu_id[0]=s_id
        selected_student = next((s for s in student_data if s["S_ID"] == s_id), None)
        if selected_student:
            student_id_text.value = str(selected_student["S_ID"])
            name_text.value = selected_student["Name"]
            surname_text.value = selected_student["SurName"]
            nickname_text.value = selected_student["Nick"]
        search_input.visible = False
        search_results.visible = False
        search_results.controls.clear()
        page.update()

    def update_selection(e, cid):
        if e.control.value:
            selected_course_ids.add(cid)
        elif cid in selected_course_ids:
            selected_course_ids.remove(cid)
        update_header_checkbox()
        update_selected_courses()
        page.update()

    def toggle_all_selections(e):
        nonlocal filtered_course_data
        filtered_cids = {course["C_ID"] for course in filtered_course_data}
        if e.control.value:
            selected_course_ids.update(filtered_cids)
        else:
            selected_course_ids.difference_update(filtered_cids)
        filter_courses()
        update_selected_courses()

    def update_header_checkbox():
        filtered_cids = {course["C_ID"] for course in filtered_course_data}
        all_selected = filtered_cids and filtered_cids.issubset(selected_course_ids)
        course_table.controls[0].columns[0].label.value = all_selected
        page.update()

    def filter_courses():
        nonlocal filtered_course_data
        selected_class = class_dropdown.value
        selected_day = day_dropdown.value
        filtered_course_data = course_data.copy()
        if selected_class != "ทั้งหมด":
            filtered_course_data = [course for course in filtered_course_data if course["Class"] == selected_class]
        if selected_day != "ทั้งหมด":
            filtered_course_data = [course for course in filtered_course_data if course["Day"] == selected_day]
        course_table.controls[0].rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Checkbox(
                    value=course["C_ID"] in selected_course_ids,
                    on_change=lambda e, cid=course["C_ID"]: update_selection(e, cid)
                )),
                ft.DataCell(ft.Text(course["C_ID"], size=txt_size)),
                ft.DataCell(ft.Text(course["Class"], size=txt_size)),
                ft.DataCell(ft.Text(course["Day"], size=txt_size)),
                ft.DataCell(ft.Text(course["Period"], size=txt_size)),
                ft.DataCell(ft.Text(course["Subject"], size=txt_size)),
                ft.DataCell(ft.Text(str(course["Cost"]), size=txt_size)),
            ]) for course in filtered_course_data
        ]
        if course_table.page is not None:
            course_table.scroll_to(offset=0, duration=0)
        update_header_checkbox()

    def update_selected_courses():
        selected_courses = [course for course in course_data if course["C_ID"] in selected_course_ids]
        total_cost.value = str(sum(int(course["Cost"]) for course in selected_courses)) if selected_courses else "0"
        discounted_total.value = total_cost.value  # Reset discounted total to total cost initially
        if not selected_courses:
            discount_radio_group.value = None
            other_discount.visible = False
        # Generate selected_cid for database insertion
        if selected_courses:
            i = int(bkn_fn.max_id(enroll_data, 'ID')['ID']) + 1 if enroll_data else 1
            selected_cid.value = ",".join(f"('{i + index}', '{student_id_text.value}', '{course['C_ID']}')" 
                                        for index, course in enumerate(selected_courses))
        else:
            selected_cid.value = ""
        formatted_course_info = format_subjects([
            f'"ห้อง": "{course["Class"]}", "รอบวัน": "{course["Day"]}", "วิชา": "{course["Subject"]}"'
            for course in selected_courses
        ])
        selected_courses_info.value = formatted_course_info if formatted_course_info else ""
        apply_discount()
        page.update()

    def format_subjects(subjects):
        data = {}
        for subject in subjects:
            subject_dict = json.loads(f'{{{subject}}}')
            room = subject_dict["ห้อง"]
            day = subject_dict["รอบวัน"]
            subject_name = subject_dict["วิชา"]
            if room not in data:
                data[room] = {}
            if day not in data[room]:
                data[room][day] = []
            if subject_name not in data[room][day]:
                data[room][day].append(subject_name)
        result = ""
        for room in sorted(data.keys()):
            room_text = f'ห้อง {room} '
            for day in sorted(data[room].keys()):
                subjects = "-".join(data[room][day])
                day_text = f'รอบวัน {day} วิชา {subjects} : '
                result += room_text + day_text
                room_text = ""
        return result.strip(" :")

    def apply_discount():
        total = float(total_cost.value) if total_cost.value else 0
        discount_value = 0
        if discount_radio_group.value == "other":
            other_discount.visible = True
            discount_value = float(other_discount.value) if other_discount.value else 0
            discounted_total.value = str(int(total - discount_value))
        else:
            other_discount.visible = False
            discount_value = float(discount_radio_group.value) if discount_radio_group.value else 0
            discounted_total.value = str(int(total - (total * discount_value / 100)))
        page.update()

    def save_to_database(e):
        if selected_cid.value:
            
            sql_enroll = f"INSERT INTO Enroll (ID, S_ID, C_ID) VALUES {selected_cid.value}"
            bkn_fn.Exec_Sql(sql_enroll)
            
            max_payment_id = int(bkn_fn.max_id(bkn_fn.Exec_Sql("SELECT ID FROM Payment"), "ID")["ID"]) + 1 if bkn_fn.Exec_Sql("SELECT ID FROM Payment") else 1
            sql_payment = f"INSERT INTO Payment (ID, S_ID, Total, RNote, Pay1, Paid_Date1, Receipt1, Pay2, Paid_Date2, Receipt2, Pay3, Paid_Date3, Receipt3, Pay4, Paid_Date4, Receipt4) VALUES ('{max_payment_id}', '{student_id_text.value}', '{discounted_total.value}', '{selected_courses_info.value}^{extranote.value}', '0', '0000-00-00', '0', '0', '0000-00-00', '0', '0', '0000-00-00', '0', '0', '0000-00-00', '0')"
            bkn_fn.Exec_Sql(sql_payment)

            go_student_page()

    def payment_to_database(e):
        if selected_cid.value:
            # Insert into Enroll table
            sql_enroll = f"INSERT INTO Enroll (ID, S_ID, C_ID) VALUES {selected_cid.value}"
            bkn_fn.Exec_Sql(sql_enroll)
            # Insert into Payment table
            max_payment_id = int(bkn_fn.max_id(bkn_fn.Exec_Sql("SELECT ID FROM Payment"), "ID")["ID"]) + 1 if bkn_fn.Exec_Sql("SELECT ID FROM Payment") else 1
            sql_payment = f"INSERT INTO Payment (ID, S_ID, Total, RNote, Pay1, Paid_Date1, Receipt1, Pay2, Paid_Date2, Receipt2, Pay3, Paid_Date3, Receipt3, Pay4, Paid_Date4, Receipt4) VALUES ('{max_payment_id}', '{student_id_text.value}', '{discounted_total.value}', '{selected_courses_info.value}^{extranote.value}', '0', '0000-00-00', '0', '0', '0000-00-00', '0', '0', '0000-00-00', '0', '0', '0000-00-00', '0')"
            bkn_fn.Exec_Sql(sql_payment)
            go_payment_page()

    def go_student_page():
        page.controls[0].controls[2].content = student_page.containers(page)
        page.controls[0].controls[0].content.controls[4].bgcolor = bkn_fn.navy_blue
        page.controls[0].controls[0].content.controls[2].bgcolor = bkn_fn.yellow
        page.controls[0].controls[0].content.controls[4].content.controls[1].color = bkn_fn.yellow
        page.controls[0].controls[0].content.controls[2].content.controls[1].color = bkn_fn.navy_blue
        page.controls[0].controls[0].content.controls[4].content.controls[0].color = bkn_fn.yellow
        page.controls[0].controls[0].content.controls[2].content.controls[0].color = bkn_fn.navy_blue
        page.update()

    def go_payment_page():
        page.controls[0].controls[2].content = payment_page.containers(page)
        page.controls[0].controls[0].content.controls[4].bgcolor = bkn_fn.navy_blue
        page.controls[0].controls[0].content.controls[5].bgcolor = bkn_fn.yellow
        page.controls[0].controls[0].content.controls[4].content.controls[1].color = bkn_fn.yellow
        page.controls[0].controls[0].content.controls[5].content.controls[1].color = bkn_fn.navy_blue
        page.controls[0].controls[0].content.controls[4].content.controls[0].color = bkn_fn.yellow
        page.controls[0].controls[0].content.controls[5].content.controls[0].color = bkn_fn.navy_blue
        page.update()

    # Initial table population
    filter_courses()

    
    # Main UI layout
    ui = ft.Column(
        controls=[
            ft.Container(
                border_radius=15,
                margin=ft.margin.only(10, 0, 10, 0),
                content=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Container(
                            #height=40,
                            #padding=ft.padding.only(10, 10, 10, 10),
                            bgcolor=navy_blue,
                            content=ft.Column(
                                spacing=0,
                                controls=[ft.Row(
                                    [ft.Text(":::  เลือกคอร์ส  :::", color=yellow, size=22,font_family=bkn_fn.menu_font)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                )]
                            )
                        ),
                        ft.Container(
                            bgcolor=grey,
                            padding=ft.padding.only(10, 10, 10, 10),
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        [
                                            ft.Text("รหัสนักเรียน :", color=navy_blue, size=txt_size),
                                            student_id_text,
                                            ft.Text("ชื่อ :", color=navy_blue, size=txt_size),
                                            name_text,
                                            ft.Text("", color=navy_blue, size=txt_size),
                                            surname_text,
                                            ft.Text("(", color=navy_blue, size=txt_size),
                                            nickname_text,
                                            ft.Text(")", color=navy_blue, size=txt_size),
                                            ft.IconButton(icon="SEARCH", on_click=lambda e: toggle_search_panel())
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    search_input,
                                    search_results,
                                    ft.Row([class_dropdown, day_dropdown]),
                                    course_table,
                                    ft.Row([selected_courses_info, selected_cid])
                                ]
                            )
                        )
                    ]
                )
            ),
            ft.Container(
                border_radius=15,
                margin=ft.margin.only(10, 0, 10, 0),
                bgcolor=grey,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor=yellow,
                            # height=40,
                            # padding=ft.padding.only(10, 0, 10, 10),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[ft.Row(
                                    [ft.Text(":::: ข้อมูลการชำระเงิน ::::", expand=True, size=22,font_family=bkn_fn.menu_font, text_align="center")]
                                )]
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.only(10, 0, 10, 10),
                            content=ft.Column(
                                controls=[
                                    ft.Row([total_cost, discount_radio_group, other_discount]),
                                    ft.Row([discounted_total, extranote]),
                                    ft.Row([
                                        ft.Row([ft.ElevatedButton(
                                            on_click=save_to_database, icon="SAVE", text="Save", width=150,
                                            color=yellow, bgcolor=navy_blue, icon_color=yellow
                                        )]),
                                        ft.Row([ft.ElevatedButton(
                                            on_click=payment_to_database, icon="CREDIT_CARD", text="Payment", width=150,
                                            icon_color=yellow, color=yellow, bgcolor=navy_blue
                                        )]),
                                    ], alignment=ft.MainAxisAlignment.END)
                                ]
                            )
                        )
                    ]
                )
            )
        ]
    )

    return ui

# Main function to set up the page
def main(page: ft.Page):
    page.title = "Course Enrollment"
    ui = containers(page)
    page.window.height = 700
    page.add(ui)
    ui.controls[0].content.controls[1].content.controls[4].scroll_to(offset=0, duration=0)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)