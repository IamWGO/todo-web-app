import json
import config

# --------DB-----------
filename = "task.json"
task_items = []

def load_db():
    json_dict = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
                try:
                    json_dict = json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Wrong JSON format: {e}")
                except ValueError:
                    print("File is not json format")
    except FileNotFoundError:
        f = open(filename, "w", encoding="utf-8")
        f.writelines("[]")  

    return json_dict

task_items = load_db()

# --------Functions----------- 
def save_db():
    with open(filename, 'w') as f:
        return json.dump(task_items, f, indent=4)


def get_max_id():
    task_items = load_db()
    if not task_items: 
        return 1
    else: 
        # Find the maximum ID in the list
        max_id = max(task["id"] for task in task_items)
        # Calculate the next ID
        return max_id + 1
    

def add_new_task(new_task): 
    task_items.append(new_task)
    save_db()
    

def get_task_info(task_id):
    for task in task_items:
        if task["id"] == task_id:
            return task  # Return the task if the ID matches
    
    return None  

def delete_task(task_id):
    for index, task in enumerate(task_items):
        if task["id"] == task_id:
            del task_items[index]
            save_db()
            break
    
def update_task(task_id, update_task):
    for index, task in enumerate(task_items):
        if task["id"] == task_id:
            task_items[index] = update_task
            save_db()
            break

def get_categories():
    return config.categories

def get_category_name_by_id(category_id):
    # Iterate through the list of tuples
    for item in config.categories:
        if item[0] == category_id:
            return item[1]
    return None
 

def get_category_id_by_name(category_name): 
    # Iterate through the list of tuples
    for item in config.categories:
        if item[1] == category_name:
            return item[0]
    return None
            

def get_all_tasks():
    return task_items

def get_tasks_by_category():
    tasks_by_category = {}

    # Group tasks by category
    for task in task_items:
        category = task["category"]
        if category not in tasks_by_category:
            tasks_by_category[category] = []
        
        item = f"{task["description"]} - {task["status"]}"
        tasks_by_category[category].append(item)
 
    return tasks_by_category

def search_by_title_and_category_name(search_text, category_id):
    category_name = get_category_name_by_id(category_id)
    matching_tasks = []
    for task in task_items:
        if (search_text.lower() in task["description"].lower() 
            and category_name.lower() in task["category"].lower()):
            matching_tasks.append(task)
    return matching_tasks

def search_tasks_by_category_name(category_id):
    category_name = get_category_name_by_id(category_id)
    matching_tasks = []
    for task in task_items:
        if category_name.lower() in task["category"].lower():
            matching_tasks.append(task)
    return matching_tasks

def search_task_by_title(search_text):
    # Create a list to store matching items
    matching_tasks = []
    for task in task_items:
        if search_text in task["description"]:
            matching_tasks.append(task)
    return matching_tasks

# Helper methods
def is_number(task_id):
    try: 
        int(task_id)
        return True
    except ValueError:
        return False