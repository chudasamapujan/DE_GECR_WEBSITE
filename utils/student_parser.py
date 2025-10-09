"""
Student Data Parser Utility
Parses Excel files to extract student information for bulk upload
"""

import openpyxl
import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)


def parse_students_excel(file_path):
    """
    Parse a student Excel file and extract student records.
    
    Expected format:
    - Columns: Roll No, Name, Email, Password, Department, Semester, Phone
    - First row: Headers
    - Each subsequent row: student data
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        dict with:
            - 'students': list of dicts with student data
            - 'errors': list of error messages
    """
    try:
        # Try using pandas for easier parsing
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        students = []
        errors = []
        
        # Define expected columns and their variations
        column_mappings = {
            'roll_no': ['roll no', 'roll_no', 'rollno', 'roll number', 'roll'],
            'name': ['name', 'student name', 'full name'],
            'email': ['email', 'e-mail', 'email id'],
            'password': ['password', 'pwd', 'pass'],
            'department': ['department', 'dept', 'branch'],
            'semester': ['semester', 'sem'],
            'phone': ['phone', 'mobile', 'contact', 'phone number', 'mobile number']
        }
        
        # Find actual column names
        actual_columns = {}
        for field, variations in column_mappings.items():
            for variation in variations:
                if variation in df.columns:
                    actual_columns[field] = variation
                    break
        
        # Check required columns
        required = ['roll_no', 'name', 'email']
        missing_cols = [col for col in required if col not in actual_columns]
        
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return {'students': [], 'errors': errors}
        
        # Extract student records
        for idx, row in df.iterrows():
            try:
                # Skip empty rows
                roll_no = str(row[actual_columns['roll_no']]).strip() if 'roll_no' in actual_columns else ''
                if pd.isna(roll_no) or roll_no.lower() in ['nan', 'roll no', '']:
                    continue
                
                name = str(row[actual_columns['name']]).strip() if 'name' in actual_columns else ''
                if pd.isna(name) or name.lower() in ['nan', 'name', '']:
                    errors.append(f"Row {idx + 2}: Name is required")
                    continue
                
                email = str(row[actual_columns['email']]).strip() if 'email' in actual_columns else ''
                if pd.isna(email) or email.lower() in ['nan', 'email', '']:
                    errors.append(f"Row {idx + 2}: Email is required")
                    continue
                
                # Validate email format
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                    errors.append(f"Row {idx + 2}: Invalid email format: {email}")
                    continue
                
                # Get optional fields
                password = str(row[actual_columns.get('password', 'password')]).strip() if 'password' in actual_columns and pd.notna(row.get(actual_columns.get('password'))) else 'student123'
                
                department = str(row[actual_columns.get('department', 'department')]).strip() if 'department' in actual_columns and pd.notna(row.get(actual_columns.get('department'))) else None
                
                semester = None
                if 'semester' in actual_columns and pd.notna(row.get(actual_columns.get('semester'))):
                    try:
                        semester = int(row[actual_columns['semester']])
                    except:
                        pass
                
                phone = str(row[actual_columns.get('phone', 'phone')]).strip() if 'phone' in actual_columns and pd.notna(row.get(actual_columns.get('phone'))) else None
                if phone and phone.lower() == 'nan':
                    phone = None
                
                student_data = {
                    'roll_no': roll_no,
                    'name': name,
                    'email': email,
                    'password': password,
                    'department': department,
                    'semester': semester,
                    'phone': phone
                }
                
                students.append(student_data)
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: Error processing - {str(e)}")
        
        return {
            'students': students,
            'errors': errors,
            'total_rows': len(df),
            'total_students': len(students)
        }
        
    except Exception as e:
        logger.error(f"Error parsing Excel file: {str(e)}")
        return {
            'students': [],
            'errors': [f"Failed to parse Excel file: {str(e)}"]
        }


def parse_students_excel_openpyxl(file_path):
    """
    Alternative parser using openpyxl directly.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Same dict format as parse_students_excel
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        
        students = []
        errors = []
        
        # Read header row
        headers = []
        for cell in sheet[1]:
            if cell.value:
                headers.append(str(cell.value).strip().lower())
            else:
                headers.append(None)
        
        # Find column indices
        column_mappings = {
            'roll_no': ['roll no', 'roll_no', 'rollno', 'roll number'],
            'name': ['name', 'student name'],
            'email': ['email', 'e-mail'],
            'password': ['password', 'pwd'],
            'department': ['department', 'dept'],
            'semester': ['semester', 'sem'],
            'phone': ['phone', 'mobile', 'contact']
        }
        
        column_indices = {}
        for field, variations in column_mappings.items():
            for idx, header in enumerate(headers):
                if header and header in variations:
                    column_indices[field] = idx
                    break
        
        # Check required columns
        required = ['roll_no', 'name', 'email']
        missing = [col for col in required if col not in column_indices]
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return {'students': [], 'errors': errors}
        
        # Process data rows
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            try:
                roll_no = str(row[column_indices['roll_no']].value).strip() if row[column_indices['roll_no']].value else ''
                if not roll_no or roll_no.lower() == 'none':
                    continue
                
                name = str(row[column_indices['name']].value).strip() if row[column_indices['name']].value else ''
                if not name:
                    errors.append(f"Row {row_idx}: Name is required")
                    continue
                
                email = str(row[column_indices['email']].value).strip() if row[column_indices['email']].value else ''
                if not email:
                    errors.append(f"Row {row_idx}: Email is required")
                    continue
                
                # Optional fields
                password = str(row[column_indices.get('password', 0)].value).strip() if column_indices.get('password') and row[column_indices.get('password')].value else 'student123'
                department = str(row[column_indices.get('department', 0)].value).strip() if column_indices.get('department') and row[column_indices.get('department')].value else None
                
                semester = None
                if column_indices.get('semester') and row[column_indices.get('semester')].value:
                    try:
                        semester = int(row[column_indices['semester']].value)
                    except:
                        pass
                
                phone = str(row[column_indices.get('phone', 0)].value).strip() if column_indices.get('phone') and row[column_indices.get('phone')].value else None
                
                students.append({
                    'roll_no': roll_no,
                    'name': name,
                    'email': email,
                    'password': password,
                    'department': department,
                    'semester': semester,
                    'phone': phone
                })
                
            except Exception as e:
                errors.append(f"Row {row_idx}: {str(e)}")
        
        return {
            'students': students,
            'errors': errors,
            'total_students': len(students)
        }
        
    except Exception as e:
        logger.error(f"Error parsing Excel file with openpyxl: {str(e)}")
        return {
            'students': [],
            'errors': [f"Failed to parse Excel file: {str(e)}"]
        }
