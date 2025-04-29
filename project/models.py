
# File: project.models.py
# Author: Justin Liao (liaoju@bu.edu), 4/14/2025
# Description: define data models for the  application 

# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
#[[-1,Meats,-1,-1,-1,dairy, -1],
# [-1,-1,pasta,asian,chips,-1, household],
# [-1,-1,-1,-1,candy,-1,-1],
# [-1,fruits, -1,-1,-1,-1,-1],
# [Main,-1,selfcheckout, -1,-1,-1,back]]

import heapq

class Customer(models.Model):


    firstname = models.TextField(blank=True)
    lastname = models.TextField(blank= True)
    address = models.TextField(blank=True)
    email = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):

        return f'{self.firstname} {self.lastname}'
    

class Item(models.Model):

    name = models.TextField(blank=True)
    price = models.FloatField(blank=True)
    aisle = models.TextField(blank=True)
    store = models.ForeignKey("Store", on_delete=models.CASCADE)
    stock = models.IntegerField(blank=True)
    image = models.URLField(blank=True)
    

    def __str__ (self):

        return f'{self.name} Price: {self.price}  Aisle: {self.aisle}  Store: {self.store.name} {self.stock}'


class Store(models.Model):

    name = models.TextField(blank=True)
    address = models.TextField(blank=True)
    zipcode = models.TextField(blank=True)
    layout = models.JSONField(blank=True)
    aisle_distances = models.JSONField(blank=True)



    def remaining_path_cost(self, current, unvisited, end):
        distances = self.aisle_distances
        
        if not unvisited:
            return 0

        unvisited = list(unvisited)

        mst_cost = 0
        visited = set()
        start = unvisited[0]
        visited.add(start)
        edges = []

        for node in unvisited:
            if node != start:
                heapq.heappush(edges, (distances[start][node]["distance"], node))

        while len(visited) < len(unvisited):
            while edges:
                cost, node = heapq.heappop(edges)
                if node not in visited:
                    visited.add(node)
                    mst_cost += cost
                    for neighbor in unvisited:
                        if neighbor not in visited:
                            heapq.heappush(edges, (distances[node][neighbor]["distance"], neighbor))
                    break

        min_end = min(distances[node][end]["distance"] for node in unvisited)

        return mst_cost + min_end


    def A_star_method(self, aisle_to_visit, start, end ):
        route = []
        copy_aisle = set(aisle_to_visit)
        distance = self.aisle_distances
        current = start
        route.append(start)
        while(len(copy_aisle) > 0):
            best_cost = float('inf')
            best_next = ""
            for aisle in copy_aisle: 
                unvisited = copy_aisle -{aisle}
                cost = distance[current][aisle]["distance"]
                cost += self.remaining_path_cost(aisle, unvisited, end)
                print("Cost for" , current, " to " , aisle, cost)
                if cost < best_cost:
                    best_cost = cost
                    best_next = aisle

            route.append(best_next)
            copy_aisle.remove(best_next)
            current = best_next


        
        route.append(end)
        return route



    
    def __str__(self):

        return f'{self.name} Address: {self.address} {self.zipcode} Layout: {self.layout}'
    

class Cart(models.Model):

    name = models.TextField(blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    removed = models.BooleanField(default=False)
    

    def __str__(self):

        return f'{self.name} Customer: {self.customer} Active: {self.is_active} Removed: {self.removed}'

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):

        return f'Cart: {self.cart} Item: {self.item} {self.quantity}'
    

class PastOrder(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField(blank=True)
    items = models.TextField(blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    routes = models.JSONField(default=dict)
    


    def __str__(self):

        return f'{self.customer} {self.timestamp} {self.total_price} {self.items}'



from collections import deque
import json
import itertools



grid = [[-1,"Meats",-1,-1,-1,"Dairy", -1],
[-1,-1,"Pasta","Asian","Chips",-1, "Household"],
[-1,-1,-1,-1,"Candy",-1,-1],
[-1,"Fruits", -1,-1,-1,-1,-1],
["Main",-1,"SelfCheckout", -1,-1,-1,"Back"]]

newgrid = [[-1      ,-1                  ,-1 ,-1 ,-1                        ,-1       ,-1         ,-1         ,-1            ,-1              ,-1              ,-1         ,-1         ,-1                    ,-1        ,-1        ,-1        ,-1               ,-1         ,-1                  ,-1         ,-1         ,-1         ,-1                                 ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,"Fish & Shellfish"  ,0 ,0 ,0                         ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,"Meats"                ,0         ,0         ,0         ,0                ,0         ,"Lunch Meat"         ,0          ,0          ,0          ,"Prepared & Frozen Meat"          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0 ,0 ,0                         ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0 ,"Deli",0                     ,-1       ,0          ,-1         ,0             ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,0          ,"Dairy"    ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0,0,0                          ,-1       ,"Aisle 1"        ,-1         ,0             ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,0                                  ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0,0 ,0                         ,0        ,0          ,"Aisle 2"        ,0             ,0               ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,0          ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,"Prepared Specialty",0,0,0                          ,0        ,-1         ,0          ,-1            ,-1              ,"Aisle 3"             ,0          ,"Aisle 4"        ,0                     ,"Aisle 5"       ,0         ,"Aisle 6"       ,"Frozen"         ,"Aisle 7"         ,0                  ,"Aisle 8"         ,0         ,"Aisle 9"         ,0                                 ,"Aisle 10"       ,0         ,"Aisle 11"         ,0         ,"Aisle 12"       ,0         ,0           ,0          ,0          ,0          ,0          ,0          ,0          ,-1],
           [-1      ,0                   ,0,0,0                          ,0        ,-1         ,0          ,-1            ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1],
           [-1      ,0                   ,0,0,0                          ,"Produce",-1         ,0          ,-1            ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,-1         ,"Aisle 13"       ,0          ,"Aisle 14"       ,0          ,"Aisle 15"       ,-1         ,"Aisle 16"       ,-1],
           [-1      ,0                   ,0,"Nuts & Dried Fruits",0      ,0        ,-1         ,0          ,-1            ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,0          ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1],
           ["Alchol",0                   ,0,"Fresh Fruits",0             ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,"Pharmacy"],
           [-1      ,"Bakery"            ,0,0,0                          ,0        ,0          ,0          ,"SelfCheckOut",0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,"Flower"   ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,-1],
           ["Main"  ,0                   ,0,0,0                          ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,"Back"],
           [-1      ,-1                  ,-1,-1,-1                         ,-1       ,-1         ,-1         ,-1            ,-1              ,-1              ,-1         ,-1         ,-1                    ,-1        ,-1        ,-1        ,-1               ,-1         ,-1                  ,-1         ,-1         ,-1         ,-1                                 ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1]]




{'Fish & Shellfish': (1, 1), 'Meat': (1, 11), 'Lunch Meat': (1, 17), 'Deli': (3, 2), 'Dairy': (3, 28), '1': (4, 4), '2': (5, 5), 'Prepared Specialty': (6, 1), '3': (6, 8), '4': (6, 10), '5': (6, 12), '6': (6, 14), 'Frozen': (6, 15), '7': (6, 16), '8': (6, 18), '9': (6, 20), '10': (6, 22), '11': (6, 24), '12': (6, 26), 'PRoduce': (8, 3), '13': (8, 28), '14': (8, 30), '15': (8, 32), '16': (8, 34), 'Alchol': (10, 0), 'Fruits': (10, 2), 'Pharmacy': (10, 35), 'Baking': (11, 1), 'SelfCheckOut': (11, 6), 'Flower': (11, 25), 'Main': (12, 0), 'Back': (12, 35)}

                                                       
aisle_names = [
    "Fish & Shellfish",
    "Meat",
    "Lunch Meat",
    "Deli",
    "Dairy",
    "1",
    "2",
    "Prepared Specialty",
    "3",
    "4",
    "5",
    "6",
    "Frozen",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "PRoduce",
    "13",
    "14",
    "15",
    "16",
    "Alchol",
    "Fruits",
    "Pharmacy",
    "Baking",
    "SelfCheckOut",
    "Flower",
    "Main",
    "Back"
]


def get_layout(grid):
    layout = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != -1 and grid[r][c] != 0:
                layout[grid[r][c]] = (r, c)
    store = Store.objects.first()
    store.layout = layout
    store.save()
    return layout


def bfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, [start])]) 
    visited = set([start])
    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    while queue:
        (r, c), path = queue.popleft()

        if (r, c) == goal:
            return {
                "distance": len(path) - 1,  
                "path": path
            }

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if (nr, nc) not in visited and grid[nr][nc] != -1:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))
    return {
        "distance": float('inf'),
        "path": []
    }

def compute_aisle_distances(grid, aisles):
    layout = get_layout(grid)
    distances = {}

    for aisle1, aisle2 in itertools.combinations(aisles, 2):
        if aisle1 in layout and aisle2 in layout:
            p1, p2 = layout[aisle1], layout[aisle2]
            dist = bfs(grid, p1, p2)

            distances.setdefault(aisle1, {})[aisle2] = {
                "distance": dist["distance"],
                "path": dist["path"]
            }
            distances.setdefault(aisle2, {})[aisle1] = {
                "distance": dist["distance"],
                "path": dist["path"][::-1] 
            }
    store = Store.objects.first()
    store.aisle_distances = distances
    store.save()

    return distances
import requests
from project.models import Store, Item

def load_items_selenium():
    print("🚀 Starting API-based scraping...")

    url = "https://www.starmarket.com/abs/pub/xapi/pgmsearch/v1/search/products"
    params = {
        "request-id": "1891745535466079608",
        "url": "https://www.starmarket.com",
        "pageurl": "https://www.starmarket.com",
        "pagename": "search",
        "rows": "30",
        "start": "0",
        "search-type": "keyword",
        "storeid": "3588",
        "featured": "true",
        "q": "milk",
        "sort": "",
        "dvid": "web-4.1search",
        "channel": "instore",
        "visitorId": "cdfb214b-71be-4cb1-a0e0-31f230abc96c",
        "pgm": "intg-search,merch-banner",
        "banner": "starmarket"
    }

        
    
    cookies = {
        'visid_incap_2083761': 'PxY/xS2+SY+hRD+O1rqlyyuECmgAAAAAQUIPAAAAAADG9kX39oIjAXk0QYnFfHum',
        'absVisitorId': 'cdfb214b-71be-4cb1-a0e0-31f230abc96c',
        '__pdst': '859f52b29b8941148decf5b2964d2ac6',
        '_pin_unauth': 'dWlkPU56ZGhNamMxTnpFdE5ETm1PUzAwTjJJMkxUZzRZalF0WWpkaU5UWmlaREV5TURZeg',
        '_tt_enable_cookie': '1',
        'signifyd_sessionId': 'a51H6fe3-5184-Peb2-8df3-abbb-2233526_37fe',
        'salsify_session_id': 'dd8a5d34-a005-4ba5-9df1-c21c27a29d0f',
        '_gcl_au': '1.1.493727837.1745519664.1595829133.1745521401.1745521400',
        'OptanonAlertBoxClosed': '2025-04-24T19:54:17.775Z',
        'akacd_PR-bg-www-prod-starmarket': '3922987988~rv=37~id=67ee0846b3d6f2b15dfdcbadbfd622f4',
        'nlbi_2083761': '/RajFZAhtk00D76TgII9VgAAAAD4vyOVrszolFM2cyI3Lakk',
        'incap_ses_130_2083761': 'lvs4KMzcjBSPOrGlMdvNAdXACmgAAAAAPRio9BQgW+fRDj0BNq6brQ==',
        'AMCVS_A7BF3BC75245ADF20A490D4D%40AdobeOrg': '1',
        'AMCV_A7BF3BC75245ADF20A490D4D%40AdobeOrg': '179643557%7CMCIDTS%7C20203%7CMCMID%7C36121588625269096751280557966579584470%7CMCAAMLH-1746139991%7C7%7CMCAAMB-1746139991%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1745542391s%7CNONE%7CvVersion%7C5.5.0',
        'ACI_S_ECommBanner': 'starmarket',
        'ACI_S_ECommSignInCount': '0',
        'at_check': 'true',
        'SAFEWAY_MODAL_LINK': '',
        '_gcl_gs': '2.1.k1$i1745535190$u28901502',
        'SWY_SHARED_SESSION_INFO': '%7B%22info%22%3A%7B%22COMMON%22%3A%7B%22userType%22%3A%22G%22%2C%22zipcode%22%3A%2202215%22%2C%22banner%22%3A%22starmarket%22%2C%22preference%22%3A%22J4U%22%2C%22Selection%22%3A%22user%22%2C%22xDTags%22%3A%22bad_user_agents%2C+non_human%22%2C%22userData%22%3A%7B%7D%2C%22grsSessionId%22%3A%22a9148b4c-3580-4aa1-87e5-fb899236526b%22%2C%22siteType%22%3A%22C%22%2C%22customerType%22%3A%22%22%2C%22resolvedBy%22%3A%22zipcode%22%7D%2C%22J4U%22%3A%7B%22storeId%22%3A%223588%22%2C%22zipcode%22%3A%2202215%22%2C%22userData%22%3A%7B%7D%7D%2C%22SHOP%22%3A%7B%22storeId%22%3A%223588%22%2C%22zipcode%22%3A%2202215%22%2C%22userData%22%3A%7B%7D%7D%7D%7D',
        '_gcl_aw': 'GCL.1745535199.CjwKCAjwwqfABhBcEiwAZJjC3n52Y-u40-QcOMOEMHYbzAlNA2S4gv0lKr-j32_NX4YmTo2rP4pDZxoCdz4QAvD_BwE',
        '_gcl_dc': 'GCL.1745535199.CjwKCAjwwqfABhBcEiwAZJjC3n52Y-u40-QcOMOEMHYbzAlNA2S4gv0lKr-j32_NX4YmTo2rP4pDZxoCdz4QAvD_BwE',
        'gpv_Page': 'starmarket%3Adelivery%3Asearch-results',
        '_uetvid': 'bec23cf0213a11f083b41fbce83a71ff',
        'ttcsid': '1745535192745::r1OSJJh5kn1ebvx-K0EX.5.1745538466569',
        'ttcsid_CEUU933C77UA1PN5K8JG': '1745535192744::xTAlcsun7g_mcYPxn6e-.4.1745538546875',
        'reese84': '3:nNa0XsU4kjgGH41HRUVYVA==:zuvAbHRy+ychHELK0KsSUQ/BH1Tiqzlw7EqHbbggyvuY2Ykw6+NNc/K6DRYJaK70qvZZ5wkF7iApoTywt1f88vxo+GTvnDNq8kwSaIDW6Na64hEQnxon+rKLfsF6/jtn+qvDkcpdrfdxmVMpE081WgNlCquiKZkY77M3mgh9xnXA7a2jMfgURABMVm/4wOXULZfhSjGEGlnug8KQ5QP5n16pz/JD0utHadhMvHH0CAZQa3fyKexxHRBqN0KRrkL/4ju0MKSjJRgCJw+k8JmrBcEx1fIbGnXDgShze324tGstrufcrW3MnULHTEpXA351be6PPD+hmzOst1zZN9qMUlhcmnvCg/Im/f5pLVfGtDRKt6M3x8SZYCH6wVBxauAwcpC7GqlA2SbQL7D2FI8Em31QR6MmJ+ffG6kfkpLbxGYvgwmK6ZGqLZEEyMAmQPqC2vgsO5Zb7hiVQKpwalW0qldOq4ACFz0KwivW4NavnFgaJxDqqb23c2PMAxAr34NxD9AbKqqbbmzJDiDDdRDx+BpljFX2wYhiQd+stTvRCh4=:9Aeg15J8w8l/KPYRESrHUouXrh0XNqbPjec8ooWaT74=',
        's_sq': 'sfsafewayprod1%3D%2526c.%2526a.%2526activitymap.%2526page%253Dstarmarket%25253Adelivery%25253Asearch-results%2526link%253DLoad%252520more%2526region%253Dsearch-grid_0%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dstarmarket%25253Adelivery%25253Asearch-results%2526pidt%253D1%2526oid%253DLoad%252520more%2526oidt%253D3%2526ot%253DSUBMIT',
        '_ga_W73SGEEDQQ': 'GS1.1.1745538466.1.1.1745539496.0.0.0',
        'mbox': 'PC#cdeede6d9d9048ea9adb3e6d4711ea23.34_0#1808784298|session#0f4ec44cf16748608f043520be7724b7#1745541358',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Thu+Apr+24+2025+20%3A04%3A58+GMT-0400+(Eastern+Daylight+Time)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=dd6c9d75-deb0-435b-af88-eb0188406c84&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0003%3A1&AwaitingReconsent=false&intType=3&geolocation=US%3BMA',
        'nlbi_2083761_2147483392': 'J5HUO4m1vQoN5B10gII9VgAAAAARHmT9KJvGT8oAVopUySc2',
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'ocp-apim-subscription-key': '5e790236c84e46338f4290aa1050cdd4',
        'priority': 'u=1, i',
        'referer': 'https://www.starmarket.com/shop/search-results.html?q=a',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        # 'cookie': 'visid_incap_2083761=PxY/xS2+SY+hRD+O1rqlyyuECmgAAAAAQUIPAAAAAADG9kX39oIjAXk0QYnFfHum; absVisitorId=cdfb214b-71be-4cb1-a0e0-31f230abc96c; __pdst=859f52b29b8941148decf5b2964d2ac6; _pin_unauth=dWlkPU56ZGhNamMxTnpFdE5ETm1PUzAwTjJJMkxUZzRZalF0WWpkaU5UWmlaREV5TURZeg; _tt_enable_cookie=1; signifyd_sessionId=a51H6fe3-5184-Peb2-8df3-abbb-2233526_37fe; salsify_session_id=dd8a5d34-a005-4ba5-9df1-c21c27a29d0f; _gcl_au=1.1.493727837.1745519664.1595829133.1745521401.1745521400; OptanonAlertBoxClosed=2025-04-24T19:54:17.775Z; akacd_PR-bg-www-prod-starmarket=3922987988~rv=37~id=67ee0846b3d6f2b15dfdcbadbfd622f4; nlbi_2083761=/RajFZAhtk00D76TgII9VgAAAAD4vyOVrszolFM2cyI3Lakk; incap_ses_130_2083761=lvs4KMzcjBSPOrGlMdvNAdXACmgAAAAAPRio9BQgW+fRDj0BNq6brQ==; AMCVS_A7BF3BC75245ADF20A490D4D%40AdobeOrg=1; AMCV_A7BF3BC75245ADF20A490D4D%40AdobeOrg=179643557%7CMCIDTS%7C20203%7CMCMID%7C36121588625269096751280557966579584470%7CMCAAMLH-1746139991%7C7%7CMCAAMB-1746139991%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1745542391s%7CNONE%7CvVersion%7C5.5.0; ACI_S_ECommBanner=starmarket; ACI_S_ECommSignInCount=0; at_check=true; SAFEWAY_MODAL_LINK=; _gcl_gs=2.1.k1$i1745535190$u28901502; SWY_SHARED_SESSION_INFO=%7B%22info%22%3A%7B%22COMMON%22%3A%7B%22userType%22%3A%22G%22%2C%22zipcode%22%3A%2202215%22%2C%22banner%22%3A%22starmarket%22%2C%22preference%22%3A%22J4U%22%2C%22Selection%22%3A%22user%22%2C%22xDTags%22%3A%22bad_user_agents%2C+non_human%22%2C%22userData%22%3A%7B%7D%2C%22grsSessionId%22%3A%22a9148b4c-3580-4aa1-87e5-fb899236526b%22%2C%22siteType%22%3A%22C%22%2C%22customerType%22%3A%22%22%2C%22resolvedBy%22%3A%22zipcode%22%7D%2C%22J4U%22%3A%7B%22storeId%22%3A%223588%22%2C%22zipcode%22%3A%2202215%22%2C%22userData%22%3A%7B%7D%7D%2C%22SHOP%22%3A%7B%22storeId%22%3A%223588%22%2C%22zipcode%22%3A%2202215%22%2C%22userData%22%3A%7B%7D%7D%7D%7D; _gcl_aw=GCL.1745535199.CjwKCAjwwqfABhBcEiwAZJjC3n52Y-u40-QcOMOEMHYbzAlNA2S4gv0lKr-j32_NX4YmTo2rP4pDZxoCdz4QAvD_BwE; _gcl_dc=GCL.1745535199.CjwKCAjwwqfABhBcEiwAZJjC3n52Y-u40-QcOMOEMHYbzAlNA2S4gv0lKr-j32_NX4YmTo2rP4pDZxoCdz4QAvD_BwE; gpv_Page=starmarket%3Adelivery%3Asearch-results; _uetvid=bec23cf0213a11f083b41fbce83a71ff; ttcsid=1745535192745::r1OSJJh5kn1ebvx-K0EX.5.1745538466569; ttcsid_CEUU933C77UA1PN5K8JG=1745535192744::xTAlcsun7g_mcYPxn6e-.4.1745538546875; reese84=3:nNa0XsU4kjgGH41HRUVYVA==:zuvAbHRy+ychHELK0KsSUQ/BH1Tiqzlw7EqHbbggyvuY2Ykw6+NNc/K6DRYJaK70qvZZ5wkF7iApoTywt1f88vxo+GTvnDNq8kwSaIDW6Na64hEQnxon+rKLfsF6/jtn+qvDkcpdrfdxmVMpE081WgNlCquiKZkY77M3mgh9xnXA7a2jMfgURABMVm/4wOXULZfhSjGEGlnug8KQ5QP5n16pz/JD0utHadhMvHH0CAZQa3fyKexxHRBqN0KRrkL/4ju0MKSjJRgCJw+k8JmrBcEx1fIbGnXDgShze324tGstrufcrW3MnULHTEpXA351be6PPD+hmzOst1zZN9qMUlhcmnvCg/Im/f5pLVfGtDRKt6M3x8SZYCH6wVBxauAwcpC7GqlA2SbQL7D2FI8Em31QR6MmJ+ffG6kfkpLbxGYvgwmK6ZGqLZEEyMAmQPqC2vgsO5Zb7hiVQKpwalW0qldOq4ACFz0KwivW4NavnFgaJxDqqb23c2PMAxAr34NxD9AbKqqbbmzJDiDDdRDx+BpljFX2wYhiQd+stTvRCh4=:9Aeg15J8w8l/KPYRESrHUouXrh0XNqbPjec8ooWaT74=; s_sq=sfsafewayprod1%3D%2526c.%2526a.%2526activitymap.%2526page%253Dstarmarket%25253Adelivery%25253Asearch-results%2526link%253DLoad%252520more%2526region%253Dsearch-grid_0%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dstarmarket%25253Adelivery%25253Asearch-results%2526pidt%253D1%2526oid%253DLoad%252520more%2526oidt%253D3%2526ot%253DSUBMIT; _ga_W73SGEEDQQ=GS1.1.1745538466.1.1.1745539496.0.0.0; mbox=PC#cdeede6d9d9048ea9adb3e6d4711ea23.34_0#1808784298|session#0f4ec44cf16748608f043520be7724b7#1745541358; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Apr+24+2025+20%3A04%3A58+GMT-0400+(Eastern+Daylight+Time)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=dd6c9d75-deb0-435b-af88-eb0188406c84&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0003%3A1&AwaitingReconsent=false&intType=3&geolocation=US%3BMA; nlbi_2083761_2147483392=J5HUO4m1vQoN5B10gII9VgAAAAARHmT9KJvGT8oAVopUySc2',
    }

    response = requests.get(
    'https://www.starmarket.com/abs/pub/xapi/pgmsearch/v1/search/products?request-id=1341745539983970716&url=https://www.starmarket.com&pageurl=https://www.starmarket.com&pagename=search&rows=30&start=540&search-type=keyword&storeid=3588&featured=true&q=a&sort=&dvid=web-4.1search&channel=instore&visitorId=cdfb214b-71be-4cb1-a0e0-31f230abc96c&pgm=intg-search,merch-banner&banner=starmarket&nextPageToken=cDZhBTZjNmMhNDNk1SMiFTOtY2N3ITLwADMw0iY4EjZjJDO2QiGrAs0oChBAv7jpjwCSADN1MgC',
        cookies=cookies,
        headers=headers,
    )
    response.raise_for_status()
    data = response.json()
    

    products = data.get("primaryProducts", {}).get("response", {}).get("docs", [])
    if not products:
        print("⚠️ No products found.")
        
    store = Store.objects.get(name= "Star Market")
    for product in products:
        name = product.get("name")
        price = product.get("price")
        image = product.get("imageUrl")
        aisle = product.get("aisleLocation") or product.get("aisleName", "Unknown")
        stock = int(product.get("inventoryAvailable", 0))

        if not name or not price:
            continue

        if not Item.objects.filter(name=name, store=store).exists():
            Item.objects.create(
                name=name,
                price=price,
                aisle=aisle,
                store=store,
                stock=stock,
                image=image
            )
            print(f"✅ Added: {name} — ${price} — Aisle: {aisle}")
        else:
            print(f"🔁 Already exists: {name}")


    print("✅ Done loading items.")