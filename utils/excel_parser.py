"""
Excel Parser Utility for Attendance Upload
Parses Excel files to extract attendance data with dates and student information
"""

import openpyxl
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def parse_attendance_excel(file_path):
    """
    Parse an attendance Excel file and extract attendance records.
    
    Expected format:
    - First row: Headers (e.g., Roll No, Name, Date1, Date2, Date3, ...)
    - Date headers should be in format: DD/MM/YYYY or YYYY-MM-DD
    - Each subsequent row: student data with attendance status (P/A/L for Present/Absent/Late)
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        dict with:
            - 'dates': list of date objects
            - 'records': list of dicts with student_roll_no, date, status
            - 'errors': list of error messages
    """
    try:
        # Try using pandas for easier parsing
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        dates = []
        date_columns = []
        records = []
        errors = []
        
        # Identify date columns (anything that's not Roll No, Name, or other metadata)
        metadata_cols = ['roll no', 'roll_no', 'rollno', 'name', 'student name', 'roll number']
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower not in metadata_cols:
                # Try to parse as date
                try:
                    # Try different date formats
                    date_obj = None
                    col_str = str(col).strip()
                    
                    # Try parsing with pandas
                    try:
                        date_obj = pd.to_datetime(col_str, dayfirst=True).date()
                    except:
                        # Try common formats manually
                        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']:
                            try:
                                date_obj = datetime.strptime(col_str, fmt).date()
                                break
                            except:
                                continue
                    
                    if date_obj:
                        dates.append(date_obj)
                        date_columns.append(col)
                except Exception as e:
                    logger.warning(f"Could not parse column '{col}' as date: {e}")
        
        if not dates:
            errors.append("No valid date columns found in Excel file")
            return {'dates': [], 'records': [], 'errors': errors}
        
        # Find roll number column
        roll_col = None
        for col in df.columns:
            if str(col).lower().strip() in metadata_cols:
                roll_col = col
                break
        
        if not roll_col:
            errors.append("Could not find 'Roll No' column in Excel file")
            return {'dates': dates, 'records': [], 'errors': errors}
        
        # Extract attendance records
        for idx, row in df.iterrows():
            try:
                roll_no = str(row[roll_col]).strip()
                
                # Skip empty rows or header rows
                if pd.isna(roll_no) or roll_no.lower() in ['roll no', 'roll_no', 'nan', '']:
                    continue
                
                # For each date column, extract attendance status
                for date_obj, date_col in zip(dates, date_columns):
                    status_val = str(row[date_col]).strip().upper() if pd.notna(row[date_col]) else ''
                    
                    # Map status values
                    status = None
                    if status_val in ['P', 'PRESENT', '1', 'Y', 'YES']:
                        status = 'Present'
                    elif status_val in ['A', 'ABSENT', '0', 'N', 'NO']:
                        status = 'Absent'
                    elif status_val in ['L', 'LATE', 'T', 'TARDY']:
                        status = 'Late'
                    
                    if status:
                        records.append({
                            'student_roll_no': roll_no,
                            'date': date_obj,
                            'status': status
                        })
            except Exception as e:
                errors.append(f"Error processing row {idx + 2}: {str(e)}")
        
        return {
            'dates': dates,
            'records': records,
            'errors': errors,
            'total_students': len(df) - 1 if len(df) > 1 else 0,
            'total_records': len(records)
        }
        
    except Exception as e:
        logger.error(f"Error parsing Excel file: {str(e)}")
        return {
            'dates': [],
            'records': [],
            'errors': [f"Failed to parse Excel file: {str(e)}"]
        }


def parse_attendance_excel_openpyxl(file_path):
    """
    Alternative parser using openpyxl directly (more control over formatting).
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Same dict format as parse_attendance_excel
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        
        dates = []
        date_columns = []
        records = []
        errors = []
        
        # Read header row
        headers = []
        for cell in sheet[1]:
            headers.append(cell.value)
        
        # Identify date columns and roll no column
        roll_col_idx = None
        metadata_cols = ['roll no', 'roll_no', 'rollno', 'name', 'student name', 'roll number']
        
        for idx, header in enumerate(headers):
            if header:
                header_lower = str(header).lower().strip()
                if header_lower in metadata_cols:
                    roll_col_idx = idx
                else:
                    # Try to parse as date
                    try:
                        header_str = str(header).strip()
                        date_obj = None
                        
                        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']:
                            try:
                                date_obj = datetime.strptime(header_str, fmt).date()
                                break
                            except:
                                continue
                        
                        if date_obj:
                            dates.append(date_obj)
                            date_columns.append(idx)
                    except:
                        pass
        
        if roll_col_idx is None:
            errors.append("Could not find 'Roll No' column")
            return {'dates': dates, 'records': [], 'errors': errors}
        
        if not dates:
            errors.append("No valid date columns found")
            return {'dates': dates, 'records': [], 'errors': errors}
        
        # Process data rows
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            try:
                roll_no = str(row[roll_col_idx].value).strip() if row[roll_col_idx].value else ''
                
                if not roll_no or roll_no.lower() in ['roll no', 'none']:
                    continue
                
                for date_obj, col_idx in zip(dates, date_columns):
                    status_val = str(row[col_idx].value).strip().upper() if row[col_idx].value else ''
                    
                    status = None
                    if status_val in ['P', 'PRESENT', '1', 'Y', 'YES']:
                        status = 'Present'
                    elif status_val in ['A', 'ABSENT', '0', 'N', 'NO']:
                        status = 'Absent'
                    elif status_val in ['L', 'LATE', 'T', 'TARDY']:
                        status = 'Late'
                    
                    if status:
                        records.append({
                            'student_roll_no': roll_no,
                            'date': date_obj,
                            'status': status
                        })
            except Exception as e:
                errors.append(f"Error processing row {row_idx}: {str(e)}")
        
        return {
            'dates': dates,
            'records': records,
            'errors': errors,
            'total_records': len(records)
        }
        
    except Exception as e:
        logger.error(f"Error parsing Excel file with openpyxl: {str(e)}")
        return {
            'dates': [],
            'records': [],
            'errors': [f"Failed to parse Excel file: {str(e)}"]
        }
