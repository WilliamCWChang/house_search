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
        "user.username": user_data["username"],
        "user.pwd": user_data["password"],
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
        "https://rent.591.com.tw/",
        "https://rent.591.com.tw/home/rent/localStorage",
        "https://sale.591.com.tw/home/sale/localStorage",
        "https://business.591.com.tw/home/business/localStorage",
        "https://market.591.com.tw/home/market/localStorage",
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

    # CHANGE TO NEW TAIPEI CITY!!
    URL = "https://rent.591.com.tw/home/index/recomNews?role=0&device=4&channel=rent&position=list-news&regionid=3"
    response = requests.get(URL, headers=headers)
    headers["cookie"] = "; ".join([x.name + "=" + x.value for x in response.cookies])

    return headers


def get_json(headers, payload):
    TARGET_URL = "https://rent.591.com.tw/home/search/rsList"
    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
    response = requests.get(TARGET_URL, headers=headers, params=payload_str,)
    assert response.status_code == 200
    return response.json()["data"]["data"]


def save_to_csv_file(csv_filename, dict_data):
    csv_columns = [
        "posttime",
        "street_name",
        "price",
        "fulladdress",
        "floorInfo",
        "area",
        "cases_name",
        "layout",
        "id",
        "room",
        "social_house",
        #
        "addr_number_name",
        "address_img",
        "address_img_title",
        "alley_name",
        "allfloor",
        "balcony_area",
        "browsenum",
        "browsenum_all",
        "cartplace",
        "cases_id",
        "comment_total",
        "comment_unread",
        "condition",
        "cover",
        "distance",
        "filename",
        "floor",
        "floor2",
        "address",
        "groundarea",
        "hasimg",
        "house_img",
        "houseage",
        "houseimg",
        "housetype",
        "icon_class",
        "icon_name",
        "houseid",
        "is_combine",
        "isvip",
        "kind",
        "kind_name",
        "kind_name_img",
        "lane_name",
        "layout_str",
        "linkman",
        "living",
        "ltime",
        "nick_name",
        "onepxImg",
        "photoNum",
        "post_id",
        "price_hide",
        "refreshtime",
        "section_name",
        "sectionname",
        "shape",
        "space_type_str",
        "status",
        "storeprice",
        "streetid",
        "type",
        "unit",
        "updatetime",
        "user_id",
        "addInfo",
        "addition2",
        "addition3",
        "addition4",
        "browsenum_name",
        "checkstatus",
        "closed",
        "comment_class",
        "comment_ltime",
        "mainarea",
        "mvip",
        "new_img",
        "new_list_comment_total",
        "photo_alt",
        "region_name",
        "regionid",
        "regionname",
        "search_name",
        "sectionid",
        "vipBorder",
        "vipimg",
        "vipstyle",
    ]
    with open(csv_filename, "w", newline="", encoding="UTF-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


def get_total_house(house_data, headers):
    payload = {
        "is_new_list": house_data["is_new_list"],
        "type": house_data["type"],
        "kind": house_data["kind"],
        "searchtype": house_data["searchtype"],
        "region": house_data["region"],
        "section": house_data["section"],
        "patternMore": house_data["patternMore"],
        "area": house_data["area"],
        "rentprice": house_data["rentprice"],
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


def house_filter(h, prefer_road, not_prefer_community):
    for road in prefer_road:
        if road in h["street_name"]:
            if h["cases_name"] not in not_prefer_community:
                # if "2衛" in h["room"]:
                return h
    return None


user_data = toml.load("user.toml")
house_data = toml.load("rent.toml")
prefer_road = house_data["prefer_road"]
not_prefer_community = house_data["not_prefer_community"]
house_result = get_total_house(house_data, get_headers(user_data))
house_result2 = []
for h in house_result:

    h["houseid"] = f"https://sale.591.com.tw/home/house/detail/2/{h['houseid']}.html"
    if house_filter(h, prefer_road, not_prefer_community):
        house_result2.append(h)

print(f"house after fileter =  {len(house_result2)}")

save_to_csv_file("new_rent.csv", house_result2)
