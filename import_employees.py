#!/usr/bin/env python3
"""
Import employee data from Excel file to database
Supports: employee_id, name, department, role
"""

import sys
import asyncio
import pandas as pd
sys.path.append('.')

from db.database import init_db_pool, close_db_pool, get_db_connection

async def import_employees_from_excel(excel_file_path: str):
    """Import employee data from Excel file"""

    print("=" * 70)
    print("📊 IMPORTING EMPLOYEE DATA FROM EXCEL")
    print("=" * 70)

    # Initialize database pool
    print("\n🔌 Initializing database connection pool...")
    await init_db_pool()

    try:
        # Read Excel file
        print(f"\n📖 Reading Excel file: {excel_file_path}")

        try:
            df = pd.read_excel(excel_file_path)
        except Exception as e:
            print(f"❌ Failed to read Excel file: {e}")
            print("\nMake sure you have openpyxl installed:")
            print("  pip install openpyxl")
            return False

        print(f"✅ Found {len(df)} rows in Excel file")

        # Display column names
        print(f"\n📋 Columns found: {list(df.columns)}")

        # Try to detect column names (case-insensitive, flexible naming)
        column_mapping = {}

        # Detect employee_id column
        for col in df.columns:
            col_lower = str(col).lower()
            if 'employee' in col_lower and ('id' in col_lower or 'number' in col_lower or 'номер' in col_lower):
                column_mapping['employee_id'] = col
            elif 'табельный' in col_lower:
                column_mapping['employee_id'] = col
            elif 'name' in col_lower or 'имя' in col_lower or 'фио' in col_lower:
                column_mapping['name'] = col
            elif 'department' in col_lower or 'отдел' in col_lower or 'dept' in col_lower:
                column_mapping['department'] = col
            elif 'role' in col_lower or 'роль' in col_lower or 'должность' in col_lower:
                column_mapping['role'] = col

        print(f"\n🔍 Detected column mapping:")
        for key, value in column_mapping.items():
            print(f"   {key}: '{value}'")

        # Validate required columns
        if 'employee_id' not in column_mapping:
            print("\n❌ Error: Could not find employee_id column")
            print("Please ensure your Excel has a column like:")
            print("  - 'Employee ID' or 'Employee Number'")
            print("  - 'Табельный номер'")
            return False

        # Connect to database
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:

                # First, ensure departments exist
                departments_created = set()

                print("\n📦 Processing departments...")
                for _, row in df.iterrows():
                    if 'department' in column_mapping and pd.notna(row[column_mapping['department']]):
                        dept_name = str(row[column_mapping['department']]).strip()
                        if dept_name and dept_name not in departments_created:
                            await cur.execute(
                                """INSERT INTO departments (name, description)
                                   VALUES (%s, %s)
                                   ON CONFLICT (name) DO NOTHING""",
                                (dept_name, f"Imported from Excel")
                            )
                            departments_created.add(dept_name)

                await conn.commit()
                print(f"✅ Processed {len(departments_created)} unique departments")

                # Now import employees
                print("\n👥 Importing employees...")

                imported_count = 0
                updated_count = 0
                skipped_count = 0

                for idx, row in df.iterrows():
                    try:
                        # Get employee_id (required)
                        employee_id = str(row[column_mapping['employee_id']]).strip()

                        if not employee_id or employee_id.lower() in ['nan', 'none', '']:
                            skipped_count += 1
                            continue

                        # Get other fields (optional)
                        name = str(row[column_mapping['name']]).strip() if 'name' in column_mapping and pd.notna(row[column_mapping['name']]) else employee_id
                        department_name = str(row[column_mapping['department']]).strip() if 'department' in column_mapping and pd.notna(row[column_mapping['department']]) else None
                        role = str(row[column_mapping['role']]).strip().lower() if 'role' in column_mapping and pd.notna(row[column_mapping['role']]) else 'employee'

                        # Validate role
                        if role not in ['employee', 'hr', 'manager']:
                            print(f"⚠️  Row {idx+2}: Invalid role '{role}' for {employee_id}, defaulting to 'employee'")
                            role = 'employee'

                        # Get department_id if department specified
                        department_id = None
                        if department_name:
                            await cur.execute(
                                "SELECT id FROM departments WHERE name = %s",
                                (department_name,)
                            )
                            dept_result = await cur.fetchone()
                            if dept_result:
                                department_id = dept_result[0]

                        # Check if user exists
                        await cur.execute(
                            "SELECT id FROM users WHERE phone = %s",
                            (employee_id,)
                        )
                        existing_user = await cur.fetchone()

                        if existing_user:
                            # Update existing user
                            await cur.execute(
                                """UPDATE users
                                   SET name = %s, role = %s, department_id = %s
                                   WHERE phone = %s""",
                                (name, role, department_id, employee_id)
                            )
                            updated_count += 1
                        else:
                            # Insert new user
                            await cur.execute(
                                """INSERT INTO users (name, surname, phone, company, job_title, role, department_id)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (name, '', employee_id, 'Halyk Bank', role.title(), role, department_id)
                            )
                            imported_count += 1

                        if (imported_count + updated_count) % 10 == 0:
                            print(f"   Processed {imported_count + updated_count} employees...")

                    except Exception as e:
                        print(f"⚠️  Row {idx+2}: Error processing employee: {e}")
                        skipped_count += 1
                        continue

                await conn.commit()

                print(f"\n✅ Import complete!")
                print(f"   📥 New employees imported: {imported_count}")
                print(f"   🔄 Existing employees updated: {updated_count}")
                print(f"   ⏭️  Rows skipped: {skipped_count}")

                # Show summary
                await cur.execute("SELECT COUNT(*) FROM users")
                total_users = (await cur.fetchone())[0]

                await cur.execute("SELECT COUNT(*) FROM departments")
                total_depts = (await cur.fetchone())[0]

                print(f"\n📊 Database Summary:")
                print(f"   Total users: {total_users}")
                print(f"   Total departments: {total_depts}")

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close database pool
        print("\n🔌 Closing database connection pool...")
        await close_db_pool()

    print("\n" + "=" * 70)
    print("✅ IMPORT COMPLETE")
    print("=" * 70)
    print("\nYou can now:")
    print("  1. Run the application: python main.py")
    print("  2. Employees can log in with their employee_id and AD password")
    print("  3. Their role and department will be automatically loaded")
    print("\n")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_employees.py <excel_file_path>")
        print("\nExample:")
        print("  python import_employees.py employees.xlsx")
        print("  python import_employees.py /path/to/employees.xlsx")
        print("\nExpected Excel columns:")
        print("  - Employee ID / Табельный номер (required)")
        print("  - Name / Имя (optional)")
        print("  - Department / Отдел (optional)")
        print("  - Role / Роль (optional: employee, hr, manager)")
        sys.exit(1)

    excel_file = sys.argv[1]

    try:
        result = asyncio.run(import_employees_from_excel(excel_file))
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
