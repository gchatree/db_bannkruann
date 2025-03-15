import flet as ft
import os
import student_page
import course_page
import enroll_page
import payment_page
import bkn_fn
# import receipt_page


def main(page: ft.Page):
    # Set page properties
    page.title = "Student Information and Financial Management"
    page.padding = 0
    page.bgcolor = bkn_fn.white
    # Set window size and center it
    page.window.width = 1200
    page.window.height = 700
    page.window.center()

    # Font definitions - register Thai fonts from assets/fonts folder
    page.fonts = {
        "THNiramit": "fonts/TH Niramit AS.ttf",
        "THFahkwang": "fonts/TH Fahkwang.ttf",
        "THK2DJuly8": "fonts/TH K2D July8.ttf",
        "THMaliGrade6": "fonts/TH Mali Grade6.ttf",
        "THSarabun": "fonts/THSarabun.ttf",
        "Charmonman": "fonts/Charmonman-Regular.ttf"
    }
    
    # Choose which font to use for Thai text
    menu_font = "THFahkwang"
    btn_font = "THSarabun"
    # Local image path
    path = os.path.abspath('')
    logo_path = "/images/bannAnn.png"
    
    # Thai title texts for different pages
    thai_titles = {
        "Home": "ระบบจัดการข้อมูลและการเงิน : Home",
        "Students": "ระบบจัดการข้อมูลและการเงิน : Students",
        "Courses": "ระบบจัดการข้อมูลและการเงิน : Courses",
        "Enroll": "ระบบจัดการข้อมูลและการเงิน : Enroll",
        "Payment": "ระบบจัดการข้อมูลและการเงิน : Payment",
        "Receipt": "ระบบจัดการข้อมูลและการเงิน : Receipt",
    }
    
    # Current page tracker
    current_page = "Home"
    
    # Function to create content for different pages
    def create_page_content(page_name):
        english_subtitle = f"{page_name} Information and Financial Management" if page_name == "Home" else f"{page_name} Page"
        if page_name == "Home":
            return ft.Container(
                expand=True,
                padding=ft.padding.all(40),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            thai_titles[page_name],
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            english_subtitle,
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=40),
                        ft.Container(
                            content=ft.Image(
                                src=logo_path,
                                width=300,
                                height=300,
                            ),
                            alignment=ft.alignment.center,
                        )
                    ]
                )
            )
        elif page_name == "Students":
            return student_page.containers(page)
        elif page_name == "Courses":
            return course_page.containers(page)
        elif page_name == "Enroll":
            return enroll_page.containers(page)
        elif page_name == "Payment":
            return payment_page.containers(page)
        # elif page_name == "Receipt":
        #     return 

    # Create content containers for each page
    home_content = create_page_content("Home")
    students_content = create_page_content("Students")
    courses_content = create_page_content("Courses")
    enroll_content = create_page_content("Enroll")
    payment_content = create_page_content("Payment")
    receipt_content = create_page_content("Receipt")
    
    # Container to hold the current page content
    content_container = ft.Container(
        expand=True,
        content=home_content
    )
    
    # Function to change the current page
    def change_page(e, page_name):
        nonlocal current_page
        current_page = page_name
        
        if page_name == "Home":
            content_container.content = home_content
        elif page_name == "Students":
            content_container.content = students_content
        elif page_name == "Courses":
            content_container.content = courses_content
        elif page_name == "Enroll":
            content_container.content = enroll_content
        elif page_name == "Payment":
            content_container.content = payment_content
        elif page_name == "Receipt":
            content_container.content = receipt_content
        for button in sidebar.content.controls[1:]:
            text = button.content.controls[1].value
            is_selected = text == page_name
            button.bgcolor = bkn_fn.yellow if is_selected else "transparent"
            button.content.controls[0].color = bkn_fn.navy_blue if is_selected else bkn_fn.yellow
            button.content.controls[1].color = bkn_fn.navy_blue if is_selected else bkn_fn.yellow
        
        page.update()
    
    
    # Create menu button factory function
    def create_menu_button(icon, text, is_selected=False):
        bg_color = bkn_fn.yellow if is_selected else "transparent"
        text_color = bkn_fn.navy_blue if is_selected else bkn_fn.yellow
        icon_color = bkn_fn.navy_blue if is_selected else bkn_fn.yellow
        
        return ft.Container(
            bgcolor=bg_color,
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.only(left=20, right=20, top=15, bottom=15),
            margin=ft.margin.only(left=10, right=10),
            content=ft.Row([
                ft.Icon(icon, color=icon_color),
                ft.Text(text, 
                        color=text_color,
                ),
            ]),
            on_click=lambda e: change_page(e, text),
            ink=True,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

    # Create the sidebar with new Enroll button
    sidebar = ft.Container(
        width=280,
        bgcolor=bkn_fn.navy_blue,
        padding=ft.padding.only(top=20),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=20, bottom=20),
                    content=ft.Row([
                        ft.Image(
                            src=logo_path,
                            width=40,
                            height=40,
                            border_radius=ft.border_radius.all(20),
                        ),
                        ft.Text(
                            "โรงเรียนกวดวิชาบ้านครูแอน",
                            color="white",
                            size=20,
                            font_family=menu_font,
                        )
                    ])
                ),
                create_menu_button(ft.Icons.HOME, "Home", is_selected=True),
                create_menu_button(ft.Icons.PERSON, "Students"),
                create_menu_button(ft.Icons.SCHOOL, "Courses"),
                create_menu_button(ft.Icons.APP_REGISTRATION, "Enroll"), 
                create_menu_button(ft.Icons.CREDIT_CARD, "Payment"),
                create_menu_button(ft.Icons.RECEIPT, "Receipt"),
            ]
        )
    )
    
    # Create the overall layout
    page.add(
        ft.Row(
            spacing=0,
            controls=[
                sidebar,
                ft.VerticalDivider(width=1, color="#e0e0e0"),
                content_container,
            ],
            expand=True,
        )
    )

ft.app(target=main, assets_dir='assets')