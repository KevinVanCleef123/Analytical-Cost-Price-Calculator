from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json

    MnHrRt = float(data['Avg_Cost_Tech']) / float(data['Avg_Cont_Hrs'])

    def calculate_labour_cost():
        return ((float(data['Actv_Wrk_Tm_Run']) / float(data['Smpls_Run'])) * (MnHrRt / 60))

    def calculate_maintenance_cost():
        return (((float(data['Int_Mnt_Tm']) / float(data['Avg_Cont_Hrs'])) * (MnHrRt / 60)) +
                (float(data['Ext_Mnt_Cst']) / float(data['Ttl_Tests_Mthd_Year'])))

    def calculate_other_opex():
        return ((float(data['Wait_Time']) * 0.05) / float(data['Smpls_Run']))

    def calculate_equipment_costs():
        capex_total = 0
        general_equipment_total = 0
        for item in data['equipment']:
            price = float(item['price'])
            exclusive = item['exclusive']
            if price > 5000:
                capex_total += price / (float(data['Eqpmnt_Wrt_off']) * float(data['Ttl_Tests_Mthd_Year']))
            else:
                if exclusive:
                    general_equipment_total += price / (8 * 0.7 * float(data['Ttl_Tests_Lab_Year']))
                else:
                    general_equipment_total += price / (8 * float(data['Ttl_Tests_Mthd_Year']))
        return capex_total, general_equipment_total

    def calculate_material_cost():
        reusable, reagent, material = 0, 0, 0
        for item in data['materials']:
            price = float(item['price'])
            unit = float(item['unit'])
            mtype = item['type']
            if mtype == "Reusable":
                reusable += (price * unit) / 100
            elif mtype == "Reagent":
                reagent += price * unit
            elif mtype == "Material":
                material += price * unit
        return reusable, reagent, material

    labour_cost = calculate_labour_cost()
    maintenance_cost = calculate_maintenance_cost()
    capex_cost, general_equipment_cost = calculate_equipment_costs()
    reusable_cost, reagent_cost, material_cost = calculate_material_cost()
    other_opex = calculate_other_opex()

    total = labour_cost + maintenance_cost + capex_cost + general_equipment_cost + reusable_cost + reagent_cost + material_cost + other_opex
    shares = {
        "Labour %": (labour_cost / total) * 100,
        "Capex %": (capex_cost / total) * 100,
        "Non-FTE %": ((general_equipment_cost + reagent_cost + material_cost) / total) * 100,
        "Opex %": ((maintenance_cost + other_opex) / total) * 100
    }

    return jsonify({
        "Total Cost Price": round(total, 4),
        "Shares": {k: round(v, 2) for k, v in shares.items()}
    })

if __name__ == '__main__':
    app.run(debug=True)
