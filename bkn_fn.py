import requests
import json
from docxtpl import DocxTemplate
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

navy_blue = "#0f172a"
yellow = "#FFCC00"
grey = "#E0E0E0"
white = "#FFFFFF"
darkgrey = "#A9A9A9"

pagefonts = {
        "THNiramit": "fonts/TH Niramit AS.ttf",
        "THFahkwang": "fonts/TH Fahkwang.ttf",
        "THK2DJuly8": "fonts/TH K2D July8.ttf",
        "THMaliGrade6": "fonts/TH Mali Grade6.ttf",
        "THSarabun": "fonts/Sarabun-Regular.ttf",
        "Charmonman": "fonts/Charmonman-Regular.ttf",
        "Niramit":"fonts/Niramit-Regular.ttf",
        "Srisakdi:":"fonts/Srisakdi-Regular.ttf"
    }
    
menu_font = "THFahkwang"
Normal_font = "THSarabun"
Header_font = "Charmonman"
btn_font = "THNiramit"

def open_pdf_receipt_no(rid):
    ospth = os.getcwd()
    pdf_path = f"{ospth}/receipt/{rid}.docx"
    try:
        if sys.platform.startswith('win'):
            # Windows
            os.startfile(pdf_path)
        elif sys.platform.startswith('darwin'):
            # macOS
            subprocess.call(('open', pdf_path))
        elif sys.platform.startswith('linux'):
            # Linux
            subprocess.call(('xdg-open', pdf_path))
        else:
            print("Platform not supported")
    except Exception as e:
        print(f"Error: {e}")

def open_excle_receipt_sum(filename):
    ospth = os.getcwd()
    pdf_path = f"{ospth}/{filename}"
    try:
        if sys.platform.startswith('win'):
            # Windows
            os.startfile(pdf_path)
        elif sys.platform.startswith('darwin'):
            # macOS
            subprocess.call(('open', pdf_path))
        elif sys.platform.startswith('linux'):
            # Linux
            subprocess.call(('xdg-open', pdf_path))
        else:
            print("Platform not supported")
    except Exception as e:
        print(f"Error: {e}")

def max_id(data,id_name):
    maxitem = ""
    maxvalue=0
    for s in data:
        if int(s[id_name]) >= maxvalue:
                maxvalue = int(s[id_name])
                maxitem = s
    return maxitem 

def Exec_Sql(sql):
    conn = sqlite3.connect("Bannkruann.db") 
    c = conn.cursor()
    c.execute(sql)
    result = c.fetchall()
    if len(result) > 0 :
        attb = [d[0] for d in c.description]
        jsonlist = [dict(zip(attb, item)) for item in result]
    else:
        jsonlist = result
    conn.commit()
    conn.close()
    #json_string = json.dumps(jsonlist, ensure_ascii=False, indent=2)
    return jsonlist

def receiptdocx(rid):
    sql = f"SELECT R.R_ID, R.Paid_Date, R.Amount, R.Cash, R.RNote, R.ExtraNote, S.S_ID, S.Name, S.SurName, S.Nick, P.M_Name, P.M_SurName, P.H_Adr, P.H_Mu, P.H_Tum, P.H_Amp, P.H_Prov, P.H_Post FROM Receipt as R JOIN Student as S ON S.S_ID = R.S_ID JOIN Parent as P ON P.P_ID = S.P_ID WHERE R.R_ID = {rid}"
    d = Exec_Sql(sql)
    d[0]['Amounttext']=bahttext(float(d[0]['Amount']))
    d[0]['Amount']=format(float(d[0]['Amount']),",.2f")
    d[0]['Paid_Date'] = thaidate(d[0]['Paid_Date'])

    # Check if ExtraNote contains "##" and split it
    if "##" in d[0]['RNote']:
        parts = d[0]['RNote'].split("##")
        d[0]['G_ID'] = parts[0].strip()  # Keep the first part in ExtraNote
        d[0]['RNote'] = parts[1].strip()  # Store the second part in c_id
    else:
        d[0]['G_ID'] = ""  # Default empty value if no "##" found

    doc = DocxTemplate('template.docx')
    doc.render(d[0])
    doc.save(f'receipt/{rid}.docx')
    
    #open_docx_file (f'receipt/{rid}.docx')   
    open_pdf_receipt_no(f'{rid}')   

def jsontolist (url):
    x = requests.get(url)
    datas = json.loads(x.text)
    return datas
    
def bahttext(amount):
    # Dictionary for Thai number names
    thai_numbers = {
        0: "ศูนย์",
        1: "หนึ่ง",
        2: "สอง",
        3: "สาม", 
        4: "สี่",
        5: "ห้า",
        6: "หก",
        7: "เจ็ด",
        8: "แปด",
        9: "เก้า"
    }
    
    # Dictionary for Thai position names
    thai_positions = {
        0: "",
        1: "สิบ",
        2: "ร้อย",
        3: "พัน",
        4: "หมื่น",
        5: "แสน",
        6: "ล้าน"
    }
    
    # Handle zero case
    if amount == 0:
        return "ศูนย์บาทถ้วน"
    
    # Handle negative amounts
    prefix = ""
    if amount < 0:
        prefix = "ลบ"
        amount = abs(amount)
    
    # Convert to string and split into integer and decimal parts
    amount_str = str(amount)
    if '.' in amount_str:
        integer_part, decimal_part = amount_str.split('.')
        # Ensure decimal is exactly 2 digits
        decimal_part = decimal_part[:2].ljust(2, '0')
    else:
        integer_part = amount_str
        decimal_part = "00"
    
    # Convert integer part to Thai text
    result = ""
    
    # Process millions and above (recurring pattern)
    if len(integer_part) > 6:
        million_cycles = (len(integer_part) - 1) // 6
        for i in range(million_cycles, 0, -1):
            start_pos = max(0, len(integer_part) - (i + 1) * 6)
            end_pos = len(integer_part) - i * 6
            segment = integer_part[start_pos:end_pos]
            
            # Skip if segment is all zeros
            if int(segment) == 0:
                continue
                
            segment_text = _convert_thai_segment(segment, thai_numbers, thai_positions)
            result += segment_text + "ล้าน"
        
        # Process the remaining part (less than a million)
        remaining = integer_part[-(6 * million_cycles):]
        if int(remaining) > 0:
            result += _convert_thai_segment(remaining, thai_numbers, thai_positions)
    else:
        result = _convert_thai_segment(integer_part, thai_numbers, thai_positions)
    
    # Add "baht"
    result += "บาท"
    
    # Add satang if not zero
    if decimal_part != "00":
        satang_text = _convert_thai_segment(decimal_part, thai_numbers, thai_positions)
        result += satang_text + "สตางค์"
    else:
        result += "ถ้วน"
    
    return prefix + result

def _convert_thai_segment(number_str, thai_numbers, thai_positions):
    """Helper function to convert a segment of digits to Thai text."""
    result = ""
    number_str = number_str.zfill(6)[-6:]  # Pad to handle positions correctly (max 6 digits per segment)
    
    for i, digit in enumerate(number_str):
        position = len(number_str) - i - 1
        if digit == '0':
            continue
            
        # Special case for 1 in tens position
        if position == 1 and digit == '1':
            result += thai_positions[position]
            continue
            
        # Special case for 2 in tens position
        if position == 1 and digit == '2':
            result += "ยี่" + thai_positions[position]
            continue
            
        # Special case for 1 in ones position
        if position == 0 and digit == '1':
            if number_str[-2] != '0':  # If tens place is not zero
                result += "เอ็ด"
            else:
                result += thai_numbers[int(digit)]
            continue
            
        result += thai_numbers[int(digit)] + thai_positions[position]
    
    return result


import datetime

# Function to convert Gregorian year to Thai Buddhist Era year
def thaidate(date_str):
    # Function to convert Gregorian year to Thai Buddhist Era year
    def gregorian_to_thai_year(year):
        return year + 543

    # Dictionary for Thai month abbreviations
    thai_months = {
        1: "ม.ค.",
        2: "ก.พ.",
        3: "มี.ค.",
        4: "เม.ย.",
        5: "พ.ค.",
        6: "มิ.ย.",
        7: "ก.ค.",
        8: "ส.ค.",
        9: "ก.ย.",
        10: "ต.ค.",
        11: "พ.ย.",
        12: "ธ.ค."
    }

    # Parse the date string into a datetime object
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    # Get the day, month, and year
    day = date_obj.day
    month = date_obj.month
    year = date_obj.year

    # Convert the year to Thai Buddhist Era
    thai_year = gregorian_to_thai_year(year) % 100  # Get the last two digits of the year

    # Format the date in the desired format
    formatted_date = f"{day} {thai_months[month]} {thai_year}"

    return formatted_date

def open_docx_file(filename):
    """
    Open a DOCX file with the default application (MS Word if installed)
    
    Args:
        filename (str): Name of the DOCX file in the same directory as this script
    """
    try:
        # Get the directory where the script is located
        script_dir = Path(__file__).parent.resolve()
        
        # Create the full path to the DOCX file
        docx_path = script_dir / filename
        
        # Check if the file exists
        if not docx_path.exists():
            print(f"Error: File '{filename}' does not exist in the script directory.")
            return False
        
        print(f"Opening '{filename}' with default application...")
        
        # Open the file with the default application
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.run(['open', docx_path])
        elif sys.platform.startswith('win'):  # Windows
            os.startfile(docx_path)
        else:  # Linux and other systems
            subprocess.run(['xdg-open', docx_path])
        
        print(f"Successfully opened '{filename}'")
        return True
    
    except Exception as e:
        print(f"Error opening file: {e}")
        return False


