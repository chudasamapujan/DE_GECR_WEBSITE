"""
Script to fix remaining .html URLs that were missed in the first update
"""

import os
import re

def fix_remaining_urls():
    """Fix the remaining .html URLs in templates"""
    
    # Additional URL mappings that were missed
    additional_mappings = {
        # Faculty URLs that don't have routes yet - map to placeholder or remove
        'faculty-events.html': '#',  # No faculty events route exists
    # faculty resources removed/archived
    'faculty-resources.html': '#',  # REMOVED: No faculty resources route exists
        'faculty-settings.html': '/shared/settings',  # Use shared settings
    }
    
    # Track changes
    updated_files = []
    total_replacements = 0
    
    # Process all HTML files in templates directory
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                try:
                    # Read file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    file_changes = 0
                    
                    # Apply additional URL mappings
                    for old_url, new_url in additional_mappings.items():
                        # Pattern to match href="old_url"
                        pattern = f'href="{re.escape(old_url)}"'
                        replacement = f'href="{new_url}"'
                        
                        count = len(re.findall(pattern, content))
                        if count > 0:
                            content = re.sub(pattern, replacement, content)
                            file_changes += count
                            print(f"  ✅ {file_path}: {old_url} → {new_url} ({count} replacements)")
                    
                    # Write back if changes were made
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.append(file_path)
                        total_replacements += file_changes
                    
                except Exception as e:
                    print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Additional URL Update Summary:")
    print(f"📁 Files updated: {len(updated_files)}")
    print(f"🔄 Total replacements: {total_replacements}")

if __name__ == '__main__':
    print("Fixing remaining .html URLs...")
    print("=" * 60)
    fix_remaining_urls()
    print(f"\n🎉 All remaining .html URLs fixed!")