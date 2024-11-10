from ravendb import DocumentStore

db = DocumentStore(
    urls=["http://localhost:8080/"],
    database="ProjectSeminar"
)

db.initialize()

print(db._initialized)
