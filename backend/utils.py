from flask import current_app
from flask_mail import Message, Mail
import os
from jinja2 import Environment, FileSystemLoader

def send_email(to, subject, template=None, text_body=None, html_body=None, **kwargs):
    """Send email using Flask-Mail"""
    try:
        mail = current_app.extensions.get('mail')
        if not mail:
            raise Exception("Mail extension not initialized")
        
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[to] if isinstance(to, str) else to
        )
        
        if template:
            # Load email template
            template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'emails')
            env = Environment(loader=FileSystemLoader(template_dir))
            template_obj = env.get_template(template)
            msg.html = template_obj.render(**kwargs)
            
            # Generate text version from HTML (basic)
            import re
            text_content = re.sub(r'<[^>]+>', '', msg.html)
            msg.body = text_content
        else:
            msg.body = text_body
            if html_body:
                msg.html = html_body
        
        mail.send(msg)
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        raise e

def format_response(success, message, status_code=200, data=None):
    """Format API response"""
    response = {
        'success': success,
        'message': message
    }
    
    if data:
        response['data'] = data
    
    return response, status_code

def generate_otp(length=6):
    """Generate numeric OTP"""
    import random
    import string
    return ''.join(random.choices(string.digits, k=length))

def validate_file_upload(file, allowed_extensions=None, max_size_mb=5):
    """Validate uploaded file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if allowed_extensions:
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_extension not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check file size (this is a basic check, actual size checking should be done during upload)
    if hasattr(file, 'content_length') and file.content_length:
        if file.content_length > max_size_mb * 1024 * 1024:
            return False, f"File size exceeds {max_size_mb}MB limit"
    
    return True, "File is valid"

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    import re
    import uuid
    
    # Get file extension
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex[:8]}_{re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)}"
    
    return unique_filename

def paginate_results(collection, page=1, per_page=10, sort_by=None, sort_order=-1, filter_query=None):
    """Paginate database results"""
    try:
        # Calculate skip value
        skip = (page - 1) * per_page
        
        # Build query
        query = filter_query or {}
        
        # Get total count
        total = collection.count_documents(query)
        
        # Build aggregation pipeline
        pipeline = [{'$match': query}]
        
        if sort_by:
            pipeline.append({'$sort': {sort_by: sort_order}})
        
        pipeline.extend([
            {'$skip': skip},
            {'$limit': per_page}
        ])
        
        # Execute query
        results = list(collection.aggregate(pipeline))
        
        # Convert ObjectId to string
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'results': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }
        
    except Exception as e:
        raise Exception(f"Pagination error: {e}")

def format_date(date_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string"""
    if not date_obj:
        return None
    return date_obj.strftime(format_str)

def parse_date(date_str, format_str='%Y-%m-%d'):
    """Parse string to datetime object"""
    from datetime import datetime
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def generate_academic_year():
    """Generate current academic year"""
    from datetime import datetime
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Academic year starts in July
    if current_month >= 7:
        start_year = current_year
        end_year = current_year + 1
    else:
        start_year = current_year - 1
        end_year = current_year
    
    return f"{start_year}-{end_year}"

def validate_enrollment_number(enrollment_number, year_digits=2):
    """Validate enrollment number format"""
    import re
    
    # Pattern: YYXXXX (YY = year, XXXX = sequence)
    pattern = f"^\\d{{{year_digits}}}\\d{{4}}$"
    
    if not re.match(pattern, enrollment_number):
        return False, f"Invalid enrollment number format. Expected: {year_digits} year digits + 4 sequence digits"
    
    return True, "Valid enrollment number"

def validate_faculty_id(faculty_id):
    """Validate faculty ID format"""
    import re
    
    # Pattern: FAC followed by 4-6 digits
    pattern = "^FAC\\d{4,6}$"
    
    if not re.match(pattern, faculty_id):
        return False, "Invalid faculty ID format. Expected: FAC followed by 4-6 digits"
    
    return True, "Valid faculty ID"