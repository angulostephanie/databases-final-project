from . import constants
from .charts import PieChart
from .charts import HorizontalBarGraph
from pygal.style import DarkStyle

TITLE = "Patients' "
def createGraphic(data, key, pie=True):
    print("hello")
    chart = None
    if pie:
        chart = PieChart(
                TITLE + key + "s",
                height=450,
                width=550,
                explicit_size=True
            )
    else:
        chart = HorizontalBarGraph(
                TITLE + key + "s",
                height=450,
                width=550,
                explicit_size=True
            )
    return chart.generate(data, key)


def createPreparedStatementForSpecificPatient(cursor, patient_id):
    field_list = ['Patient Id', 'Race', 'Gender']
    values = []
    select_ps = "SELECT Patient.patient_id, Patient.race, Patient.gender"
    from_ps = "FROM Patient"
    where_ps = "WHERE Patient.patient_id = '" + patient_id + "'"
    ps = select_ps + " " + from_ps + " " + where_ps + ";"
    print(ps)
    cursor.execute(ps)
    return cursor.fetchall(), field_list, values


def insertNewPatient(cursor, data):
    insert_ps = "INSERT INTO Patient" + " (patient_id, race, gender, payer_code) "
    print(data)
    print(data['Race'])
    new_patient_data = data['patientID'] + ", '" + data['Race'] + "', '" + data['Gender'] + "', '" + data['PayerCode'] +"'"

    values = "VALUES( " + new_patient_data + " );"

    ps = insert_ps + values
    print(ps)
    cursor.execute(ps)

    return True

def createPreparedStatement(cursor, request_data):
    field_list = ['Patient Id', 'Race', 'Gender', 'Age']
    keys = request_data.keys()
    values = []
    select_ps = "SELECT Patient.patient_id, Patient.race, Patient.gender, Encounter.age"
    from_ps = "FROM Patient"
    where_ps = "WHERE "
    joins = {"Encounter": True,
             "Medication": False,
             "Vitals": False,
             "Source": False,
             "Discharge": False}
    for key in keys:
        value = request_data.get(key)
        if key != "csrfmiddlewaretoken":
            values.append(value)

        if key == "Gender":
            where_ps += "Patient.gender = '" + value + "'"
        elif key == "Race":
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Patient.race = '" + value + "'"
        elif key == "Age":
            # add to where statement
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Encounter.age = '" + value + "'"
        elif key == "Medication":
            field_list.append('Medication')
            joins["Medication"] = True
            # add to select statement
            select_ps += ", Medication.med_name"
            # add to from statement
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Medication.med_name = '" + value + "'"
        elif key == "a1c_result":
            field_list.append("A1c Result")
            joins["Vitals"] = True
            # add to select statement
            select_ps += ", Vitals.a1c_result"
            # add to from statement
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Vitals.a1c_result = '" + value + "'"
        elif key == "glucose_result":
            field_list.append("Glucose Result")
            joins["Vitals"] = True
            # add to select statement
            select_ps += ", Vitals.glucose_result"
            # add to from statement
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Vitals.glucose_result = '" + value + "'"
        elif key == "source_id":
            field_list.append("Admission Source")
            joins["Source"] = True
            # add to select statement
            select_ps += ", Source.source_name"
            # add to from statement
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Source.source_id = '" + value + "'"
        elif key == "discharge_id":
            field_list.append("Discharge Destination")
            joins["Discharge"] = True
            # add to select statement
            select_ps += ", Discharge.discharge_name"
            # add to from statement
            if where_ps != "WHERE ":
                where_ps += " AND "
            where_ps += "Discharge.discharge_id = '" + value + "'"

    if joins["Encounter"]:
        from_ps += " natural join Has natural join Encounter"
    if joins["Medication"]:
        from_ps += " natural join Prescribes natural join Medication"
    if joins["Vitals"]:
        from_ps += " natural join Vitals"
    if joins["Source"]:
        from_ps += " natural join GetsPatientFrom natural join Source "
    if joins["Discharge"]:
        from_ps += " natural join SendsPatientTo natural join Discharge "

    ps = select_ps + " " + from_ps + " " + where_ps + ";"
    print(ps)
    cursor.execute(ps)
    return cursor.fetchall(), field_list, values
