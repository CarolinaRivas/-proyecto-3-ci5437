import json, datetime
import saveload

# Global variables to store all values for later retrieval during decoding
value_dict = {}
last_value = 1

def var(d, h, i, j):
    assert(0<= i and i <= N and 0<= j and j <=N)
    #value = f"{d}00{h}00{i}00{j}"
    #return value
    global last_value
    k = f"{d} {h} {i} {j}"

    if k not in value_dict:
        value_dict[k] = last_value
        last_value += 1
        return last_value - 1

    return value_dict[k]

def convert(filename):
    global N

    file_name = filename

    with open(file_name, 'r') as f:
        data = json.loads(f.read())

    N = len(data["participants"])

    clauses = []
    
    
    init_date = datetime.date.fromisoformat(data["start_date"])
    end_date = datetime.date.fromisoformat(data["end_date"])
    dur_date = (end_date - init_date).days + 1

    init_hour = datetime.time.fromisoformat(data["start_time"])
    end_hour = datetime.time.fromisoformat(data["end_time"])
    dur_hour = abs(end_hour.hour - init_hour.hour)

    temp = []
    count = 0
    clauses_sum = 0

    print("Calculating clauses...")

    # Número total de variables
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            if i != j:
                for d in range(1, dur_date + 1):
                    for h in range(1, (dur_hour // 2) + 1):
                        count += 1
    
    # Los participantes deben jugar al menos una vez con cada uno de los otros participantes
    for i in range(1, N + 1): #Participante que juega como local
        for j in range(1, N + 1): #Participante que juega como visitante
            if i != j:
                for d in range(1, dur_date + 1):
                    temp += [f"{var(d,h,i,j)}" for h in range(1, (dur_hour // 2) + 1)]

                clauses.append(temp)
                temp = []

    with open("cnf.txt", "w") as cnf:
        separator = " "

        for cls in clauses:
            cls.append("0")
            cnf.write(separator.join(cls) + "\n")

    clauses_sum += len(clauses)
    clauses = []
    
    # Los participantes máximo deben jugar una vez como local y una como visitante con otro participante
    for d in range(1, dur_date + 1):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if i != j:
                    for h in range(1, (dur_hour // 2) + 1):
                        for w in range(1, dur_date + 1):
                            for k in range(1, (dur_hour // 2) + 1):
                                if w != d or k != h:
                                    clauses.append([f"-{var(d,h,i,j)}", f"-{var(w,k,i,j)}"])

    with open("cnf.txt", "a") as cnf:
        separator = " "

        for cls in clauses:
            cls.append("0")
            cnf.write(separator.join(cls) + "\n")

    clauses_sum += len(clauses)
    clauses = []

    # Un participante puede jugar a lo sumo una vez por dia
    for d in range(1, dur_date + 1):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if i != j:
                    for h in range(1, (dur_hour // 2) + 1):
                        for w in range(1, N + 1):
                            if w != i:
                                for k in range(1, (dur_hour // 2) + 1):
                                    if w != j:
                                        clauses.append([f"{-var(d,h,i,j)}", f"{-var(d,k,i,w)}"])
                                        clauses.append([f"{-var(d,h,i,j)}", f"{-var(d,k,w,j)}"])
                                    
                                    clauses.append([f"{-var(d,h,i,j)}", f"{-var(d,k,w,i)}"])

    with open("cnf.txt", "a") as cnf:
        separator = " "

        for cls in clauses:
            cls.append("0")
            cnf.write(separator.join(cls) + "\n")

    clauses_sum += len(clauses)
    clauses = []

    # Dos juegos no pueden ocurrir al mismo tiempo
    for d in range(1, dur_date + 1):
        for h in range(1, (dur_hour // 2) + 1):
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    if i != j:
                        for w in range(1, N + 1):
                            for k in range(1, N + 1):
                                if (w != i or k != j) and w != k:
                                    clauses.append([f"{-var(d,h,i,j)}", f"{-var(d,h,w,k)}"])

    with open("cnf.txt", "a") as cnf:
        separator = " "

        for cls in clauses:
            cls.append("0")
            cnf.write(separator.join(cls) + "\n")

    clauses_sum += len(clauses)
    clauses = []

    # Un jugador no puede jugar ni de local ni de visitante dos dias consecutivos
    for d in range(1, dur_date):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if i != j:
                    for h in range(1, (dur_hour // 2) + 1):
                        for w in range(1, N + 1):
                            if w != i and w != j:
                                for k in range(1, (dur_hour // 2) + 1):
                                    clauses.append([f"{-var(d,h,i,j)}", f"{-var(d+1,k,i,w)}"])
                                    clauses.append([f"{-var(d,h,i,j)}", f"{-var(d+1,k,w,j)}"])

    with open("cnf.txt", "a") as cnf:
        separator = " "

        for cls in clauses:
            cls.append("0")
            cnf.write(separator.join(cls) + "\n")

    clauses_sum += len(clauses)
    clauses = []

    with open("cnf.txt", 'r+') as cnf:
        readcont = cnf.read()
        cnf.seek(0,0)

        cnf.write(f"p cnf {count} {clauses_sum} \n")

        cnf.write(readcont)

    print("Saving value dictionary in keys.pkl")
    saveload.save_obj(value_dict, "keys")


    print("Done")



