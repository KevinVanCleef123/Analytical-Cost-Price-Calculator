Location = input("Location: ")
Mthd_Name = input("Name of the method: ")
Avg_Cost_Tech = input("Average annual costs of a lab technician: ")
Avg_Cont_Hrs = input("Average FTE contract hours: ")
Ttl_Tests_Mthd_Year = input("Total number of tests performed with this method per year: ")
Ttl_Tests_Lab_Year = input("Total number of tests performed in the lab per year: ")
Actv_Wrk_Tm_Run = input("Active work time per run (Minutes): ")
Smpls_Run = input("Samples per run: ")
Wait_Time = input("Wait time during test (e.g., drying, centrifuging, etc.: ")
Eqpmnt_Wrt_off = input("Equipment Write-off: ")
Int_Mnt_Tm = input("What time is spend in minutes to maintain a method (e.g., Line controls, Training, First line equipment maintenance etc.: ")
Ext_Mnt_Cst = input("Costs for maintenance by suppliers: ")

raw_input = input("Enter equipment as: Name,Price,Yes/No; ...\n")
equipment_list = []

for item in raw_input.split(";"):
    name, price, exclusive = item.strip().split(",")
    equipment_list.append({
        "name": name.strip(),
        "price": float(price),
        "exclusive": exclusive.strip().lower() == "yes"
    })

raw_input = input("Enter material as: Name,Price,Unit, Reagent/Material/Reusable; ...\n")
material_list = []

for item in raw_input.split(";"):
    name, price, unit, type = item.strip().split(",")
    material_list.append({
        "name": name.strip(),
        "price": float(price.strip()),
        "unit": float(unit.strip()),
        "type": type.strip()
    })

MnHrRt = float(Avg_Cost_Tech) / float(Avg_Cont_Hrs)

def calculate_labour_cost(Avg_Cost_Tech, Avg_Cont_Hrs, Actv_Wrk_Tm_Run, Smpls_Run):
        return ((float(Actv_Wrk_Tm_Run) / float(Smpls_Run)) * (MnHrRt / 60))

def calculate_maintenance_cost(Int_Mnt_Tm, Ext_Mnt_Cst, Avg_Cont_Hrs, MnHrRt, Ttl_Tests_Mthd_Year):
    return (((float(Int_Mnt_Tm)/float(Avg_Cont_Hrs)) * (MnHrRt / 60))+(float(Ext_Mnt_Cst)/float(Ttl_Tests_Mthd_Year)))

def calculate_other_opex(Wait_Time, Smpls_Run):
    return ((float(Wait_Time) * 0.05)/float(Smpls_Run))

def calculate_equipment_costs(equipment_list, Eqpmnt_Wrt_off, Ttl_Tests_Mthd_Year, Ttl_Tests_Lab_Year):
    capex_total = 0
    general_equipment_total = 0

    for item in equipment_list:
        price = item["price"]
        exclusive = item["exclusive"]
        write_off = float(Eqpmnt_Wrt_off)

        if price > 5000:
            # Capex: depreciated over write-off period and divided by method-specific tests
            capex_cost = price / (write_off * float(Ttl_Tests_Mthd_Year))
            capex_total += capex_cost
        else:
            # General equipment cost: depends on exclusivity
            if exclusive:
                gen_cost = price / (8 * 0.7 * float(Ttl_Tests_Lab_Year))
            else:
                gen_cost = price / (8 * float(Ttl_Tests_Mthd_Year))
            general_equipment_total += gen_cost

    return capex_total, general_equipment_total

def calculate_material_cost(material_list):
    Reusable_material_total = 0
    Reagent_total = 0
    Material_total = 0

    for item in material_list:
        price = item["price"]
        unit = item["unit"]
        mtype = item["type"]  # renamed to avoid conflict with built-in `type`

        if mtype == "Reusable":
            Reusable_material_total += (price *unit) /100
        elif mtype == "Reagent":
            Reagent_total += price * unit
        elif mtype == "Material":
            Material_total += price * unit
        else:
            print(f"Warning: Unknown material type '{mtype}' for item '{item['name']}'")

    return Reusable_material_total, Reagent_total, Material_total

def calculate_total_and_shares(labour_cost, maintenance_cost, capex_cost, general_equipment_cost, reusable_material_cost, reagent_cost, material_cost, other_opex):
    # Total cost price
    total_cost_price = (labour_cost + maintenance_cost + capex_cost + general_equipment_cost + reusable_material_cost + reagent_cost + material_cost + other_opex)

    # Calculate shares
    labour_share = (labour_cost / total_cost_price) * 100
    capex_share = (capex_cost / total_cost_price) * 100
    non_fte_share = ((general_equipment_cost + reagent_cost + material_cost) / total_cost_price) * 100
    opex_share = ((maintenance_cost + other_opex) / total_cost_price) * 100

    return total_cost_price, {"Labour %": labour_share, "Capex %": capex_share, "Non-FTE %": non_fte_share, "Opex %": opex_share }

print("Location: ", Location)
print("Method: ", Mthd_Name)
print("Manhour rate: ",MnHrRt)
print("Labour costs: ", calculate_labour_cost(Avg_Cost_Tech, Avg_Cont_Hrs, Actv_Wrk_Tm_Run, Smpls_Run))
print("Maintenance costs: ", calculate_maintenance_cost(Int_Mnt_Tm, Ext_Mnt_Cst, Avg_Cont_Hrs, MnHrRt, Ttl_Tests_Mthd_Year))
print("Capex and General equipment Total: ", calculate_equipment_costs(equipment_list, Eqpmnt_Wrt_off, Ttl_Tests_Mthd_Year, Ttl_Tests_Lab_Year))
print("Material and Reagent costs: ", calculate_material_cost(material_list))
print("Other OPEX: ", calculate_other_opex(Wait_Time, Smpls_Run))

total_cost_price, shares = calculate_total_and_shares(
    calculate_labour_cost(Avg_Cost_Tech, Avg_Cont_Hrs, Actv_Wrk_Tm_Run, Smpls_Run),
    calculate_maintenance_cost(Int_Mnt_Tm, Ext_Mnt_Cst, Avg_Cont_Hrs, MnHrRt, Ttl_Tests_Mthd_Year),
    calculate_equipment_costs(equipment_list, Eqpmnt_Wrt_off, Ttl_Tests_Mthd_Year, Ttl_Tests_Lab_Year)[0],
    calculate_equipment_costs(equipment_list, Eqpmnt_Wrt_off, Ttl_Tests_Mthd_Year, Ttl_Tests_Lab_Year)[1],
    calculate_material_cost(material_list)[0],
    calculate_material_cost(material_list)[1],
    calculate_material_cost(material_list)[2],
    calculate_other_opex(Wait_Time, Smpls_Run)
)

labour_cost = calculate_labour_cost(Avg_Cost_Tech, Avg_Cont_Hrs, Actv_Wrk_Tm_Run, Smpls_Run)
maintenance_cost = calculate_maintenance_cost(Int_Mnt_Tm, Ext_Mnt_Cst, Avg_Cont_Hrs, MnHrRt, Ttl_Tests_Mthd_Year)
capex_cost, general_equipment_cost = calculate_equipment_costs(equipment_list, Eqpmnt_Wrt_off, Ttl_Tests_Mthd_Year, Ttl_Tests_Lab_Year)
reusable_material_cost, reagent_cost, material_cost = calculate_material_cost(material_list)
other_opex = calculate_other_opex(Wait_Time, Smpls_Run)

total_cost_price, shares = calculate_total_and_shares(
    labour_cost,
    maintenance_cost,
    capex_cost,
    general_equipment_cost,
    reusable_material_cost,
    reagent_cost,
    material_cost,
    other_opex
)

print("\n--- Final Summary ---")
print(f"Total Cost Price: {total_cost_price:.4f}")
for key, value in shares.items():
    print(f"{key}: {value:.2f}%")