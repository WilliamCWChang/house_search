import requests
import csv

TOTAL = 0
SPECIAL = []


def get_info(num):
    global TOTAL
    print(f"num = {num}, TOTAL = {TOTAL}", end="")
    headers = {
        "Content-Type": "application/json"
    }
    payload = {"Method": "CaseDetail", "Data": {"IDX": int(num)}}
    r = requests.post(
        "https://m.ycut.com.tw/ashx/CaseDetail.ashx", headers=headers, json=payload)
    data = r.json()["Data"]
    if(len(data) > 1):
        TOTAL += 1
        SPECIAL.append(num)
        print()
    elif(len(data) == 0):
        TOTAL += 1
        print()
    else:
        TOTAL = 0
        data = data[0]
        print(f'   title =  {data["AddrSimp"]} || {data["CaseName"]}')

        # if "三峽" in data["AddrSimp"] or "樹林" in data["AddrSimp"]:
        return {
            "IDX": data["IDX"],
            "SellRent": data["SellRent"],
            "HeadCode": data["HeadCode"],
            "CaseName": data["CaseName"],
            "MStaff": data["MStaff"],
            "BuildingName": data["BuildingName"],
            "ParkingPrice": data["ParkingPrice"],
            "Price": data["Price"],
            "AvePrice": data["AvePrice"],
            "PubRate": data["PubRate"],
            "Rm": data["Rm"],
            "LivingRm": data["LivingRm"],
            "BathRm": data["BathRm"],
            "AddrSimp": data["AddrSimp"],
            "LandShPin": data["LandShPin"],
            "BuiTotPin": data["BuiTotPin"],
            "BuiMPin": data["BuiMPin"],
            "BasementPin": data["BasementPin"],
            "BuiAuxPin": data["BuiAuxPin"],
            "BuiPubPin": data["BuiPubPin"],
            "UseCode": data["UseCode"],
            "TypeCode": data["TypeCode"],
            "PositionName": data["PositionName"],
            "ParkingSpace": data["ParkingSpace"],
            "MgCode": data["MgCode"],
            "MgExpense": data["MgExpense"],
            "ParkingExpense": data["ParkingExpense"],
            "PriSchoolName": data["PriSchoolName"],
            "JunSchoolName": data["JunSchoolName"],
            "BuiYear": data["BuiYear"],
            "FloorSt": data["FloorSt"],
            "FloorEn": data["FloorEn"],
            "UpFloor": data["UpFloor"],
            "IncludeParking": data["IncludeParking"],
            "ModDate": data["ModDate"],
            "SharedUrl": data["SharedUrl"],
            "TwDate": data["TwDate"]}


def save_to_csv_file(csv_filename, dict_data):
    csv_columns = [
        "IDX",
        "SellRent",
        "HeadCode",
        "CaseName",
        "MStaff",
        "BuildingName",
        "ParkingPrice",
        "Price",
        "AvePrice",
        "PubRate",
        "Rm",
        "LivingRm",
        "BathRm",
        "AddrSimp",
        "LandShPin",
        "BuiTotPin",
        "BuiMPin",
        "BasementPin",
        "BuiAuxPin",
        "BuiPubPin",
        "UseCode",
        "TypeCode",
        "PositionName",
        "ParkingSpace",
        "MgCode",
        "MgExpense",
        "ParkingExpense",
        "PriSchoolName",
        "JunSchoolName",
        "BuiYear",
        "FloorSt",
        "FloorEn",
        "UpFloor",
        "IncludeParking",
        "ModDate",
        "SharedUrl",
        "TwDate",
    ]

    with open(csv_filename, "a", newline="", encoding="UTF-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        # writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


def get_max_min(csv_filename):
    data = []

    with open(csv_filename, "r", newline="", encoding="UTF-8") as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            num = row[0]
            if str.isdigit(num):
                data.append(int(num))
    # print(data)

    return max(data), min(data)


for i in range(1):
    csv_filename = "ycut.csv"
    dict_data = []

    MAX_TOTAL = 10
    mx, mi = get_max_min(csv_filename)
    print(mx, mi)

    number = mx + 1
    while TOTAL < MAX_TOTAL:
        info = get_info(number)
        if info:
            print(info)
            dict_data.append(info)
        number = number + 1
    dict_data.append({"IDX": number - 1})

    TOTAL = 0
    number = mi - 1
    while TOTAL < MAX_TOTAL:
        info = get_info(number)
        if info:
            # print(info)
            dict_data.append(info)
        number = number - 1
    dict_data.append({"IDX": number + 1})

    save_to_csv_file(csv_filename, dict_data)
    print(f"SPECIAL = {SPECIAL}")
