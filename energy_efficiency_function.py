import numpy as np
from auxiliary_functions import * 

def calculate_energy_efficiency(wind_farm):

    # Initialize an empty dictionary to store the results
    results = {}

    for w_i in range(0, len(wind_farm.w_direction)):
        # For each wind direction, calculate the power generated by each turbine
        p_generated = []
        p_generated_without_wake = []
        for t_k in range(0, wind_farm.N_turbines):
            # Calculate the rotor area of turbine t_k
            A_k = np.pi * wind_farm.R_r ** 2

            # Calculate the power generated by turbine t_k without the wake effect and the thrust coefficient
            p_ideal_k, C_k = get_power_and_thrust(wind_farm.w_speed[w_i], wind_farm.p_curve)

            other_turbines = [t for t in range(0, wind_farm.N_turbines) if t != t_k]

            #print(f'other turbines:', other_turbines)
            
            sum_u_kj = 0

            #print(other_turbines)
            for t_j in other_turbines:
                #print(f'turbine {t_k} in the wake of turbine {t_j}')
                #print(f'turbine {t_j} coordinates:', coordinates[t_j])
                # Calculate the distance between turbine t_k and t_j
                dist_kj, c_kj = calculate_distances(
                    wind_farm.coordinates[t_k][0],
                    wind_farm.coordinates[t_k][1],
                    wind_farm.coordinates[t_j][0],
                    wind_farm.coordinates[t_j][1],
                    wind_farm.w_direction[w_i]
                )

                #print(f'distance between turbine {t_k} and {t_j}:', dist_kj)
            
                # Calculate the distance between turbine t_j and t_k
                dist_jk, c_jk = calculate_distances(
                    wind_farm.coordinates[t_j][0],
                    wind_farm.coordinates[t_j][1],
                    wind_farm.coordinates[t_k][0],
                    wind_farm.coordinates[t_k][1],
                    wind_farm.w_direction[w_i]
                )
                #
                R_kj = wind_farm.R_r + wind_farm.xi * dist_kj

                # Calculate the rotor area of turbine t_j in the wake of turbine t_i
                
                if c_kj > R_kj: 
                    A_kj = 0 
                elif  c_kj + wind_farm.R_r <= R_kj:
                    A_kj = np.pi * wind_farm.R_r ** 2
                else: 
                    A_kj = calculate_Ak_j(
                        R_kj,
                        wind_farm.R_r,
                        c_jk,
                        c_kj
                    )

                #print(f'rotor area of turbine {t_k}:', A_k)
                print(f'rotor area of turbine {t_k} in the wake of {t_j} is:', A_kj)

                # Interference caused on turbine k by turbine j
                u_kj = (1 - np.sqrt(1 - C_k)) / (1 + wind_farm.xi * dist_kj / wind_farm.R_r)**2 *  (A_kj / A_k)

                sum_u_kj += u_kj**2

            # Calculate the velocity experienced by the turbine t_k in the wake of all other turbines
            u_j = wind_farm.w_speed[w_i] * (1 - np.sqrt(sum_u_kj))
            print(f'velocity experienced by turbine {t_k} in the wake of all other turbines:', u_j)
            #print(f'c_kj:', c_kj)
            #print(f'R+:', R_kj + R_r)
            #print(f'R_:', R_kj - R_r)


            # Calculate the power generated by turbine t_k in the wake of all other turbines
            p_k = get_power_and_thrust(u_j, wind_farm.p_curve)[0]

            p_generated.append(p_k)
            p_generated_without_wake.append(p_ideal_k)

        # Store the results for this w_direction
        results[wind_farm.w_direction[w_i]] = {
        'p_generated': p_generated,
        'p_generated_without_wake': p_generated_without_wake
        }


    # calculate the energy production 

    term1 = sum([ sum(results[wind_farm.w_direction[w]]['p_generated'][t] * wind_farm.w_frequency[w] for t in range(0, wind_farm.N_turbines)) for w in range(0,len(wind_farm.w_direction))])

    term2 = sum([ wind_farm.N_turbines * results[wind_farm.w_direction[w]]['p_generated_without_wake'][0] * wind_farm.w_frequency[w] for w in range(0,len(wind_farm.w_direction))])
        
    e_production = term1 / term2
    print('Energy production:', e_production)
    
    return e_production

