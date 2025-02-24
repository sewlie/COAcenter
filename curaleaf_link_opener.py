import webbrowser
import time

base_url = "https://coas.curaleaf.com/transparency/"

endings = [
    "002A", "007A", "062A", "064A", "065A", "066A", "069A", "070A", "071A", "072A", "073A", "075A",
    "083A", "086A", "087A", "088A", "089A", "096A", "098A", "100A", "101A", "103A", "1055A", "105A",
    "1314A", "1379A", "1383A", "1385A", "1392A", "1453A", "1454A", "1476A", "1481A", "1484A", "1486A",
    "1487A", "1490A", "1491A", "1494A", "1496A", "1498A", "1566A", "1568A", "1578A", "1582A", "1583A",
    "1587A", "1589A", "1596A", "1597A", "1598A", "1599A", "1601A", "1603A", "1604A", "1614A", "792B",
    "796B", "956A", "979B"
]

for ending in endings:
    full_url = base_url + ending
    webbrowser.open_new_tab(full_url)
    time.sleep(2)  # 2-second delay between opening each tab
