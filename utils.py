import math

def lerp(a: float, b: float, t:float):
    return (1-t)*a+t*b

def add_vectors(a: list[float], b: list[float]):
    return [a[0]+b[0], a[1]+b[1]]

def sub_vectors(a, b):
    return add_vectors(a, scale_vector(b, -1))

def scale_vector(a: list[float], s: float):
    return [a[0]*s, a[1]*s]

def square_dist(a: list[float], b: list[float]):
    return (a[0]-b[0])**2+(a[1]-b[1])**2
def dist(a, b):
    return math.sqrt(square_dist(a,b))
def vector_size(a):
    return dist(a, [0,0])

def vectors_eq(a: list[float], b: list[float]):
    return a[0] == b[0] and a[1] == b[1]