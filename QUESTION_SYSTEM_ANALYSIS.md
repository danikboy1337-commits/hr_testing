# 📚 Question System - Complete Analysis

## Overview

Your HR testing platform uses a sophisticated **hierarchical question structure** with **adaptive topic selection** and **AI-generated content**. This document explains how questions are stored and selected for each test.

---

## 🗂️ Database Structure

### Hierarchical Organization

```
Profile (Профессия)
  └── Specialization (Специализация)
       └── Competency (Компетенция) [with importance rating]
            └── Topic (Тема) [4 topics per competency]
                 └── Question (Вопрос) [3 questions per topic: Junior/Middle/Senior]
```

### Database Tables

#### 1. **`specializations`** (Специализации)
Stores the specializations for each profile (e.g., "Java Backend Developer", "Frontend Developer")

```sql
CREATE TABLE specializations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id),
    name VARCHAR(255) NOT NULL
);
```

#### 2. **`competencies`** (Компетенции)
Stores competencies for each specialization with importance rating

```sql
CREATE TABLE competencies (
    id SERIAL PRIMARY KEY,
    specialization_id INTEGER REFERENCES specializations(id),
    name VARCHAR(255) NOT NULL,
    importance INTEGER DEFAULT 50  -- Range: 0-100 (CORE vs DAILY)
);
```

**Example:**
- "Навыки Java" [CORE 90%] → importance = 90
- "CI/CD процессы" [DAILY 60%] → importance = 60

#### 3. **`topics`** (Темы)
Stores 4 topics per competency

```sql
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    competency_id INTEGER REFERENCES competencies(id),
    name VARCHAR(255) NOT NULL
);
```

**Example Topics for "Навыки Java":**
- "Основы синтаксиса Java"
- "Многопоточность и конкурентность"
- "Java Collections Framework"
- "Stream API и функциональное программирование"

#### 4. **`questions`** (Вопросы)
Stores 3 questions per topic (one for each level: Junior, Middle, Senior)

```sql
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    level VARCHAR(50) NOT NULL,           -- 'Junior', 'Middle', or 'Senior'
    question_text TEXT NOT NULL,          -- The question
    var_1 TEXT NOT NULL,                  -- Option 1
    var_2 TEXT NOT NULL,                  -- Option 2
    var_3 TEXT NOT NULL,                  -- Option 3
    var_4 TEXT NOT NULL,                  -- Option 4
    correct_answer INTEGER NOT NULL       -- 1, 2, 3, or 4
);
```

**Example Question Structure:**
```json
{
  "level": "Middle",
  "question_text": "В чем основное различие между HashMap и ConcurrentHashMap?",
  "var_1": "ConcurrentHashMap синхронизирован, HashMap - нет",
  "var_2": "ConcurrentHashMap использует сегментацию для потокобезопасности",
  "var_3": "HashMap быстрее в многопоточных приложениях",
  "var_4": "ConcurrentHashMap не допускает null ключей",
  "correct_answer": 2
}
```

---

## 🎯 Question Selection Process

### Overview

When a user starts a test, the system generates a **unique set of 8 topics** and serves **24 questions** (8 topics × 3 levels).

### Step-by-Step Process

#### **Step 1: User Starts Test**

When user selects a specialization and starts the test:

```python
# In main.py - POST /api/start-test
await generate_test_topics(user_test_id, specialization_id)
```

#### **Step 2: Topic Selection Algorithm**

Located in: `db/utils.py` → `generate_test_topics()`

**Algorithm Flow:**

1. **Fetch all competencies** for the specialization
2. **Sort by importance** (DESC) - CORE competencies with high importance come first
3. **Determine topic distribution** based on number of competencies:

| # of Competencies | Distribution Logic | Example |
|-------------------|-------------------|---------|
| 4 | All get 2 topics each | [2, 2, 2, 2] |
| 5 | Top 3 get 2 topics, rest get 1 | [2, 2, 2, 1, 1] |
| 6 | Top 2 get 2 topics, rest get 1 | [2, 2, 1, 1, 1, 1] |
| Other | Distributed evenly with remainder to top | Calculated |

4. **Randomly select topics** from each competency (using `random.sample`)
5. **Store selected topics** in `user_test_topics` table with fixed order

**Code Example:**
```python
# From db/utils.py:66-89
for idx, (comp_id, comp_data) in enumerate(sorted_competencies):
    num_topics_needed = topics_distribution[idx]
    available_topics = comp_data['topics']

    # Randomly select topics
    chosen_topics = random.sample(available_topics, num_topics_needed)

    # Store with order (1-8)
    for topic in chosen_topics:
        topics_to_insert.append((
            user_test_id,
            topic['id'],
            comp_id,
            topic_order  # Sequential: 1, 2, 3, ..., 8
        ))
        topic_order += 1
```

#### **Step 3: Question Retrieval**

Located in: `main.py` → `GET /api/test/{user_test_id}/questions`

**SQL Query:**
```sql
SELECT
    c.id, c.name,           -- Competency info
    q.id, q.level,          -- Question info
    q.question_text,
    q.var_1, q.var_2, q.var_3, q.var_4,  -- Options
    t.name,                 -- Topic name
    utt.topic_order,        -- Display order (1-8)
    ta.user_answer,         -- User's answer (if answered)
    ta.is_correct           -- Correctness (if answered)
FROM user_test_topics utt
JOIN topics t ON t.id = utt.topic_id
JOIN competencies c ON c.id = utt.competency_id
JOIN questions q ON q.topic_id = t.id
LEFT JOIN test_answers ta ON ta.question_id = q.id AND ta.user_test_id = utt.user_test_id
WHERE utt.user_test_id = %s
ORDER BY utt.topic_order,
         CASE q.level
             WHEN 'Junior' THEN 1
             WHEN 'Middle' THEN 2
             WHEN 'Senior' THEN 3
         END
```

**Ordering Logic:**
1. **Primary Sort:** By `topic_order` (1-8) - ensures topics appear in the assigned order
2. **Secondary Sort:** By `level` (Junior → Middle → Senior) - ensures difficulty progression within each topic

**Result:** 24 questions in total:
- Topic 1: Junior Q, Middle Q, Senior Q
- Topic 2: Junior Q, Middle Q, Senior Q
- ...
- Topic 8: Junior Q, Middle Q, Senior Q

---

## 📝 Question Generation (AI-Powered)

### Overview

Questions are **generated using Claude AI** (Anthropic), not manually written. The system is in: `specializations/generate_from_input.py`

### Generation Process

#### **Step 1: Define Input**

Create `input_prof.json`:
```json
{
  "profile": "IT специалист",
  "specialization": "Java Backend Developer",
  "competencies": [
    "Навыки Java [CORE 90%]",
    "Spring Framework [CORE 85%]",
    "Базы данных [CORE 75%]",
    "REST API проектирование [DAILY 70%]"
  ]
}
```

#### **Step 2: Generate Topics (4 per competency)**

**Prompt to Claude AI:**
```
Ты генеришь темы для тестирования IT-специалистов.

ПРОФЕССИЯ: IT специалист
СПЕЦИАЛИЗАЦИЯ: Java Backend Developer
КОМПЕТЕНЦИЯ: Навыки Java
ТИП: CORE 90%

ЗАДАЧА: Сгенерируй 4 темы для проверки этой компетенции.

ТРЕБОВАНИЯ:
- Темы должны покрывать разные аспекты компетенции
- От базовых до продвинутых аспектов
```

**Claude Output:**
```json
{
  "themes": [
    "Основы синтаксиса и ООП в Java",
    "Коллекции и обработка данных",
    "Многопоточность и конкурентность",
    "Stream API и функциональное программирование"
  ]
}
```

#### **Step 3: Generate Questions (3 per topic)**

**Prompt to Claude AI:**
```
ЗАДАЧА: Сгенерируй 3 вопроса с ПРАВИЛЬНЫМИ ответами.

УРОВНИ:
- JUNIOR (6 мес - 1.5 года): Базовые определения, синтаксис
- MIDDLE (2-3 года): Применение, выбор подхода
- SENIOR (5+ лет): Архитектура, оптимизация, edge cases

ТРЕБОВАНИЯ К ВОПРОСАМ:
- Контекст: банки/телеком в Казахстане
- Четкий и однозначный вопрос

ТРЕБОВАНИЯ К ПРАВИЛЬНЫМ ОТВЕТАМ:
- 5-15 слов
- Технически корректный
```

**Claude Output:**
```json
{
  "questions": [
    {
      "level": "Junior",
      "question": "Что такое ArrayList в Java?",
      "correct_answer": "Динамический массив с изменяемым размером"
    },
    {
      "level": "Middle",
      "question": "В чем разница между ArrayList и LinkedList?",
      "correct_answer": "ArrayList использует массив, LinkedList - двусвязный список"
    },
    {
      "level": "Senior",
      "question": "Как оптимизировать производительность ArrayList при частых вставках?",
      "correct_answer": "Использовать ensureCapacity() или LinkedList для частых вставок"
    }
  ]
}
```

#### **Step 4: Generate Wrong Answers (3 per question)**

**Prompt to Claude AI:**
```
ЗАДАЧА: Сгенерируй 3 НЕПРАВИЛЬНЫХ варианта ответа.

ПРАВИЛЬНЫЙ ОТВЕТ: Динамический массив с изменяемым размером
Длина: 5 слов

ТРЕБОВАНИЯ:
- Похожи на правильный (но НЕ правильные)
- Разная длина (±3 слова от правильного)
- Правдоподобные (не очевидно неправильные)
- Не содержат отрицаний или слов "неправильно"
```

**Claude Output:**
```json
{
  "wrong_answers": [
    "Статический массив фиксированного размера",
    "Список с произвольным доступом к элементам",
    "Коллекция для хранения уникальных значений"
  ]
}
```

#### **Step 5: Shuffle and Store**

```python
# Shuffle all 4 options (1 correct + 3 wrong)
all_answers = [correct_answer] + wrong_answers
random.shuffle(all_answers)

# Find position of correct answer (1-4)
correct_position = all_answers.index(correct_answer) + 1

# Store in database
{
  "question_text": "Что такое ArrayList в Java?",
  "var_1": all_answers[0],
  "var_2": all_answers[1],
  "var_3": all_answers[2],
  "var_4": all_answers[3],
  "correct_answer": correct_position  # 1, 2, 3, or 4
}
```

---

## 🔄 Test Flow

### Complete User Journey

```
1. User selects specialization
   └─> System calls: generate_test_topics()
       └─> Selects 8 random topics based on competency importance
       └─> Stores in: user_test_topics

2. User starts test
   └─> Frontend calls: GET /api/test/{user_test_id}/questions
       └─> System joins: user_test_topics + topics + questions
       └─> Returns: 24 questions (8 topics × 3 levels)
       └─> Ordered by: topic_order, then level (Junior→Middle→Senior)

3. User answers questions
   └─> Frontend calls: POST /api/submit-answer
       └─> System checks: question.correct_answer == user_answer
       └─> Stores in: test_answers
       └─> Updates: current_question_number

4. User completes test
   └─> System calculates: score = COUNT(is_correct = true)
   └─> Stores: completed_at timestamp
   └─> Generates: AI recommendations (Claude API)
```

---

## 📊 Current Question Structure

### Field Breakdown

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | Integer | Primary key | 1234 |
| `topic_id` | Integer | Links to topic | 56 (→ "Многопоточность") |
| `level` | String | Difficulty | "Junior", "Middle", "Senior" |
| `question_text` | Text | The question | "Что такое volatile в Java?" |
| `var_1` | Text | Option 1 | "Ключевое слово для синхронизации" |
| `var_2` | Text | Option 2 | "Модификатор для видимости переменной" |
| `var_3` | Text | Option 3 | "Тип данных для чисел с плавающей точкой" |
| `var_4` | Text | Option 4 | "Аннотация для статических методов" |
| `correct_answer` | Integer | Correct option (1-4) | 2 |

### Characteristics

**Current Structure:**
- ✅ 4 options per question (var_1, var_2, var_3, var_4)
- ✅ Single correct answer (integer 1-4)
- ✅ Fixed columns for options
- ✅ Questions generated by AI (Claude)
- ✅ Wrong answers also generated by AI
- ✅ Shuffled order (correct answer position varies)

---

## 🔍 Key Features

### 1. **Competency-Based Selection**
- Questions grouped by competencies
- Important competencies (CORE 90%) get more topics
- Ensures comprehensive coverage

### 2. **Progressive Difficulty**
- Each topic has Junior → Middle → Senior questions
- Tests knowledge progression
- 8 questions per level (total 24)

### 3. **Randomization**
- Topics selected randomly from each competency
- Different users get different topic combinations
- Answer options shuffled (correct position varies)

### 4. **Fixed Test Structure**
- Once test starts, topics are locked
- User can review/change answers
- Order remains consistent (topic_order)

### 5. **AI-Powered Content**
- Questions generated by Claude AI
- Context-aware (banking/telecom in Kazakhstan)
- Professional quality control

---

## 📈 Statistics

**Typical Specialization:**
- 4-6 competencies
- 4 topics per competency = 16-24 topics total
- 3 questions per topic = 48-72 questions total
- **Test uses:** 8 randomly selected topics = **24 questions**

**Question Breakdown:**
- 8 Junior questions (33%)
- 8 Middle questions (33%)
- 8 Senior questions (33%)

**Scoring:**
- Max score: 24 points
- Each question: 1 point
- Percentage: (score / 24) × 100%

---

## 🎓 Example: Complete Test Structure

**Specialization:** Java Backend Developer
**Test ID:** 789
**User:** Иван Тестовый

### Selected Topics (8):

| Order | Competency | Topic |
|-------|-----------|-------|
| 1 | Навыки Java (CORE 90%) | Основы ООП |
| 2 | Навыки Java (CORE 90%) | Многопоточность |
| 3 | Spring Framework (CORE 85%) | Dependency Injection |
| 4 | Spring Framework (CORE 85%) | Spring Boot |
| 5 | Базы данных (CORE 75%) | SQL запросы |
| 6 | Базы данных (CORE 75%) | Индексы и оптимизация |
| 7 | REST API (DAILY 70%) | HTTP методы |
| 8 | REST API (DAILY 70%) | Безопасность API |

### Questions (24 total):

**Topic 1 - Основы ООП:**
- Q1 (Junior): Что такое инкапсуляция?
- Q2 (Middle): В чем разница между абстрактным классом и интерфейсом?
- Q3 (Senior): Как реализовать паттерн Strategy в Java?

**Topic 2 - Многопоточность:**
- Q4 (Junior): Что такое поток (Thread)?
- Q5 (Middle): В чем разница между synchronized и volatile?
- Q6 (Senior): Как избежать deadlock?

...and so on for all 8 topics.

---

## 🛠️ Files Reference

**Database Schema:**
- `/home/user/hr_testing/db/init_db.sql` - Complete schema definition

**Topic Selection Logic:**
- `/home/user/hr_testing/db/utils.py` - `generate_test_topics()` function

**Question Retrieval:**
- `/home/user/hr_testing/main.py:735` - `GET /api/test/{user_test_id}/questions`

**Question Generation (AI):**
- `/home/user/hr_testing/specializations/generate_from_input.py` - Claude AI integration

**Question Storage:**
- Table: `questions` (lines 78-89 in init_db.sql)

---

## 💡 Summary

**How Questions Are Stored:**
- Hierarchical: Profile → Specialization → Competency → Topic → Question
- Each question has: text, 4 options, correct_answer (1-4), level (Junior/Middle/Senior)
- Stored in PostgreSQL `questions` table

**How Questions Are Selected:**
1. System selects 8 topics based on competency importance + randomization
2. For each topic, retrieves all 3 questions (Junior, Middle, Senior)
3. Orders by topic_order, then by level
4. Total: 24 questions per test
5. Topics locked once test starts (stored in `user_test_topics`)

**Key Algorithm:**
- Important competencies (CORE, high %) get more topics
- Random selection within each competency
- Fixed structure ensures consistency
- Progressive difficulty (Junior → Middle → Senior)

---

**Generated:** 2025-11-07
**Current Structure:** 4 options per question (var_1, var_2, var_3, var_4)
**Selection Algorithm:** Competency-importance-based with randomization
