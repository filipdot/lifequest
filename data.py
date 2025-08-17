CURRENT_QUESTION_VERSION = "1.3"
CURRENT_APP_VERSION = "1.3"

# Ścieżki rozwoju z wersjonowaniem pytań
PATHS = {
    "question_version": CURRENT_QUESTION_VERSION,
    "Fizyczna": {
        "questions": [  
            ("Ile razy w tygodniu ćwiczysz (siłownia, bieganie, basen itp.)? (0-7)", 0, 7),
            ("Jaki jest Twój przybliżony czas na 5 km biegu (w minutach)? (Wpisz 0 jeśli nie wiesz lub nie biegasz)", 0, 60),
            ("Ile pompek jesteś w stanie zrobić na raz? (0 jeśli nie wiesz)", 0, 100),
        ],
        "levels": {1: 0, 2: 10, 3: 30, 4: 60, 5: 100, 6: 150, 7: 210, 8: 280, 9: 360, 10: 450},
        "guides": {
            1: "Zrób 3 spacery tygodniowo po 30 min.",
            2: "Dodaj siłownię 2x/tydz. po 45 min.",
            3: "Biegaj 3x/tydz. po 5km w <30 min.",
            4: "Trening siłowy 4x/tydz. z ciężarami.",
            5: "Dodaj basen 2x/tydz. po 1h.",
            6: "Przygotuj się do półmaratonu.",
            7: "Zaawansowane HIIT 5x/tydz.",
            8: "Trenuj z trenerem personalnym.",
            9: "Weź udział w zawodach sportowych.",
            10: "Osiągnij poziom profesjonalnego atlety."
        }
    },
    "Społeczna": {
        "questions": [  
            ("Ile interakcji społecznych (>5 min rozmowy) masz tygodniowo? (0-20, wpisz 0 jeśli nie wiesz)", 0, 20),
            ("Ile masz bliskich przyjaciół (osób, z którymi dzielisz się osobistymi sprawami)? (0-10)", 0, 10),
            ("Jak oceniasz swoją umiejętność prowadzenia rozmowy (1-5, gdzie 1=trudno mi zacząć, 5=łatwo buduję relacje)?", 1, 5),
        ],
        "levels": {1: 0, 2: 10, 3: 30, 4: 60, 5: 100, 6: 150, 7: 210, 8: 280, 9: 360, 10: 450},
        "guides": {
            1: "Uśmiechnij się i przywitaj 3 osoby dziennie.",
            2: "Zagadaj do kogoś w sklepie lub na siłowni (>5 min).",
            3: "Idź na meetup tematyczny raz w tygodniu.",
            4: "Zbuduj 1 nową relację (wymiana numerów).",
            5: "Dołącz do grupy hobby i bądź aktywny.",
            6: "Weź udział w evencie networkingowym.",
            7: "Prowadź głębokie rozmowy z przyjaciółmi.",
            8: "Zbuduj krąg 5+ przyjaciół.",
            9: "Zostań liderem w społeczności.",
            10: "Mistrz empatii i relacji."
        }
    },
    "Zawodowa": {
        "questions": [  
            ("Czy prowadzisz backlog zadań? (1=tak, 0=nie)", 0, 1),
            ("Jak radzisz sobie z zmianami w pracy (1-5, 1=trudno adaptuję, 5=łatwo)?", 1, 5),
        ],
        "levels": {1: 0, 2: 10, 3: 30, 4: 60, 5: 100, 6: 150, 7: 210, 8: 280, 9: 360, 10: 450},
        "guides": {
            1: "Zrób 1 zadanie z backlogu dziennie.",
            2: "Planuj tydzień pracy z priorytetami.",
            3: "Adaptuj do zmian rynkowych (ucz się nowej umiejętności).",
            4: "Stwórz budżet miesięczny i śledź wydatki.",
            5: "Rozpocznij side project zarobkowy.",
            6: "Celuj w awans lub podwyżkę poprzez wyniki.",
            7: "Lideruj zespołem zadań w pracy.",
            8: "Wprowadzaj innowacje i optymalizuj procesy.",
            9: "Rozwijaj przedsiębiorczość (własny biznes).",
            10: "Osiągnij poziom eksperta/CEO."
        }
    }
}

DATA_FILE = "lifequest_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    # Migrate i defaults dla kompatybilności
    if "app_version" not in data or data["app_version"] != CURRENT_APP_VERSION:
        data["app_version"] = CURRENT_APP_VERSION
        data["question_version"] = PATHS["question_version"]
        data["levels"] = data.get("levels", {})
        data["exp"] = data.get("exp", {})
        data["achievements"] = data.get("achievements", [])
        # Migrate tasks
        tasks = data.get("tasks", [])
        migrated_tasks = []
        for task in tasks:
            if isinstance(task, str):
                migrated_tasks.append({"text": task, "path": "Fizyczna", "exp": 5, "condition": "N/A", "completed": False})
            else:
                migrated_tasks.append(task)
        data["tasks"] = migrated_tasks
        data["responses"] = data.get("responses", {})
        data["dashboard_config"] = data.get("dashboard_config", {"show_levels": True, "show_ach": True, "show_tasks": True})
    return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
