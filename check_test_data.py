#!/usr/bin/env python3
"""
Check if test data exists in the database
"""

import asyncio
from db.database import init_db_pool, get_db_connection

async def check_test_data():
    """Check if required test data tables have content"""

    print("\n" + "=" * 80)
    print("CHECKING TEST DATA IN HR SCHEMA")
    print("=" * 80 + "\n")

    await init_db_pool()

    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Check profiles
                await cur.execute("SELECT COUNT(*) FROM hr.profiles")
                profiles_count = (await cur.fetchone())[0]
                print(f"✓ Profiles: {profiles_count} records")

                # Check specializations
                await cur.execute("SELECT COUNT(*) FROM hr.specializations")
                spec_count = (await cur.fetchone())[0]
                print(f"✓ Specializations: {spec_count} records")

                # Check competencies
                await cur.execute("SELECT COUNT(*) FROM hr.competencies")
                comp_count = (await cur.fetchone())[0]
                print(f"✓ Competencies: {comp_count} records")

                # Check topics
                await cur.execute("SELECT COUNT(*) FROM hr.topics")
                topics_count = (await cur.fetchone())[0]
                print(f"✓ Topics: {topics_count} records")

                # Check questions
                await cur.execute("SELECT COUNT(*) FROM hr.questions")
                questions_count = (await cur.fetchone())[0]
                print(f"✓ Questions: {questions_count} records")

                print("\n" + "=" * 80)
                print("DIAGNOSIS:")
                print("=" * 80)

                if profiles_count == 0 or spec_count == 0:
                    print("\n❌ PROBLEM: No profiles or specializations found!")
                    print("   You need to populate these tables with test data.")
                    print("   The application cannot generate tests without this data.")
                elif comp_count == 0 or topics_count == 0 or questions_count == 0:
                    print("\n❌ PROBLEM: No competencies, topics, or questions found!")
                    print("   You need to populate these tables to generate tests.")
                    print("   Each specialization needs:")
                    print("   - Competencies (skills to test)")
                    print("   - Topics (for each competency)")
                    print("   - Questions (for each topic)")
                else:
                    print("\n✅ All required tables have data!")
                    print("   The test system should work correctly.")

                    # Show sample data
                    print("\n" + "=" * 80)
                    print("SAMPLE DATA:")
                    print("=" * 80)

                    await cur.execute("SELECT id, name FROM hr.profiles LIMIT 3")
                    profiles = await cur.fetchall()
                    print("\nProfiles:")
                    for p in profiles:
                        print(f"  - {p[0]}: {p[1]}")

                    await cur.execute("SELECT id, name, profile_id FROM hr.specializations LIMIT 3")
                    specs = await cur.fetchall()
                    print("\nSpecializations:")
                    for s in specs:
                        print(f"  - {s[0]}: {s[1]} (profile_id: {s[2]})")

                    await cur.execute("SELECT id, name, specialization_id FROM hr.competencies LIMIT 3")
                    comps = await cur.fetchall()
                    print("\nCompetencies:")
                    for c in comps:
                        print(f"  - {c[0]}: {c[1]} (specialization_id: {c[2]})")

                    await cur.execute("SELECT id, name, competency_id FROM hr.topics LIMIT 3")
                    topics = await cur.fetchall()
                    print("\nTopics:")
                    for t in topics:
                        print(f"  - {t[0]}: {t[1]} (competency_id: {t[2]})")

                    await cur.execute("SELECT COUNT(*), level FROM hr.questions GROUP BY level")
                    q_by_level = await cur.fetchall()
                    print("\nQuestions by level:")
                    for q in q_by_level:
                        print(f"  - {q[1]}: {q[0]} questions")

                print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_test_data())
