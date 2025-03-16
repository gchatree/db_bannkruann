import flet as ft
import sqlite3
import json
import os
import bkn_fn



class AddressManager:
    def __init__(self, filepath="./assets/data/thailand_data.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    def get_provinces(self):
        return list(self.data.keys())
    
    def get_districts(self, province):
        return list(self.data.get(province, {}).keys())
    
    def get_subdistricts(self, province, district):
        return list(self.data.get(province, {}).get(district, {}).keys())
    
    def get_postal_code(self, province, district, subdistrict):
        return self.data.get(province, {}).get(district, {}).get(subdistrict, "")

def containers(page):
    # Define colors and styles
    navy_blue = bkn_fn.navy_blue
    yellow = bkn_fn.yellow
    grey = bkn_fn.grey
    white = "#FFFFFF"

    page.fonts = bkn_fn.pagefonts

    # Fetch initial data from the database
    student_sql = "SELECT * FROM Student as S, Parent as P WHERE S.P_ID = P.P_ID ORDER BY S.S_ID DESC"
    parent_sql = "SELECT * FROM Parent ORDER BY P_ID DESC"
    global student_data
    student_data = bkn_fn.Exec_Sql(student_sql)
    parent_data = bkn_fn.Exec_Sql(parent_sql)

    # Global variable for current student, initialized as None if no data
    global current_student
    current_student = student_data[0] if student_data else None

    # State variables for editing
    editing_student = [False]
    editing_parent = [False]

    # Student ID input field
    student_id_input = ft.TextField(
        label="รหัสนักเรียน",
        value=str(current_student["S_ID"]) if current_student else "",
        bgcolor=white,
        expand=True,
        on_submit=lambda e: search_student(e),
    )

    # Search input and results for students
    search_input = ft.TextField(
        label="ค้นหา: ชื่อ นามสกุล หรือ ชื่อเล่น",
        bgcolor=white,
        on_change=lambda e: update_search_results(e.control.value)
    )
    search_results = ft.Column(expand=True, scroll="auto")

    # Search input and results for parents
    parent_search_input = ft.TextField(
        label="ค้นหา: ชื่อหรือนามสกุลผู้ปกครอง",
        bgcolor=white,
        on_change=lambda e: update_parent_search_results(e.control.value)
    )
    parent_search_results = ft.Column(expand=True, scroll="auto")

    # Containers to hold dynamic content
    student_info_content = ft.Container()
    student_info_content.bgcolor=grey
    parent_info_content = ft.Container()

    # Edit buttons
    edit_save_student_btn = ft.ElevatedButton(
        text="Edit",
        icon="EDIT",
        color=yellow,
        bgcolor=navy_blue,
        icon_color=yellow,
        on_click=lambda e: toggle_student_edit(e)
    )
    edit_save_parent_btn = ft.ElevatedButton(
        text="Edit",
        icon="EDIT",
        color=navy_blue,
        bgcolor=yellow,
        icon_color=navy_blue,
        on_click=lambda e: toggle_parent_edit(e)
    )

    search_parent_btn = ft.ElevatedButton(
        text="Search",
        icon="SEARCH",
        color=navy_blue,
        bgcolor=yellow,
        icon_color=navy_blue,
        on_click=lambda e: toggle_parent_search_panel()
    )

    # Editable student fields (global to access values)
    name_input = ft.TextField(bgcolor=white, height=40)
    surname_input = ft.TextField(bgcolor=white, height=40)
    nick_input = ft.TextField(bgcolor=white, height=40)
    school_input = ft.TextField(bgcolor=white, height=40)
    class_input = ft.TextField(bgcolor=white, height=40)
    s_tel_input = ft.TextField(bgcolor=white, height=40)

    # Editable parent fields (global to access values) - Used in edit mode
    parent_name_input = ft.TextField(bgcolor=white, height=40)
    parent_surname_input = ft.TextField(bgcolor=white, height=40)
    parent_tel_input = ft.TextField(bgcolor=white, height=40)
    parent_line_input = ft.TextField(bgcolor=white, height=40)
    parent_facebook_input = ft.TextField(bgcolor=white, height=40)
    parent_address_input = ft.TextField(bgcolor=white, height=40)  # House Number
    parent_mu_input = ft.TextField(bgcolor=white, height=40)       # Village
    parent_tum_input = ft.TextField(bgcolor=white, height=40)      # Sub-district
    parent_amp_input = ft.TextField(bgcolor=white, height=40)      # District
    parent_prov_input = ft.TextField(bgcolor=white, height=40)     # Province
    parent_post_input = ft.TextField(bgcolor=white, height=40)     # Postal Code

    # AddressManager instance for dropdowns in add mode
    address_manager = AddressManager()

    # Dropdown fields for adding a new parent (used only in add mode)
    add_prov_input = ft.Dropdown(bgcolor=white, options=[ft.dropdown.Option(p) for p in address_manager.get_provinces()])
    add_amp_input = ft.Dropdown(bgcolor=white, options=[], visible=False)
    add_tum_input = ft.Dropdown(bgcolor=white, options=[], visible=False)
    add_post_input = ft.TextField(bgcolor=white, read_only=True, value="")

    # Cascading address selection functions for add mode
    def prov_select(e):
        add_amp_input.options = [ft.dropdown.Option(d) for d in address_manager.get_districts(add_prov_input.value)]
        add_amp_input.visible = True
        add_tum_input.options = []
        add_tum_input.visible = False
        add_post_input.value = ""
        page.update()

    def Amp_select(e):
        add_tum_input.options = [ft.dropdown.Option(s) for s in address_manager.get_subdistricts(add_prov_input.value, add_amp_input.value)]
        add_tum_input.visible = True
        add_post_input.value = ""
        page.update()

    def Tum_select(e):
        add_post_input.value = address_manager.get_postal_code(add_prov_input.value, add_amp_input.value, add_tum_input.value)
        page.update()

    add_prov_input.on_change = prov_select
    add_amp_input.on_change = Amp_select
    add_tum_input.on_change = Tum_select

    # Function to create editable student fields
    def create_editable_student_fields(student):
        if student:
            name_input.value = student["Name"]
            surname_input.value = student["SurName"]
            nick_input.value = student["Nick"]
            school_input.value = student["School"]
            class_input.value = student["Class"]
            s_tel_input.value = student["S_Tel"]
        
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            [
                                student_id_input,
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.SEARCH,
                                            icon_color=navy_blue,
                                            on_click=lambda e: toggle_search_panel()
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.ADD,
                                            icon_color=navy_blue,
                                            on_click=lambda e: add_student(e)
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            expand=3,
                        ),
                        ft.Row([edit_save_student_btn], expand=1, alignment=ft.MainAxisAlignment.END),
                    ]
                ),
                search_input,
                search_results,
                ft.Row(
                    [
                        ft.Column([ft.Text("ชื่อนักเรียน", size=13), name_input], expand=2, spacing=0),
                        ft.Column([ft.Text("นามสกุล", size=13), surname_input], expand=2, spacing=0),
                        ft.Column([ft.Text("ชื่อเล่น", size=13), nick_input], expand=1, spacing=0),
                    ],
                    spacing=5,
                ),
                ft.Row(
                    [
                        ft.Column([ft.Text("โรงเรียนประจำ", size=13), school_input], expand=5, spacing=0),
                        ft.Column([ft.Text("ระดับชั้น", size=13), class_input], expand=2, spacing=0),
                    ],
                    spacing=5,
                ),
                ft.Row(
                    [ft.Column([ft.Text("หมายเลขโทรศัพท์", size=13), s_tel_input], expand=True, spacing=0)],
                    spacing=5,
                ),
                # ft.Row(
                #     [
                #         ft.ElevatedButton(text="Enroll", icon="APP_REGISTRATION", color=yellow, bgcolor=navy_blue, icon_color=yellow, width=150),
                #         ft.ElevatedButton(text="Payment", icon="PAYMENT", color=yellow, bgcolor=navy_blue, icon_color=yellow, width=150),
                #     ],
                #     alignment=ft.MainAxisAlignment.START
                # )
            ]
        )

    # Function to create editable parent fields (for edit mode)
    def create_editable_parent_fields(student):
        if student:
            parent_name_input.value = student["M_Name"]
            parent_surname_input.value = student["M_SurName"]
            parent_tel_input.value = student["M_Tel"]
            parent_line_input.value = student["line"]
            parent_facebook_input.value = student["facebook"]
            parent_address_input.value = student.get("H_Adr", "")
            parent_mu_input.value = student.get("H_Mu", "")
            parent_tum_input.value = student.get("H_Tum", "")
            parent_amp_input.value = student.get("H_Amp", "")
            parent_prov_input.value = student.get("H_Prov", "")
            parent_post_input.value = student.get("H_Post", "")
            
            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(f"รหัสผู้ปกครอง: {student['P_ID']}"),
                            edit_save_parent_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("ชื่อผู้ปกครอง", size=13), parent_name_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("นามสกุล", size=13), parent_surname_input],
                                expand=1, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("หมายเลขโทรศัพท์", size=13), parent_tel_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("Line ID", size=13), parent_line_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("Facebook", size=13), parent_facebook_input],
                                expand=1, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("บ้านเลขที่", size=13), parent_address_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("หมู่", size=13), parent_mu_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("ตำบล", size=13), parent_tum_input],
                                expand=1, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("อำเภอ", size=13), parent_amp_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("จังหวัด", size=13), parent_prov_input],
                                expand=1, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("รหัสไปรษณีย์", size=13), parent_post_input],
                                expand=1, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                ]
            )
        return ft.Column([ft.Text("No parent data available")])

    # Function to create parent fields for adding a new student/parent
    def create_add_parent_fields():
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(f"รหัสผู้ปกครอง: {int(bkn_fn.max_id(parent_data, 'P_ID')['P_ID']) + 1 if parent_data else 1}"),
                        search_parent_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                parent_search_input,
                parent_search_results,
                ft.Row(
                    [
                        ft.Column(
                            [ft.Text("ชื่อผู้ปกครอง", size=13), parent_name_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("นามสกุล", size=13), parent_surname_input],
                            expand=1, spacing=0
                        ),
                    ],
                    spacing=5,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [ft.Text("หมายเลขโทรศัพท์", size=13), parent_tel_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("Line ID", size=13), parent_line_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("Facebook", size=13), parent_facebook_input],
                            expand=1, spacing=0
                        ),
                    ],
                    spacing=5,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [ft.Text("บ้านเลขที่", size=13), parent_address_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("หมู่", size=13), parent_mu_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("ตำบล", size=13), add_tum_input],
                            expand=1, spacing=0
                        ),
                    ],
                    spacing=5,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [ft.Text("อำเภอ", size=13), add_amp_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("จังหวัด", size=13), add_prov_input],
                            expand=1, spacing=0
                        ),
                        ft.Column(
                            [ft.Text("รหัสไปรษณีย์", size=13), add_post_input],
                            expand=1, spacing=0
                        ),
                    ],
                    spacing=5,
                ),
            ]
        )

    # Function to display student info dynamically
    def display_student_info(student, is_adding=False):
        if student or is_adding:
            student_info_content.content = create_editable_student_fields(student) if editing_student[0] else ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                [
                                    student_id_input,
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.SEARCH,
                                                icon_color=navy_blue,
                                                on_click=lambda e: toggle_search_panel()
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.ADD,
                                                icon_color=navy_blue,
                                                on_click=lambda e: add_student(e)
                                            ),
                                        ],
                                        spacing=0,
                                    ),
                                ],
                                expand=3,
                            ),
                            ft.Row([edit_save_student_btn], expand=1, alignment=ft.MainAxisAlignment.END),
                        ]
                    ),
                    search_input,
                    search_results,
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("ชื่อนักเรียน", size=13), ft.TextField(value=student["Name"] if student else "", read_only=True, bgcolor=white, height=40)],
                                expand=2, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("นามสกุล", size=13), ft.TextField(value=student["SurName"] if student else "", read_only=True, bgcolor=white, height=40)],
                                expand=2, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("ชื่อเล่น", size=13), ft.TextField(value=student["Nick"] if student else "", read_only=True, bgcolor=white, height=40)],
                                expand=1, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("โรงเรียนประจำ", size=13), ft.TextField(value=student["School"] if student else "", read_only=True, bgcolor=white, height=40)],
                                expand=5, spacing=0
                            ),
                            ft.Column(
                                [ft.Text("ระดับชั้น", size=13), ft.TextField(value=student["Class"] if student else "", read_only=True, bgcolor=white, height=40)],
                                expand=2, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [ft.Text("หมายเลขโทรศัพท์", size=13), ft.TextField(value=student["S_Tel"] if student else "", read_only=True, bgcolor=white, height=40)],
                                expand=True, spacing=0
                            ),
                        ],
                        spacing=5,
                    ),
                    # ft.Row(
                    #     [
                    #         ft.ElevatedButton(text="Enroll", icon="APP_REGISTRATION", color=yellow, bgcolor=navy_blue, icon_color=yellow, width=150),
                    #         ft.ElevatedButton(text="Payment", icon="PAYMENT", color=yellow, bgcolor=navy_blue, icon_color=yellow, width=150),
                    #     ],
                    #     alignment=ft.MainAxisAlignment.START
                    # )
                ]
            )
            parent_info_content.content = (
                create_add_parent_fields() if is_adding else
                create_editable_parent_fields(student) if editing_parent[0] else
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(f"รหัสผู้ปกครอง: {student['P_ID']}" if student else ""),
                                edit_save_parent_btn,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [ft.Text("ชื่อผู้ปกครอง", size=13), ft.TextField(value=student["M_Name"] if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("นามสกุล", size=13), ft.TextField(value=student["M_SurName"] if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                            ],
                            spacing=5,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [ft.Text("หมายเลขโทรศัพท์", size=13), ft.TextField(value=student["M_Tel"] if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("Line ID", size=13), ft.TextField(value=student["line"] if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("Facebook", size=13), ft.TextField(value=student["facebook"] if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                            ],
                            spacing=5,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [ft.Text("บ้านเลขที่", size=13), ft.TextField(value=student.get("H_Adr", "") if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("หมู่", size=13), ft.TextField(value=student.get("H_Mu", "") if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("ตำบล", size=13), ft.TextField(value=student.get("H_Tum", "") if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                            ],
                            spacing=5,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [ft.Text("อำเภอ", size=13), ft.TextField(value=student.get("H_Amp", "") if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("จังหวัด", size=13), ft.TextField(value=student.get("H_Prov", "") if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                                ft.Column(
                                    [ft.Text("รหัสไปรษณีย์", size=13), ft.TextField(value=student.get("H_Post", "") if student else "", read_only=True, bgcolor=white, height=40)],
                                    expand=1, spacing=0
                                ),
                            ],
                            spacing=5,
                        ),
                    ]
                )
            )
        else:
            if editing_student[0]:
                student_info_content.content = create_editable_student_fields(None)
            else:
                student_info_content.content = ft.Text("No student selected")
                
            if editing_parent[0]:
                parent_info_content.content = create_editable_parent_fields(None)
            else:
                parent_info_content.content = ft.Text("")
        page.update()

    # Toggle student edit mode and save to database
    def toggle_student_edit(e):
        global current_student, student_data
        
        editing_student[0] = not editing_student[0]
        
        if editing_student[0]:
            edit_save_student_btn.text = "Save"
            edit_save_student_btn.icon = "SAVE"
            display_student_info(current_student)
        else:
            if current_student and "S_ID" in current_student and current_student["S_ID"] is not None:  # Editing an existing student
                if not str(student_id_input.value).strip():
                    student_info_content.content = ft.Text("กรุณากรอกรหัสนักเรียน")
                    page.update()
                    return
                
                sql = f"""
                    UPDATE Student 
                    SET Name = '{name_input.value}', 
                        SurName = '{surname_input.value}', 
                        Nick = '{nick_input.value}', 
                        School = '{school_input.value}', 
                        Class = '{class_input.value}', 
                        S_Tel = '{s_tel_input.value}' 
                    WHERE S_ID = {student_id_input.value}
                """
                bkn_fn.Exec_Sql(sql)
            else:  # Adding a new student
                all_students = bkn_fn.Exec_Sql("SELECT * FROM Student ORDER BY S_ID DESC")
                next_s_id = int(bkn_fn.max_id(all_students, "S_ID")["S_ID"]) + 1 if all_students else 1
                
                if current_student["P_ID"] is None:  # No parent selected, create new
                    all_parents = bkn_fn.Exec_Sql("SELECT * FROM Parent ORDER BY P_ID DESC")
                    next_p_id = int(bkn_fn.max_id(all_parents, "P_ID")["P_ID"]) + 1 if all_parents else 1
                    parent_sql = f"""
                        INSERT INTO Parent (P_ID, M_Name, M_SurName, M_Tel, line, facebook, H_Adr, H_Mu, H_Tum, H_Amp, H_Prov, H_Post)
                        VALUES ({next_p_id}, '{parent_name_input.value}', '{parent_surname_input.value}', 
                                '{parent_tel_input.value}', '{parent_line_input.value}', 
                                '{parent_facebook_input.value}', '{parent_address_input.value}', 
                                '{parent_mu_input.value}', '{add_tum_input.value or ''}', 
                                '{add_amp_input.value or ''}', '{add_prov_input.value or ''}', 
                                '{add_post_input.value}')
                    """
                    bkn_fn.Exec_Sql(parent_sql)
                    p_id_to_use = next_p_id
                else:  # Use existing parent
                    p_id_to_use = current_student["P_ID"]
                
                student_sql = f"""
                    INSERT INTO Student (S_ID, Name, SurName, Nick, School, Class, S_Tel, P_ID)
                    VALUES ({next_s_id}, '{name_input.value}', '{surname_input.value}', '{nick_input.value}', 
                            '{school_input.value}', '{class_input.value}', '{s_tel_input.value}', 
                            {p_id_to_use})
                """
                bkn_fn.Exec_Sql(student_sql)
                
                student_id_input.value = str(next_s_id)

            student_data = bkn_fn.Exec_Sql("SELECT * FROM Student as S, Parent as P WHERE S.P_ID = P.P_ID ORDER BY S.S_ID DESC")
            current_student = next((s for s in student_data if s["S_ID"] == int(student_id_input.value)), None) if student_id_input.value else student_data[0] if student_data else None
            
            edit_save_student_btn.text = "Edit"
            edit_save_student_btn.icon = "EDIT"
            editing_parent[0] = False
            edit_save_parent_btn.text = "Edit"
            edit_save_parent_btn.icon = "EDIT"
            display_student_info(current_student)

    # Toggle parent edit mode and save to database
    def toggle_parent_edit(e):
        global current_student
        
        if not current_student:
            parent_info_content.content = ft.Text("ไม่พบข้อมูลผู้ปกครอง")
            page.update()
            return
        
        editing_parent[0] = not editing_parent[0]
        
        if editing_parent[0]:
            edit_save_parent_btn.text = "Save"
            edit_save_parent_btn.icon = "SAVE"
        else:
            parent_id = current_student["P_ID"]
            sql = f"""
                UPDATE Parent 
                SET M_Name = '{parent_name_input.value}', 
                    M_SurName = '{parent_surname_input.value}', 
                    M_Tel = '{parent_tel_input.value}', 
                    line = '{parent_line_input.value}', 
                    facebook = '{parent_facebook_input.value}',
                    H_Adr = '{parent_address_input.value}', 
                    H_Mu = '{parent_mu_input.value}', 
                    H_Tum = '{parent_tum_input.value}', 
                    H_Amp = '{parent_amp_input.value}', 
                    H_Prov = '{parent_prov_input.value}', 
                    H_Post = '{parent_post_input.value}' 
                WHERE P_ID = {parent_id}
            """
            bkn_fn.Exec_Sql(sql)
            
            student_data = bkn_fn.Exec_Sql("SELECT * FROM Student as S, Parent as P WHERE S.P_ID = P.P_ID ORDER BY S.S_ID DESC")
            current_student = next((s for s in student_data if s["S_ID"] == int(student_id_input.value)), None)
            
            edit_save_parent_btn.text = "Edit"
            edit_save_parent_btn.icon = "EDIT"
        
        display_student_info(current_student)

    # Search student by ID when Enter is pressed
    def search_student(e):
        student_id = str(student_id_input.value).strip()
        if not student_id:
            student_info_content.content = ft.Text("กรุณากรอกรหัสนักเรียน")
            parent_info_content.content = ft.Text("")
            page.update()
            return
        sql = f"SELECT * FROM Student as S, Parent as P WHERE S.P_ID = P.P_ID AND S.S_ID = {student_id}"
        result = bkn_fn.Exec_Sql(sql)
        global current_student
        current_student = result[0] if result else None
        if current_student:
            display_student_info(current_student)
        else:
            student_info_content.content = ft.Text("ไม่พบข้อมูลนักเรียน")
            parent_info_content.content = ft.Text("")
            page.update()

    # Toggle student search panel visibility
    def toggle_search_panel():
        search_input.visible = not search_input.visible
        search_results.visible = not search_results.visible
        if search_input.visible:
            update_search_results('')
        else:
            search_results.controls.clear()
        page.update()

    # Update student search results inline
    def update_search_results(search_text):
        search_results.controls.clear()
        for item in student_data:
            if (search_text in item['Name']) or (search_text in item['SurName']) or (search_text in item['Nick']):
                search_results.controls.append(
                    ft.Row(
                        [
                            ft.TextButton(
                                text=f"{item['Name']} {item['SurName']} ({item['Nick']}) - ID: {item['S_ID']}",
                                on_click=lambda e, s_id=item['S_ID']: select_student(s_id)
                            )
                        ]
                    )
                )
        page.update()

    # Select a student from search results
    def select_student(s_id):
        student_id_input.value = str(s_id)
        student = next((s for s in student_data if s["S_ID"] == s_id), None)
        if student:
            global current_student
            current_student = student
            display_student_info(student)
        search_input.visible = False
        search_results.visible = False
        search_results.controls.clear()
        page.update()

    # Toggle parent search panel visibility
    def toggle_parent_search_panel():
        parent_search_input.visible = not parent_search_input.visible
        parent_search_results.visible = not parent_search_results.visible
        if parent_search_input.visible:
            update_parent_search_results('')
        else:
            parent_search_results.controls.clear()
        page.update()

    # Update parent search results inline
    def update_parent_search_results(search_text):
        parent_search_results.controls.clear()
        for item in parent_data:
            if (search_text in item['M_Name']) or (search_text in item['M_SurName']):
                parent_search_results.controls.append(
                    ft.Row(
                        [
                            ft.TextButton(
                                text=f"{item['M_Name']} {item['M_SurName']} - ID: {item['P_ID']}",
                                on_click=lambda e, p_id=item['P_ID']: select_parent(p_id)
                            )
                        ]
                    )
                )
        page.update()

    # Select a parent from search results
    def select_parent(p_id):
        selected_parent = next((p for p in parent_data if p["P_ID"] == p_id), None)
        if selected_parent:
            parent_name_input.value = selected_parent["M_Name"]
            parent_surname_input.value = selected_parent["M_SurName"]
            parent_tel_input.value = selected_parent["M_Tel"]
            parent_line_input.value = selected_parent["line"]
            parent_facebook_input.value = selected_parent["facebook"]
            parent_address_input.value = selected_parent.get("H_Adr", "")
            parent_mu_input.value = selected_parent.get("H_Mu", "")
            add_tum_input.value = selected_parent.get("H_Tum", "")
            add_amp_input.value = selected_parent.get("H_Amp", "")
            add_prov_input.value = selected_parent.get("H_Prov", "")
            add_post_input.value = selected_parent.get("H_Post", "")
            # Update dropdown visibility
            add_amp_input.visible = True
            add_tum_input.visible = True
            add_amp_input.options = [ft.dropdown.Option(d) for d in address_manager.get_districts(add_prov_input.value)]
            add_tum_input.options = [ft.dropdown.Option(s) for s in address_manager.get_subdistricts(add_prov_input.value, add_amp_input.value)]
            # Set current_student P_ID for saving
            global current_student
            current_student["P_ID"] = p_id
        parent_search_input.visible = False
        parent_search_results.visible = False
        parent_search_results.controls.clear()
        page.update()

    # Add new student function with cascading address workflow
    def add_student(e):
        global current_student
        
        all_students = bkn_fn.Exec_Sql("SELECT * FROM Student ORDER BY S_ID DESC")
        all_parents = bkn_fn.Exec_Sql("SELECT * FROM Parent ORDER BY P_ID DESC")
        
        next_s_id = int(bkn_fn.max_id(all_students, "S_ID")["S_ID"]) + 1 if all_students else 1
        next_p_id = int(bkn_fn.max_id(all_parents, "P_ID")["P_ID"]) + 1 if all_parents else 1
        
        current_student = {
            "S_ID": None,
            "P_ID": None,  # Reset to None
            "Name": "",
            "SurName": "",
            "Nick": "",
            "School": "",
            "Class": "",
            "S_Tel": "",
            "M_Name": "",
            "M_SurName": "",
            "M_Tel": "",
            "line": "",
            "facebook": "",
            "H_Adr": "",
            "H_Mu": "",
            "H_Tum": "",
            "H_Amp": "",
            "H_Prov": "",
            "H_Post": ""
        }
        
        student_id_input.value = str(next_s_id)
        
        # Clear all input fields
        name_input.value = ""
        surname_input.value = ""
        nick_input.value = ""
        school_input.value = ""
        class_input.value = ""
        s_tel_input.value = ""
        parent_name_input.value = ""
        parent_surname_input.value = ""
        parent_tel_input.value = ""
        parent_line_input.value = ""
        parent_facebook_input.value = ""
        parent_address_input.value = ""
        parent_mu_input.value = ""
        add_tum_input.value = None
        add_amp_input.value = None
        add_prov_input.value = None
        add_post_input.value = ""
        add_amp_input.visible = False
        add_tum_input.visible = False
        
        editing_student[0] = True
        editing_parent[0] = True
        
        edit_save_student_btn.text = "Save"
        edit_save_student_btn.icon = "SAVE"
        edit_save_parent_btn.text = "Save" 
        edit_save_parent_btn.icon = "SAVE"
        
        display_student_info(current_student, is_adding=True)
        
        if search_input.visible:
            search_input.visible = False
            search_results.visible = False
            search_results.controls.clear()
            page.update()

    # Initial display
    display_student_info(current_student)

    # Hide search panels initially
    search_input.visible = False
    search_results.visible = False
    parent_search_input.visible = False
    parent_search_results.visible = False

    # Student Info Container
    student_info_container = ft.Container(
        margin=ft.margin.only(10, 0, 10, 0),
        padding=ft.padding.only(0,0,0,10),
        border_radius=15,
        bgcolor=grey,
        content=ft.Column(
            controls=[
                ft.Container(
                    bgcolor=bkn_fn.navy_blue,
                    height=40,
                    content=ft.Row(
                        [ft.Text("::: ข้อมูลนักเรียน :::", color=bkn_fn.yellow, size=22,font_family=bkn_fn.menu_font)],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
                student_info_content,
            ]
        ),
    )

    # Parent Info Container
    parent_info_container = ft.Container(
        margin=ft.margin.only(10, 0, 10, 0),
        padding=ft.padding.only(0,0,0,10),
        border_radius=15,
        bgcolor=grey,
        content=ft.Column(
            controls=[
                ft.Container(
                    bgcolor=yellow,
                    height=40,
                    content=ft.Row(
                        [ft.Text("::: ข้อมูลผู้ปกครอง :::", color=navy_blue, size=22,font_family=bkn_fn.menu_font)],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
                parent_info_content,
            ]
        ),
    )

    return ft.Column(
        controls=[student_info_container, parent_info_container],
        spacing=10,
    )

# Example usage
def main(page: ft.Page):
    page.add(containers(page))

if __name__ == "__main__":
    ft.app(target=main)