import yaml, os.path

Books = yaml.safe_load(
    open(os.path.join(
        os.path.dirname(__file__),
        "static/data.yml")))

i = 0
for book in Books:
    book[id] = i
    i += 1

def get_books():
    return Books
