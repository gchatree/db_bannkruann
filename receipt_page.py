import flet as ft
import bkn_fn
import pandas as pd
import calendar_utils as calendar
from datetime import datetime, timedelta

# Constants
TEXT_SIZE = 14
FIELD_HEIGHT = 40

def containers(page):
    page.fonts = bkn_fn.pagefonts
    calendar_manager = calendar.CalendarManager(page)
    from_date = ft.TextField(width=150, label="From Date")
    to_date = ft.TextField(width=150, label="To Date")

    # Base query to fetch data
    base_query = """
        SELECT 
            r.R_ID, 
            r.Paid_Date, 
            s.Name, 
            s.Nick, 
            r.Cash, 
            r.Amount
        FROM 
            Receipt r
        JOIN 
            Student s ON r.S_ID = s.S_ID
    """
    filtered_data = bkn_fn.Exec_Sql(base_query)

    def update_dates(e):
        today = datetime.now()
        if dropdownfilter.value == "today":
            from_date.value = today.strftime("%Y-%m-%d")
            to_date.value = today.strftime("%Y-%m-%d")
        elif dropdownfilter.value == "this week":
            start_of_week = today - timedelta(days=today.weekday())
            from_date.value = start_of_week.strftime("%Y-%m-%d")
            to_date.value = today.strftime("%Y-%m-%d")
        elif dropdownfilter.value == "this month":
            from_date.value = today.replace(day=1).strftime("%Y-%m-%d")
            to_date.value = today.strftime("%Y-%m-%d")
        elif dropdownfilter.value == "last week":
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            from_date.value = start_of_last_week.strftime("%Y-%m-%d")
            to_date.value = end_of_last_week.strftime("%Y-%m-%d")
        elif dropdownfilter.value == "last month":
            first_of_current = today.replace(day=1)
            last_day_of_last_month = first_of_current - timedelta(days=1)
            first_of_last_month = last_day_of_last_month.replace(day=1)
            from_date.value = first_of_last_month.strftime("%Y-%m-%d")
            to_date.value = last_day_of_last_month.strftime("%Y-%m-%d")
        
        from_date.value = calendar.thaidate(from_date.value)
        to_date.value = calendar.thaidate(to_date.value)
        page.update()

    dropdownfilter = ft.Dropdown(
        label="ช่วงเวลา",
        options=[
            ft.dropdown.Option("today"),
            ft.dropdown.Option("this week"),
            ft.dropdown.Option("this month"),
            ft.dropdown.Option("last week"),   
            ft.dropdown.Option("last month")
        ],
        expand=True,
        on_change=update_dates
    )

    def process_data_for_table(data):
        payment_types = sorted(set(item["Cash"] for item in data))
        grouped_data = {}
        for item in data:
            key = (item["R_ID"], item["Paid_Date"], item["Name"], item["Nick"])
            if key not in grouped_data:
                grouped_data[key] = {ptype: 0 for ptype in payment_types}
            amount = int(item["Amount"])  # Use float(item["Amount"]) if decimals are needed
            grouped_data[key][item["Cash"]] = amount
        
        processed_data = [
            {
                "R_ID": key[0],
                "Paid_Date": key[1],
                "Name": key[2],
                "Nick": key[3],
                **amounts
            } for key, amounts in grouped_data.items()
        ]
        
        sums = {ptype: sum(item[ptype] for item in processed_data) for ptype in payment_types}
        total_sum = sum(sums.values())
        
        return processed_data, payment_types, sums, total_sum

    def build_table(filtered_data):
        processed_data, payment_types, sums, total_sum = process_data_for_table(filtered_data)
        
        columns = [
            ft.DataColumn(ft.Text("เลขที่", size=TEXT_SIZE)),
            ft.DataColumn(ft.Text("วันที่", size=TEXT_SIZE)),
            ft.DataColumn(ft.Text("ชื่อนักเรียน", size=TEXT_SIZE)),
        ] + [
            ft.DataColumn(ft.Text(ptype, size=TEXT_SIZE)) for ptype in payment_types
        ]

        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item["R_ID"], size=TEXT_SIZE)),
                    ft.DataCell(ft.Text(item["Paid_Date"], size=TEXT_SIZE)),
                    ft.DataCell(ft.Text(f'{item["Name"]} (น้อง {item["Nick"]})', size=TEXT_SIZE)),
                ] + [
                    ft.DataCell(ft.Text(str(item[ptype]) if item[ptype] else "", 
                                      text_align=ft.TextAlign.CENTER, size=TEXT_SIZE))
                    for ptype in payment_types
                ]
            ) for item in processed_data
        ]

        # Summary row for each payment type
        summary_row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("รวม", size=TEXT_SIZE, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("")),
                ft.DataCell(ft.Text("")),
            ] + [
                ft.DataCell(ft.Text(str(sums[ptype]), text_align=ft.TextAlign.CENTER, 
                                  size=TEXT_SIZE, weight=ft.FontWeight.BOLD))
                for ptype in payment_types
            ]
        )
        rows.append(summary_row)

        # Total sum row without span
        total_row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("ยอดรวมทั้งหมด", size=TEXT_SIZE, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("")),  # Empty cell for Paid_Date
                ft.DataCell(ft.Text("")),  # Empty cell for Name/Nick
            ] + [
                ft.DataCell(ft.Text(str(total_sum) if i == len(payment_types) - 1 else "", 
                                  text_align=ft.TextAlign.CENTER, size=TEXT_SIZE, 
                                  weight=ft.FontWeight.BOLD))
                for i in range(len(payment_types))
            ]
        )
        rows.append(total_row)

        return ft.DataTable(
            column_spacing=50,
            columns=columns,
            rows=rows,
        )
    
    table_container = ft.Container(content=build_table(filtered_data), expand=True)
    
    def update_table(e):
        if from_date.value != "":
            f = calendar.ISOdate(from_date.value)
            if to_date.value == "" or calendar.ISOdate(to_date.value) < calendar.ISOdate(from_date.value):
                t = f
                to_date.value = from_date.value
            else:
                t = calendar.ISOdate(to_date.value)
            query = base_query + f' WHERE r.Paid_Date BETWEEN "{f}" AND "{t}"'
        else:
            query = base_query
        f_data = bkn_fn.Exec_Sql(query)
        table_container.content = build_table(f_data)
        page.update()
        #print(query)

    return ft.Column(controls=[
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=bkn_fn.navy_blue,
                        height=40,
                        content=ft.Row(
                            [ft.Text("::: สรุปรายรับ :::", color=bkn_fn.yellow, size=22, font_family=bkn_fn.menu_font)],
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Row([from_date, calendar_manager.get_calendar_button(from_date), 
                           to_date, calendar_manager.get_calendar_button(to_date), 
                           dropdownfilter, 
                           ft.IconButton(on_click=update_table, icon=ft.Icons.SEARCH, 
                                       bgcolor=bkn_fn.navy_blue, icon_color=bkn_fn.yellow)], 
                           spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Column([table_container], scroll="auto", height=300),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.only(0, 0, 0, 10),
            margin=ft.margin.only(10, 0, 10, 0),
            border_radius=15,
            bgcolor=bkn_fn.grey,
        ),
    ])

def main(page: ft.Page):
    page.title = "Receipt Management"
    page.bgcolor = "#F5F5F5"
    con = ft.Column([containers(page)], scroll='auto')
    page.add(con)
    page.scroll = True

if __name__ == "__main__":
    ft.app(target=main)