from deta import Deta

deta = Deta("a0558p23_1qnSrugdeUhAokVe8AvE5w9HyNSnt6yx")

db = deta.Base("Prosjekter")

def insert_data(projectname, id, project_type, project_status, lat, long, name, date):
    return db.put({
        "key" : projectname,
        "Oppdragsnummer" : id, 
        "Type" : project_type,
        "Status" : project_status,
        "Latitude" : lat,
        "Longitude" : long, 
        "Innsender" : name,
        "Dato" : date})

def fetch_all_data():
    res = db.fetch()
    return res.items

def get_data(projectname):
    return db.get(projectname)

def remove_data(projectname):
    return db.delete(projectname)

