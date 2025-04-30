# payment_page.py
import flet as ft
import sqlite3
#from calendar_utils import CalendarManager  # Correct import from calendar_utils
import calendar_utils as calendar
import bkn_fn

def containers(page):
    page.fonts = bkn_fn.pagefonts
    # Define color scheme
    navy_blue = bkn_fn.navy_blue
    yellow = bkn_fn.yellow
    grey = bkn_fn.grey
    white = "#FFFFFF"

    # Constants for text size and field height
    txt_size = 13
    field_height = 40

    # Initialize CalendarManager
    calendar_manager = calendar.CalendarManager(page)

    # Fetch the last payment record along with student details
    payment_sql = """
        SELECT pay.*, s.Name, s.SurName, s.Nick 
        FROM Payment AS pay 
        JOIN Student AS s ON pay.S_ID = s.S_ID 
        ORDER BY pay.ID DESC LIMIT 1
    """
    payment_data = bkn_fn.Exec_Sql(payment_sql)
    last_payment = payment_data[0] if payment_data else None

    # Fetch all payment records for search functionality
    all_payments_sql = """
        SELECT pay.*, s.Name, s.SurName, s.Nick 
        FROM Payment AS pay 
        JOIN Student AS s ON pay.S_ID = s.S_ID 
        ORDER BY pay.ID DESC
    """
    all_payments = bkn_fn.Exec_Sql(all_payments_sql)

    # UI elements for student info
    student_id_text = ft.Text(
        str(last_payment["S_ID"]) if last_payment else "N/A", 
        color=navy_blue, 
        size=txt_size
    )
    name_text = ft.Text(
        last_payment["Name"] if last_payment else "N/A", 
        color=navy_blue, 
        size=txt_size
    )
    surname_text = ft.Text(
        last_payment["SurName"] if last_payment else "N/A", 
        color=navy_blue, 
        size=txt_size
    )
    nickname_text = ft.Text(
        last_payment["Nick"] if last_payment else "N/A", 
        color=navy_blue, 
        size=txt_size
    )

    # Course details (RNote)
    r_note = ft.TextField(
        label="รายละเอียดของคอร์ส", 
        text_size=txt_size, 
        height=field_height,
        value=last_payment["RNote"].split("^")[0] if last_payment and "^" in last_payment["RNote"] else last_payment["RNote"] if last_payment else ""
    )

    # Payment Section Components
    total_amount = ft.TextField(
        keyboard_type=ft.KeyboardType.NUMBER,
        width=100,
        color="#0000ff",
        value=str(last_payment["Total"]) if last_payment else "0"
    )
    remaining_amount = ft.TextField(
        keyboard_type=ft.KeyboardType.NUMBER,
        height=field_height,
        width=100,
        color='#ff0000',
        value=str(int(last_payment["Total"]) - (int(last_payment["Pay1"]) + int(last_payment["Pay2"]) + int(last_payment["Pay3"]) + int(last_payment["Pay4"]))) if last_payment else "0"
    )
    extranotes = ft.TextField(
        label="บันทึกเพิ่มเติม",
        text_size=txt_size,
        height=field_height,
        bgcolor=white,
        value=last_payment["RNote"].split("^")[1] if last_payment and "^" in last_payment["RNote"] else ""
    )

    def save_handler(index,paymentid):
            # เตรียม id ต่อไปสำหรับเพิ่มข้อมูลใน receipt
            maxrecID = int(bkn_fn.max_id(bkn_fn.Exec_Sql("SELECT R_ID FROM Receipt"),"R_ID")["R_ID"])+1
            #ปรัปปรุงข้อมูลการชำระเงินเฉพาะครั้งที่มีการชำระ 
            sql = f"UPDATE Payment SET  Pay{index} = '{pay_amount_field[index].value}', Paid_Date{index} = '{calendar.ISOdate(payment_date_field[index].value)}', Receipt{index} = '{maxrecID}' WHERE ID = {paymentid}"
            bkn_fn.Exec_Sql(sql)
            # สร้างข้อมูลใบเสร็จใหม่ ใน receipt
            sql = f"INSERT INTO Receipt (R_ID, Amount, Cash, RNote, ExtraNote, Paid_Date, S_ID) VALUES ('{maxrecID}', '{pay_amount_field[index].value}', '{paytype_radio[index].value}', '{r_note.value}', '{extranotes.value}', '{calendar.ISOdate(payment_date_field[index].value)}', '{student_id_text.value}');"
            bkn_fn.Exec_Sql(sql)
            #update หน้าแสดงผล 
            save_btns[index].visible = False
            all = bkn_fn.Exec_Sql(all_payments_sql)
            select_payment(paymentid,all)
   

    def show_receipt(index):

            bkn_fn.receiptdocx(index)
    
    def check_save_button_visibility(index):
        amount_filled = pay_amount_field[index].value != ""
        date_filled = payment_date_field[index].value != ""
        type_selected = paytype_radio[index].value is not None
        
        # Only show save button if all required fields are filled
        save_btns[index].visible = amount_filled and date_filled and type_selected
        page.update()


    payment_date_field = [None]*5
    pay_amount_field = [None]*5
    paytype_radio = [None]*5
    receipt_btns = [None]*5
    save_btns = [None]*5
    for i in range(1,5):
        payment_date_field[i] = ft.TextField(
            label="วันที่ชำระ", 
            text_size=txt_size, 
            height=field_height, 
            width=100,
            on_change=lambda e, idx=i: check_save_button_visibility(idx),
            value=calendar.thaidate(str(last_payment[f"Paid_Date{i}"])) if last_payment and last_payment[f"Paid_Date{i}"] != "0000-00-00" else ""
        )
        pay_amount_field[i] = ft.TextField(
            keyboard_type=ft.KeyboardType.NUMBER, 
            width=100, 
            height=field_height, 
            text_size=txt_size,
            on_change=lambda e, idx=i: check_save_button_visibility(idx),
            value=str(last_payment[f"Pay{i}"]) if last_payment and last_payment[f"Pay{i}"] != 0 else ""
        )
        paytype_radio[i] = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="เงินสด", label="เงินสด"),
                ft.Radio(value="โอน", label="โอน"),
                ft.Radio(value="บัตรเครดิต", label="บัตรเครดิต"),
                ft.Radio(value="คูปอง", label="คูปอง"),
            ]),
            on_change=lambda e, idx=i: check_save_button_visibility(idx)
        )
        receipt_btns[i] = ft.ElevatedButton(
            text=f"ใบเสร็จเลขที่ {last_payment[f'Receipt{i}']}" if last_payment and last_payment[f"Receipt{i}"] != 0 else "ใบเสร็จเลขที่ 0", 
            bgcolor=navy_blue, 
            color=yellow,
            width=150,
            visible=False,
            on_click = lambda e, idx = last_payment[f'Receipt{i}'] : show_receipt(idx)
        )
        save_btns[i] = ft.ElevatedButton(
            text="Save", 
            bgcolor=yellow, 
            color=navy_blue,
            width=150,
            visible = False,
            on_click = lambda e, idx = i : save_handler(idx,last_payment["ID"])
        )
        if pay_amount_field[i].value !="":
            receipt_btns[i].visible = True

    # Payment Installment Section
    payment_rows = []
    for i in range(1, 5):
        payment_row = ft.Row([
            ft.Text(f'ชำระครั้งที่ {i} : ', width=120),
            pay_amount_field[i],
            payment_date_field[i],
            calendar_manager.get_calendar_button(payment_date_field[i]),
            paytype_radio[i],
            receipt_btns[i],
            save_btns[i]
        ])
        payment_rows.append(payment_row)

    payment_section_group = ft.Column(payment_rows)

    # Search functionality
    search_input = ft.TextField(
        label="ค้นหา: ชื่อ นามสกุล หรือ ชื่อเล่น", 
        bgcolor=white, 
        visible=False,
        on_change=lambda e: update_search_results(e.control.value)
    )
    search_results = ft.Column(visible=False, scroll="auto", height=150)

    def toggle_search_panel(e):
        search_input.visible = not search_input.visible
        search_results.visible = not search_results.visible
        if search_input.visible:
            search_input.value = ""
            update_search_results("")
        else:
            search_results.controls.clear()
        page.update()

    def update_search_results(search_text):
        all_payments =bkn_fn.Exec_Sql(all_payments_sql)
        search_results.controls.clear()
        if not all_payments:
            search_results.controls.append(ft.Text("ไม่มีข้อมูลการชำระเงินในฐานข้อมูล"))
        else:
            filtered_payments = [
                p for p in all_payments
                if (search_text.lower() in str(p["Name"]).lower() or
                    search_text.lower() in str(p["SurName"]).lower() or
                    search_text.lower() in str(p["Nick"]).lower())
            ]
            if not filtered_payments:
                search_results.controls.append(ft.Text("ไม่พบการชำระเงินที่ตรงกับการค้นหา"))
            else:
                for payment in filtered_payments:
                    search_results.controls.append(
                        ft.TextButton(
                            text=f"{payment['Name']}({payment['Nick']}):{payment['RNote']}:ยอดเต็ม= {payment['Total']}",
                            on_click=lambda e, p_id=payment["ID"]: select_payment(p_id,all_payments)
                        )
                    )
        page.update()

    def select_payment(p_id,allpay):
        selected_payment = next((p for p in allpay if p["ID"] == p_id), None)
        if selected_payment:
            # Update student info
            student_id_text.value = str(selected_payment["S_ID"])
            name_text.value = selected_payment["Name"]
            surname_text.value = selected_payment["SurName"]
            nickname_text.value = selected_payment["Nick"]
            # Update course details
            r_note.value = selected_payment["RNote"].split("^")[0] if "^" in selected_payment["RNote"] else selected_payment["RNote"]
            extranotes.value = selected_payment["RNote"].split("^")[1] if "^" in selected_payment["RNote"] else ""
            # Update payment details
            total_amount.value = str(selected_payment["Total"])
            remaining_amount.value = str(int(selected_payment["Total"]) - (int(selected_payment["Pay1"]) + int(selected_payment["Pay2"]) + int(selected_payment["Pay3"]) + int(selected_payment["Pay4"])))
            # Update payment rows
            for i in range(1, 5):
                pay_amount_field[i].value = str(selected_payment[f"Pay{i}"]) if selected_payment[f"Pay{i}"] != 0 else ""
                payment_date_field[i].value = str(calendar.thaidate(selected_payment[f"Paid_Date{i}"])) if selected_payment[f"Paid_Date{i}"] != "0000-00-00" else ""
                save_btns[i].on_click = lambda e, idx = i : save_handler(idx,selected_payment["ID"])
                # Check if payment already exists
                if pay_amount_field[i].value != "":
                    save_btns[i].visible = False
                    receipt_btns[i].visible = True
                else:
                    # Check if all fields required for saving are filled
                    check_save_button_visibility(i)
                    receipt_btns[i].visible = False
                receipt_btns[i].text = f"ใบเสร็จเลขที่ {selected_payment[f'Receipt{i}']}" if selected_payment[f"Receipt{i}"] != 0 else "ใบเสร็จเลขที่ 0"
                receipt_btns[i].on_click = lambda e, idx = selected_payment[f'Receipt{i}'] : show_receipt(idx) 
        search_input.visible = False
        search_results.visible = False
        search_results.controls.clear()
        page.update()

    # Main UI layout
    return ft.Column(
        controls=[
            # Student Info Container
            ft.Container(
                margin=ft.margin.only(10, 0, 10, 0),
                padding=0,
                border_radius=15,
                bgcolor=grey,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor=navy_blue,
                            height=40,
                            content=ft.Row(
                                [ft.Text("::: ข้อมูลนักเรียน :::", color=yellow, size=22,font_family=bkn_fn.menu_font)],
                                expand=True,
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.only(10, 0, 10, 10),
                            content=ft.Column([
                                ft.Row([
                                    ft.Text('รหัสประจำตัวนักเรียน', expand=False),
                                    student_id_text,
                                    ft.Text("ชื่อ :", color=navy_blue, size=txt_size),
                                    name_text,
                                    surname_text,
                                    ft.Text("(", color=navy_blue, size=txt_size),
                                    nickname_text,
                                    ft.Text(")", color=navy_blue, size=txt_size),
                                    ft.IconButton(on_click=toggle_search_panel, icon=ft.Icons.SEARCH)
                                ]),
                                search_input,
                                search_results,
                                r_note,
                            ])
                        ),
                    ]
                )
            ),
            # Payment Details Container
            ft.Container(
                margin=ft.margin.only(10, 0, 10, 0),
                padding=0,
                border_radius=15,
                bgcolor=grey,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor=yellow,
                            height=40,
                            content=ft.Row(
                                [ft.Text("::: การชำระเงิน :::", color=navy_blue, size=22,font_family=bkn_fn.menu_font)],
                                expand=True,
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.only(10, 0, 10, 10),
                            content=ft.Column([
                                ft.Row([
                                    ft.Column([
                                        ft.Text('ยอดที่ต้องชำระ : ', width=120)
                                    ], expand=False),
                                    ft.Column([
                                        total_amount,
                                    ], expand=True),
                                    ft.Column([], expand=True),
                                ]),
                                payment_section_group,
                                ft.Row([
                                    ft.Column([
                                        ft.Text('คงเหลือค้างชำระ : ', width=120)
                                    ], expand=False),
                                    ft.Column([
                                        remaining_amount,
                                    ]),
                                    ft.Column([
                                        extranotes,
                                    ], expand=True),
                                ]),
                            ])
                        )
                    ]
                )
            ),
        ]
    )

# Main function to set up the page
def main(page: ft.Page):
    page.title = "Payment Page"
    ui = containers(page)
    page.window.height = 650
    page.window.width = 1050
    page.add(ui)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)