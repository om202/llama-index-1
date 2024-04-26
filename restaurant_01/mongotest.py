import pymongo

db_name = 'test'
test_client = pymongo.MongoClient('mongodb://localhost:27017/')
test_db = test_client[db_name]

col_name = 'col'
test_col = test_db[col_name]
test_dict = { "surname": "Omprakash", "address": "Meliq Adamyan 1",
             "city": "Yerevan" }
pl = test_col.insert_one(test_dict)

print(pl)

# Check if inserted or not

all_data = test_col.find({})

for doc in all_data:
    print(doc)