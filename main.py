import sys
import json
import datetime
import subprocess
import threading
import time
from ics import Calendar, Event
import cnf
import saveload


def get_var(keys_dict, value):
    """
    Obtiene los valores enteros a partir de una cadena dividida en una lista.
    :param keys_dict: Diccionario que contiene los valores.
    :param value: Valor a procesar.
    :return: Tupla con los valores enteros obtenidos.
    """
    values = keys_dict[value].split()
    return tuple(map(int, values))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Missing Argument")
        sys.exit(1)

    start_t = time.perf_counter()

    # Creación de un hilo para ejecutar la función cnf.convert
    threading.Thread(target=cnf.convert, args=(sys.argv[1],)).start()

    cnf_t = time.perf_counter()
    print(f"JSON to CNF Time: {cnf_t - start_t}")

    # Ejecución del programa Glucose
    subprocess.run(["./glucose/simp/glucose_static", "cnf.txt", "r.txt"])

    glucose_t = time.perf_counter()
    print(f"Glucose Time: {glucose_t - cnf_t}")

    # Carga del diccionario de claves
    value_dict = saveload.load_obj('keys')
    keys_dict = {v: k for k, v in value_dict.items()}

    with open('r.txt', 'r') as result:
        read_data = result.read()

    if read_data.startswith("UNSAT"):
        print("Unsatisfiable")
        sys.exit(2)

    # Extracción de los ID de los matches
    match_ids = [int(i) for i in read_data.split() if int(i) > 0]
    matches = [get_var(keys_dict, k) for k in match_ids]

    with open(sys.argv[1], 'r') as file:
        t_json = json.load(file)

    # Obtención de datos del torneo
    tournament_name = t_json["tournament_name"]
    start_date = datetime.date.fromisoformat(t_json["start_date"])
    end_date = datetime.date.fromisoformat(t_json["end_date"])
    start_time = datetime.time.fromisoformat(t_json["start_time"])
    end_time = datetime.time.fromisoformat(t_json["end_time"])
    participants = t_json["participants"]

    cal = Calendar()
    for d, h, i, j in matches:
        begin = datetime.datetime.combine(start_date + datetime.timedelta(days=d - 1), start_time)
        begin += datetime.timedelta(hours=2 * (h - 1))
        end = begin + datetime.timedelta(hours=2)

        e = Event()
        e.name = f"{participants[i - 1]} vs. {participants[j - 1]}"
        e.begin = begin.isoformat()
        e.end = end.isoformat()

        cal.events.add(e)

    print("Writing calendar file...")
    with open(f"{tournament_name}.ics", 'w') as ic:
        ic.write(str(cal))
    print("Done")

    end_t = time.perf_counter()
    print(f"Creating Calendar Time: {end_t - glucose_t}")
    print(f"Execution time: {end_t - start_t}")
