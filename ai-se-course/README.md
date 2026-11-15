# קורס מעשי: AI Solutions Engineer

לכל נושא יש כאן שיעור מעמיק, תרגילי קוד עם בדיקות אוטומטיות, שאלות תרחיש, וביקורת קוד בתוך ה-IDE.
קובץ הסקירה הכללית (מפה, כרטיסיות, מבחנים, סימולציית ראיון): [`../ai-solutions-engineer-prep.html`](../ai-solutions-engineer-prep.html).

## התקנה (פעם אחת)

```bash
cd ai-se-course
```

```bash
python -m venv .venv && source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

הרצת כל הבדיקות (בהתחלה כולן נכשלות — זה מצופה, עוד לא כתבתם קוד):

```bash
python -m pytest
```

מפתח API נדרש רק לסקריפטים `run_live.py`. שמים אותו במשתנה סביבה `ANTHROPIC_API_KEY` או בקובץ `.env` בתיקייה הזו (הוא ב-`.gitignore`, לעולם לא עושים לו commit).

## איך עובדים עם כל נושא

```
1. LESSON.md      קוראים פרק אחד
2. EXERCISES.md   מבינים את המשימה
3. exN_*.py       כותבים קוד (במקום ה-TODO)
4. pytest          מריצים את הבדיקות של התרגיל
5. /review X.Y    ביקורת ב-Claude Code → נשמרת ב-reviews/X.Y.md
6. מתקנים, ו-/review שוב (הביקורת משווה לסבב הקודם)
7. QUESTIONS.md   בסוף הנושא: שאלות תרחיש, עונים בכתב ב-reviews/, ואז /review X-questions
```

**ביקורת:** ב-Claude Code (טרמינל, VS Code או JetBrains), כשהריפו פתוח, כותבים `/review 1.2`. Claude מריץ את הבדיקות, קורא את הקוד מול קריטריוני `RUBRIC.md`, ומחזיר ציון, נקודות טובות, בעיות לפי חומרה עם מספר שורה, ושאלות להבנה. הוא **לא** כותב את הפתרון במקומכם. אם תקועים — שאלו אותו ישירות ("אני תקוע ב-2.1, החפיפה שוברת לי את האורך"), והוא ייתן רמז.

## תוכן

| # | נושא | שיעור | תרגילים | סטטוס |
|---|---|---|---|---|
| 1 | [LLMs והנדסת הנחיות](01-llm-basics/LESSON.md) | 11 פרקים | עלות, סיווג עם Structured Outputs, retry, ניהול היסטוריה | ✅ מוכן |
| 2 | [RAG](02-rag/LESSON.md) | 14 פרקים | chunking, חיפוש וקטורי, BM25, היברידי+RRF, מדידה, Mini RAG מלא | ✅ מוכן |
| 3 | סוכנים ו-MCP | | לולאת סוכן ידנית, כלים, אישור אנושי, שרת MCP, workflow מול סוכן | ⏳ מתווסף כשתגיעו |
| 4 | הערכה, אבטחה ותצפיתיות | | golden set + LLM-as-judge, CI, PII, התקפת prompt injection | ⏳ |
| 5 | ענן ופריסה | | FastAPI+SSE, Docker, Bedrock, CI/CD | ⏳ |
| 6 | ארכיטקטורה ועבודה מול לקוח | | אפיון, HLD, POC, ROI (משימות כתיבה עם ביקורת) | ⏳ |
| 7 | אוטומציה | | n8n מול קוד | ⏳ |

שלבים 3–7 ייבנו באותו פורמט. כשמסיימים שלב, בקשו: "תכין את שלב 3".

## מבנה

```
ai-se-course/
├── common/            FakeClient (API מזויף לבדיקות) + HashingEmbedder
├── 01-llm-basics/     LESSON · EXERCISES · QUESTIONS · RUBRIC · ex*.py · tests/ · run_live.py
├── 02-rag/            ... + data/ (מסמכים לדוגמה בעברית)
└── reviews/           כאן נשמרות הביקורות והתשובות שלכם
```

## הקשר לפרויקט הראשי

התרגילים הם אבני הבניין. אחרי כל שלב, לוקחים את מה שבניתם ומכניסים לפרויקט (`service-assistant`) כשכבה: סיווג מ-1.2 + עלות מ-1.1 = שכבה 1; Mini RAG מ-2.6 עם embedder אמיתי ו-pgvector = שכבה 2.
