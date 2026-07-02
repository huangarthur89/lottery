import itertools

def generate_wheel2(pool_size, ticket_size, draw_hits, guarantee_hits):
    pool = list(range(1, pool_size + 1))
    universe = list(itertools.combinations(pool, draw_hits))
    tickets = list(itertools.combinations(pool, ticket_size))
    
    ticket_coverage = []
    for t in tickets:
        t_set = set(t)
        covered = set()
        for i, u in enumerate(universe):
            if len(set(u).intersection(t_set)) >= guarantee_hits:
                covered.add(i)
        ticket_coverage.append((t, covered))
        
    uncovered_universe = set(range(len(universe)))
    selected_tickets = []
    
    while uncovered_universe:
        best_ticket = None
        best_cover = set()
        for t, covered in ticket_coverage:
            current_cover = covered.intersection(uncovered_universe)
            if len(current_cover) > len(best_cover):
                best_cover = current_cover
                best_ticket = t
        
        selected_tickets.append(list(best_ticket))
        uncovered_universe -= best_cover
        
    return selected_tickets

w8_4_3 = generate_wheel2(8, 6, 4, 3)
w8_5_4 = generate_wheel2(8, 6, 5, 4)
w10_3_3 = generate_wheel2(10, 6, 3, 3)
w10_4_4 = generate_wheel2(10, 6, 4, 4)
w12_3_3 = generate_wheel2(12, 6, 3, 3)

with open("wheel_data.py", "w") as f:
    f.write(f"WHEEL_8_4_3 = {w8_4_3}\n")
    f.write(f"WHEEL_8_5_4 = {w8_5_4}\n")
    f.write(f"WHEEL_10_3_3 = {w10_3_3}\n")
    f.write(f"WHEEL_10_4_4 = {w10_4_4}\n")
    f.write(f"WHEEL_12_3_3 = {w12_3_3}\n")

print("Generated.")
print(f"8 numbers 4 if 3: {len(w8_4_3)} tickets")
print(f"8 numbers 5 if 4: {len(w8_5_4)} tickets")
print(f"10 numbers 3 if 3: {len(w10_3_3)} tickets")
print(f"10 numbers 4 if 4: {len(w10_4_4)} tickets")
print(f"12 numbers 3 if 3: {len(w12_3_3)} tickets")
