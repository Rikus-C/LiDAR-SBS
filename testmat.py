import math

def calculate_errors(L1D, L2D, L1A, L2A, ox):
    c = 50
    #L1A = -(90+L1A)
    #L2A = -(L2A-90)
    x1 = L1D * math.cos(L1A)
    x2 = L2D * math.cos(L2A)

    y1 = L1D * math.sin(L1A)
    y2 = L2D * math.sin(L2A)

    L1 = math.sqrt(y1*y1 + (c + x1)*(c + x1))
    L2 = math.sqrt(y2*y2 + (c + x2)*(c + x2))
    print("L1", L1)
    print("L2", L2)

    S1 = 180 - L1A
    S2 = 180 - L2A

    B1 = math.asin(((L1D * math.sin(S1))/L1)) 
    B2 = math.asin(((L2D * math.sin(S2))/L2))

    roll = math.atan((((L1 * math.sin(B1)) + (L2 * math.sin(B2*3.14/180)) )/ ((L2 * math.cos(B2*3.14/180)) + (L1 * math.cos(B1*3.14/180))))) * 180/3.14
    y = L1 * math.sin((B1 - roll)*3.14/180)
    x = L1 * math.cos((B1 - roll)*3.14/180) - c - ox

    print(x)
    print(y)
    print(roll)

v1 = 208.205
v2 = 208.205
v3 = 7
v4 = 7
v5 = 200
calculate_errors(v1, v2, v3, v4, v5)