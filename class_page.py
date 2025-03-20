import flet as ft
import sqlite3
import bkn_fn
import pandas as pd

# Constants
TEXT_SIZE = 14
FIELD_HEIGHT = 40

def containers(page):
    page.fonts = bkn_fn.pagefonts
    # Fetch course data with student counts in a single query
    course_query = """
    SELECT 
        c.ID,
        c.C_ID,
        c.Class,
        c.Day,
        c.Period,
        c.Subject,
        c.Cost,
        COALESCE((
            SELECT COUNT(e.S_ID)
            FROM Enroll e
            WHERE e.C_ID = c.C_ID
            GROUP BY e.C_ID
        ), 0) AS number_of_students
    FROM Course c
    ORDER BY c.ID DESC
    """
    course_data = bkn_fn.Exec_Sql(course_query)
    
    # State variables
    filtered_data = course_data.copy()  # For filtering
    table = None  # Define table as a nonlocal variable
    student_list_container = None  # Container for displaying the student list
    last_clicked_c_id = None  # Track the last clicked C_ID to toggle visibility
    current_students = []  # Store the current student list for export
    snack_bar = ft.SnackBar(content=ft.Text(""))  # Manually managed SnackBar

    # Add the SnackBar to the page
    page.snack_bar = snack_bar
    page.overlay.append(snack_bar)

    # File picker for saving the Excel file
    file_picker = ft.FilePicker(on_result=lambda e: save_to_excel(e))

    # Add the file picker to the page (required for it to work)
    page.overlay.append(file_picker)

    # Define refresh_table
    def refresh_table():
        nonlocal table
        table = build_table()  # Update table
        table_container.content = table
        page.update()

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

    # Function to export student list to Excel
    def save_to_excel(e):
        if e.path:
            try:
                # Create a DataFrame from the current student list
                df = pd.DataFrame(current_students, columns=["Name", "SurName", "Nick"])
                # Rename columns for the Excel file (in Thai)
                df.columns = ["ชื่อ", "นามสกุล", "ชื่อเล่น"]
                # Save the DataFrame to an Excel file
                output_path = f"{e.path}.xlsx"
                df.to_excel(output_path, index=False)
                # Update and show the SnackBar with success message
                snack_bar.content = ft.Text(f"Exported student list to {output_path}")
                snack_bar.bgcolor = ft.colors.GREEN_700
                snack_bar.open = True
                page.update()
            except ModuleNotFoundError as e:
                # Update and show the SnackBar with openpyxl error message
                snack_bar.content = ft.Text("Error: Please install 'openpyxl' to export to Excel. Run 'pip install openpyxl'")
                snack_bar.bgcolor = ft.colors.RED_700
                snack_bar.open = True
                page.update()
            except Exception as e:
                # Update and show the SnackBar with general error message
                snack_bar.content = ft.Text(f"Error exporting to Excel: {str(e)}")
                snack_bar.bgcolor = ft.colors.RED_700
                snack_bar.open = True
                page.update()
        else:
            # Update and show the SnackBar with cancellation message
            snack_bar.content = ft.Text("Export cancelled")
            snack_bar.bgcolor = ft.colors.RED_700
            snack_bar.open = True
            page.update()

    # Function to initiate the export process
    def export_to_excel():
        if not current_students:
            snack_bar.content = ft.Text("No student data to export")
            snack_bar.bgcolor = ft.colors.RED_700
            snack_bar.open = True
            page.update()
            return
        # Open the file picker to let the user choose a save location
        file_picker.save_file(
            file_name=f"students_course_{last_clicked_c_id}.xlsx",
            allowed_extensions=["xlsx"]
        )

    # Function to fetch and display student list for a given C_ID
    def show_student_list(c_id):
        nonlocal student_list_container, last_clicked_c_id, current_students

        # If the same button is clicked again, hide the student list
        if last_clicked_c_id == c_id and student_list_container.visible:
            student_list_container.visible = False
            last_clicked_c_id = None
            page.update()
            return

        # Update the last clicked C_ID
        last_clicked_c_id = c_id

        # Construct the SQL query with the C_ID value directly embedded
        # Since C_ID is a text field, we wrap it in single quotes
        student_query = f"""
        SELECT 
            s.S_ID,
            s.Name,
            s.SurName,
            s.Nick
        FROM Student s
        JOIN Enroll e ON s.S_ID = e.S_ID
        WHERE e.C_ID = '{c_id}'
        """
        students = bkn_fn.Exec_Sql(student_query)  # Pass only the query string

        # Store the students for export
        current_students = students

        # Clear previous content in the student list container
        student_list_container.content.controls.clear()

        if not students:
            # If no students are enrolled, show a message
            student_list_container.content.controls.append(
                ft.Text(f"No students enrolled in course {c_id}", size=16, color=bkn_fn.navy_blue)
            )
        else:
            # Create a DataTable to display the student list (Name, SurName, Nick only)
            student_table = ft.DataTable(
    column_spacing=10,
    columns=[
        ft.DataColumn(ft.Text("ลำดับ", size=TEXT_SIZE)),
        ft.DataColumn(ft.Text("ชื่อ", size=TEXT_SIZE)),
        ft.DataColumn(ft.Text("นามสกุล", size=TEXT_SIZE)),
        ft.DataColumn(ft.Text("ชื่อเล่น", size=TEXT_SIZE)),
    ],
    rows=[
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(i + 1), size=TEXT_SIZE)),  # i + 1 starts from 1 instead of 0
                ft.DataCell(ft.Text(student["Name"], size=TEXT_SIZE)),
                ft.DataCell(ft.Text(student["SurName"], size=TEXT_SIZE)),
                ft.DataCell(ft.Text(student["Nick"], size=TEXT_SIZE)),
            ]
        ) for i, student in enumerate(students)
    ]
)
            # Add the student table and an "Export to Excel" button
            student_list_container.content.controls.append(
                ft.Column([
                    ft.Container(
                        bgcolor=bkn_fn.navy_blue,
                        height=40,
                        content=ft.Row(
                            [ft.Text(f":::รายชื่อนักเรียน ห้อง -- {c_id} -- :::", color=bkn_fn.yellow, size=22,font_family=bkn_fn.menu_font)],
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ),
                    student_table,
                    ft.Row([
                        ft.ElevatedButton(
                            "Export to Excel",
                            bgcolor=bkn_fn.navy_blue,
                            color=bkn_fn.yellow,
                            height=30,
                            on_click=lambda e: export_to_excel()
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ]
                )
            )
            

        # Make the student list container visible
        student_list_container.visible = True
        page.update()

    # Build the table
    def build_table():
        return ft.DataTable(
            column_spacing=10,
            columns=[
                ft.DataColumn(ft.Text("รหัส", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("ห้องเรียน", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("วันเรียน", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("วิชา", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("จำนวนนักเรียน", size=TEXT_SIZE)),
                ft.DataColumn(ft.Text("", size=TEXT_SIZE, text_align=ft.TextAlign.CENTER)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["C_ID"], size=TEXT_SIZE)),
                        ft.DataCell(ft.Text(item["Class"], size=TEXT_SIZE)),
                        ft.DataCell(ft.Text(item["Day"], size=TEXT_SIZE)),
                        ft.DataCell(ft.Text(item["Subject"], size=TEXT_SIZE)),
                        ft.DataCell(ft.Text(str(item["number_of_students"]),text_align=ft.TextAlign.CENTER, size=TEXT_SIZE)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Student List",
                                        bgcolor=bkn_fn.navy_blue,
                                        color=bkn_fn.yellow,
                                        height=30,
                                        on_click=lambda e, c_id=item["C_ID"]: show_student_list(c_id)  # Pass the C_ID to the function
                                    ),
                                ],
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ),
                    ]
                ) for i, item in enumerate(filtered_data)
            ],
        )

    # Filter field with on_change filtering
    filter_field = ft.TextField(hint_text="Filter by C_ID or Class", text_size=TEXT_SIZE, height=FIELD_HEIGHT, width=200, on_change=filter_records)

    # Table container
    table_container = ft.Container(content=build_table(), expand=True)

    # Student list container (initially hidden)
    student_list_container = ft.Container(
        content=ft.Column([]),  # Empty column initially
        #padding=ft.padding.all(10),
        margin=ft.margin.only(10, 0, 0, 10),
        border_radius=15,
        bgcolor=bkn_fn.grey,
        visible=False  # Hidden by default
    )

    # Main container layout
    return ft.Column(controls=[
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=bkn_fn.yellow,
                        height=40,
                        content=ft.Row(
                            [ft.Text("::: ข้อมูลคอร์สเรียน :::", color=bkn_fn.navy_blue, size=22, font_family=bkn_fn.menu_font)],
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Row([filter_field], spacing=10),
                    ft.Column([table_container], scroll="auto", height=300),
                    ft.Text(f"     Showing 1-{len(filtered_data)} of {len(course_data)} records", size=12, color="#757575"),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.only(0, 0, 0, 10),
            margin=ft.margin.only(10, 0, 10, 0),
            border_radius=15,
            bgcolor=bkn_fn.grey,
        ),
        student_list_container  # Add the student list container below the course details
    ])

def main(page: ft.Page):
    page.title = "Course Management"
    page.bgcolor = "#F5F5F5"
    con = ft.Column([containers(page)],scroll='auto')
    page.add(con)
    page.scroll = True

if __name__ == "__main__":
    ft.app(target=main)