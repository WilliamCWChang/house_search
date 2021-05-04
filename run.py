import csv
import requests
from bs4 import BeautifulSoup
import toml
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()


def get_headers(user_data):

    client = requests.session()
    LOGIN_URL = "https://www.591.com.tw/user-login.html?"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    }
    data = {
        "user.username": user_data["user"]["username"],
        "user.pwd": user_data["user"]["password"],
        "user.verifyCode": "",
        "cookie": "on",
        "login_sub": "",
        "module": " user",
        "user.bindCode": "",
        "action": " login",
        "redirect": "",
        "isShowCode": "",
    }
    response = client.get(LOGIN_URL)
    response = client.post(LOGIN_URL, data=data, headers=headers, verify=False,)
    assert response.status_code == 200
    headers["cookie"] = "; ".join([x.name + "=" + x.value for x in response.cookies])

    response = client.get(
        "https://www.591.com.tw/index.php?module=userCenter&action=newGuest",
        params={"module": "userCenter", "action": "newGuest"},
        headers=headers,
        verify=False,
    )
    assert response.status_code == 200
    headers["cookie"] = "; ".join([x.name + "=" + x.value for x in response.cookies])

    urls = [
        "https://rent.591.com.tw/home/rent/localStorage",
        "https://sale.591.com.tw/home/sale/localStorage",
        "https://business.591.com.tw/home/business/localStorage",
    ]
    for url in urls:
        response = client.get(url, headers=headers, verify=False)
        assert response.status_code == 200
        headers["cookie"] = "; ".join(
            [x.name + "=" + x.value for x in response.cookies]
        )

    response = requests.get("https://sale.591.com.tw/", headers=headers)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text)
    headers["X-CSRF-TOKEN"] = soup.find("meta", {"name": "csrf-token"})["content"]
    return headers


def get_json(headers, payload):
    TARGET_URL = "https://sale.591.com.tw/home/search/list"
    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
    response = requests.get(TARGET_URL, headers=headers, params=payload_str)
    assert response.status_code == 200
    return response.json()["data"]["house_list"]


def save_to_csv_file(csv_filename, dict_data):
    csv_columns = [
        "filename",
        "type",
        "houseid",
        "kind",
        "kind_name",
        "shape_name",
        "region_name",
        "section_name",
        "title",
        "has_carport",
        "room",
        "floor",
        "photoNum",
        "mainarea",
        "carttype",
        "cartmodel",
        "is_video",
        "is_full",
        "photo_url",
        "refreshtime",
        "nick_name",
        "housetype",
        "isnew",
        "posttime",
        "area",
        "houseage",
        "showhouseage",
        "address",
        "browsenum",
        "unit_price",
        "unitprice",
        "price",
        "showprice",
        "is_oversea",
        "is_carport",
        "original_price",
        "is_down_price",
        "down_price_percent",
        "is_combine",
        "isvip",
        "is_hurry_price",
        "community_link",
        "community_name",
        "tag",
        "saletype",
        "delivery",
        "fci_pai",
        "pc_good_house",
        "good_house",
        "mvip",
        "m_recom",
        "user_id",
    ]
    with open(csv_filename, "w", newline="", encoding="UTF-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


def get_total_house(user_data, headers):
    payload = {
        "type": user_data["house"]["type"],
        "shType": user_data["house"]["shType"],
        "regionid": user_data["house"]["regionid"],
        "section": user_data["house"]["section"],
        "area": user_data["house"]["area"],
        "price": user_data["house"]["price"],
        "houseage": user_data["house"]["houseage"],
    }

    dict_data = []
    number = 1
    index = 0
    while number:
        payload["firstRow"] = str(index * 30)
        r = get_json(headers, payload)
        number = len(r)
        index += 1
        dict_data.extend(r)
        print(f"index = {index}, number = {number}")
    print(len(dict_data))
    return dict_data


user_data = toml.load("user.toml")
house_data = get_total_house(user_data, get_headers(user_data))
save_to_csv_file("new.csv", house_data)