# calendar_utils.py
import flet as ft
from datetime import datetime

def thaidate(date):
    months = {
        "01": "ม.ค.", "02": "ก.พ.", "03": "มี.ค.", "04": "เม.ย.", "05": "พ.ค.",
        "06": "มิ.ย.", "07": "ก.ค.", "08": "ส.ค.", "09": "ก.ย.", "10": "ต.ค.",
        "11": "พ.ย.", "12": "ธ.ค."
    }
    year, month, day = date.split("-")
    thai_year = int(year) + 543
    thai_year_str = str(thai_year % 100).zfill(2)
    return f"{day} {months[month]} {thai_year_str}"

def ISOdate(tdate):
        months = {
            "ม.ค.": "01",
            "ก.พ.": "02",
            "มี.ค.": "03",
            "เม.ย.": "04",
            "พ.ค.": "05",
            "มิ.ย.": "06",
            "ก.ค.": "07",
            "ส.ค.": "08",
            "ก.ย.": "09",
            "ต.ค.": "10",
            "พ.ย.": "11",
            "ธ.ค.": "12"
        }
        
        day, month, year = tdate.split(" ")
        #month, year = month_year[:(len(month_year)-2)], month_year[(len(month_year)-2):]
        
        iso_year = int(year) - 543 + 2500
        iso_year_str = str(iso_year).zfill(4)
        
        iso_date = f"{iso_year_str}-{months[month]}-{day.zfill(2)}"
        return iso_date

class CalendarManager:
    def __init__(self, page):
        self.page = page
        self.target_field = None
        # DatePicker setup
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            first_date=datetime(2019, 1, 1),
            last_date=datetime(2034, 12, 31),
        )
        self.page.overlay.append(self.date_picker)

    def change_date(self, e):
        if e.control.value:
            self.target_field.value = thaidate(e.control.value.strftime("%Y-%m-%d"))
            self.page.update()

    def open_date_picker(self, e, field):
        self.target_field = field
        self.date_picker.open = True
        self.page.update()

    def get_calendar_button(self, field):
        return ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
            on_click=lambda e: self.open_date_picker(e, field)
        )
    
    