
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
                heapq.heappush(edges, (distances[start][node], node))

        while len(visited) < len(unvisited):
            while edges:
                cost, node = heapq.heappop(edges)
                if node not in visited:
                    visited.add(node)
                    mst_cost += cost
                    for neighbor in unvisited:
                        if neighbor not in visited:
                            heapq.heappush(edges, (distances[node][neighbor], neighbor))
                    break

        min_end = min(distances[node][end] for node in unvisited)

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
                cost = distance[current][aisle]
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


def get_layout(grid):
    layout = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != -1 and grid[r][c] != "#":
                layout[grid[r][c]] = (r, c)
    return layout

def bfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, 0)])
    visited = set([start])
    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    while queue:
        (r, c), dist = queue.popleft()
        if (r, c) == goal:
            return dist

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if (nr, nc) not in visited:
                    if grid[nr][nc] != "#":
                        visited.add((nr, nc))
                        queue.append(((nr, nc), dist + 1))

    return float('inf')  

def compute_aisle_distances(grid, aisles):
    layout = get_layout(grid)
    distances = {}

    for aisle1, aisle2 in itertools.combinations(aisles, 2):
        if aisle1 in layout and aisle2 in layout:
            p1, p2 = layout[aisle1], layout[aisle2]
            dist = bfs(grid, p1, p2)

            distances.setdefault(aisle1, {})[aisle2] = dist
            distances.setdefault(aisle2, {})[aisle1] = dist

    return distances