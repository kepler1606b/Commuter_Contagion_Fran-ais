#l'interface


import math
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data import create_stm_data
from simulation import MetroSim

class SimApp:


    def __init__(self, root):
        #construit l'interface visuelle en divisant la fenêtre en deux : un panneau gauche pour les contrôles et un panneau droit pour le graphique et crée tous les menus déroulants (type de masque, ventilation) et les curseurs interactifs

        self.root = root


        self.root.title('Commuter Contagion')
        self.root.geometry('1400x850')
        
        create_stm_data()

        try:
            self.df = pd.read_csv('stm_orange_line_clean.csv')


        except Exception as e:
            messagebox.showerror('Startup Error', f"Couldn't load default dataset: {e}")

            return

        
        self.saved_scenario = None
        
        
        self.results_df = None
        
        self.inf_rate = 0.0

        left_panel = ttk.Frame(self.root, padding='10', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        right_panel = ttk.Frame(self.root, padding='10')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Button(left_panel, text='Load Custom CSV', command=self.load_file).pack(fill=tk.X, pady=5)


        ttk.Label(left_panel, text='Time of Day', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        self.tod_var = tk.StringVar(value='AM_Peak')
        ttk.Combobox(left_panel, textvariable=self.tod_var, values=['AM_Peak', 'Off_Peak'], state='readonly').pack(fill=tk.X)



        ttk.Label(left_panel, text='HVAC System', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        self.hvac_var = tk.StringVar(value='Conventional (Ceiling Exhaust)')


        hvac_opts =['Conventional (Ceiling Exhaust)', 'Proposed (Floor Exhaust - Nazari)', 'Hybrid (Floor Supply - Chang)']




        ttk.Combobox(left_panel, textvariable=self.hvac_var, values=hvac_opts, state='readonly').pack(fill=tk.X)
        ttk.Label(left_panel, text='Mask Type', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        self.mask_var = tk.StringVar(value='N95 (99.6%)')
        mask_opts =['N95 (99.6%)', 'Surgical (80%)', 'Cloth (60%)', 'No Mask']
        ttk.Combobox(left_panel, textvariable=self.mask_var, values=mask_opts, state='readonly').pack(fill=tk.X)
        self.lbl_speed = ttk.Label(left_panel, text='Train Speed (km/h): 40.0', font=('Arial', 10, 'bold'))
        self.lbl_speed.pack(anchor=tk.W, pady=(15,0))
        self.speed = tk.DoubleVar(value=40.0)
        ttk.Scale(left_panel, from_=15.0, to=80.0, variable=self.speed, orient=tk.HORIZONTAL,
                  
                  command=lambda v: self.lbl_speed.config(text=f'Train Speed (km/h): {float(v):.1f}')).pack(fill=tk.X)
        self.lbl_ach = ttk.Label(left_panel, text='Ventilation ACH: 10.0', font=('Arial', 10, 'bold'))
        self.lbl_ach.pack(anchor=tk.W, pady=(10,0))
        self.ach = tk.DoubleVar(value=10.0)
        ttk.Scale(left_panel, from_=4.0, to=18.0, variable=self.ach, orient=tk.HORIZONTAL,
                  command=lambda v: self.lbl_ach.config(text=f'Ventilation ACH: {float(v):.1f}')).pack(fill=tk.X)
        self.lbl_comp = ttk.Label(left_panel, text='Mask Compliance: 0%', font=('Arial', 10, 'bold'))
        self.lbl_comp.pack(anchor=tk.W, pady=(10,0))
        self.compliance = tk.DoubleVar(value=0.0)
        ttk.Scale(left_panel, from_=0.0, to=100.0, variable=self.compliance, orient=tk.HORIZONTAL,
                  command=lambda v: self.lbl_comp.config(text=f'Mask Compliance: {float(v):.0f}%')).pack(fill=tk.X)
        ttk.Button(left_panel, text='Run Simulation', command=self.run_sim).pack(fill=tk.X, pady=(25,5))
        ttk.Button(left_panel, text='Lock as Scenario A', command=self.save_scenario).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text='Export Results', command=self.export_csv).pack(fill=tk.X, pady=5)



        self.scenario_label = ttk.Label(right_panel, text='Scenario A: None', font=('Arial', 9, 'italic'), foreground='gray')


        self.scenario_label.pack(anchor=tk.W)
        

        self.fig, self.ax = plt.subplots(figsize=(10, 6))

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)



        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_file(self):


        #permet d'importer des données externes en ouvrant une fenêtre de dialogue Windows/Mac pour choisir un fichier CSV personnalisé
        
        path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv')])
        if not path: 
            return
            
        
        try:
            self.df = pd.read_csv(path, comment='#')
            messagebox.showinfo('Loaded', f'Got {len(self.df)} stations.')
        
        except Exception as e:
            messagebox.showerror('Error', f'Bad file:\n{str(e)}')

    def run_sim(self):
        
        #connecte vos choix visuels au moteur mathématique en lisant les valeurs de l'interface et configure l'objet MetroSim et après fait une boucle sur chaque station faisant avancer le train en enregistrant le nombre total d'infections dans un tableau de résultats
        
        if self.df is None: 
            messagebox.showwarning('Missing Data', 'Load a CSV first.')
            return
            
        df = self.df.copy()
        is_am = 'AM' in self.tod_var.get()
        col_on = 'boarding_on_AM' if is_am else 'boarding_off_peak'
        col_off = 'boarding_off_AM' if is_am else 'descending_off_peak'
        sim = MetroSim()
        sim.ach = self.ach.get()
        sim.hvac = self.hvac_var.get()
        sim.mask_compliance = self.compliance.get() / 100.0
        


        m_type = self.mask_var.get()
        
        
        if 'N95' in m_type:
            sim.mask_eff_out = 0.996
            sim.mask_eff_in = 0.996
        
        
        elif 'Surgical' in m_type:
            sim.mask_eff_out = 0.59
            sim.mask_eff_in = 0.51
        
        
        elif 'Cloth' in m_type:
            sim.mask_eff_out = 0.51
            sim.mask_eff_in = 0.44
        
        
        else:
            sim.mask_eff_out = 0.0
            sim.mask_eff_in = 0.0

        


        
        results =[]
        total_inf = 0





        try:
            
            start_station = df.iloc[0]
            
            initial_on = math.ceil(start_station[col_on] / 9)
            


            sim.seed_train(initial_on, infectious_count=1)
            

            results.append({
                'Station': start_station['Station'], 
                'Pop': int(sim.pax), 
                'New': 0, 
                'Total': 0
            })

            
            for i in range(len(df) - 1):
                distance_km = df.iloc[i]['distance_in_km']
                travel_s = (distance_km / self.speed.get()) * 3600 if distance_km > 0 else 0
                

                
                new_cases = 0
                if travel_s > 0:
                    new_cases = sim.run_leg(travel_s)
                    total_inf += new_cases


                next_st = df.iloc[i + 1]
                off = math.ceil(next_st[col_off] / 9)
                on = math.ceil(next_st[col_on] / 9)
                
                sim.stop_at_station(off, on)
                

                results.append({
                    'Station': next_st['Station'], 
                    'Pop': int(sim.pax), 
                    'New': new_cases, 
                    'Total': total_inf
                })

        except KeyError as e:
            messagebox.showerror('Data Error', f'Missing column: {e}')
            return



        self.results_df = pd.DataFrame(results)
        


        
        if sim.tot_pax > 0:
            self.inf_rate = (total_inf / sim.tot_pax) * 100
        
        
        else:
            self.inf_rate = 0.0
            
        self.update_plot()



    def update_plot(self):
        #dessine le graphique des infections en utilisant la bibliothèque Matplotlib pour tracer une courbe montrant l'évolution des cas cumulés à chaque station.

        self.ax.clear()
       
        x = range(len(self.results_df))
        
        if self.saved_scenario is not None:
            
            
            self.ax.plot(x, self.saved_scenario['Total'], 'r--x', label='Scenario A')
            
        self.ax.plot(x, self.results_df['Total'], 'b-o', lw=2, label='Current')
        
        final_val = self.results_df['Total'].iloc[-1]
        
        
        self.ax.annotate(
            f'{final_val:.4f}', 
            xy=(len(self.results_df) - 1, final_val), 
            xytext=(-50, 15),
            textcoords='offset points', 
            fontsize=10, 
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='blue', alpha=0.8)
        )
                         
        self.ax.set_title(f"HRV Exposures — Orange Line ({self.tod_var.get()})\nTotal Exposed: {self.inf_rate:.2f}% of historical passengers")
        self.ax.set_ylabel('Total Exposures (Cumulative Exposures)')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.results_df['Station'], rotation=60, ha='right', fontsize=8)
        self.ax.legend()
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.fig.tight_layout()
        self.canvas.draw()



    def save_scenario(self):
        
        #permet de comparer deux simulations. Ainsi, il sauvegarde les résultats actuels en mémoire et les affiche en arrière plan.
        
        
        if self.results_df is None:
            
            messagebox.showwarning('Hold on', 'Run it once before locking.')
            return
            
        self.saved_scenario = self.results_df.copy()
        mask_clean = self.mask_var.get().split('(')[0].strip()
        hvac_clean = self.hvac_var.get().split()[0]
        info = f"A: {self.tod_var.get()} | {self.speed.get():.0f}km/h | {self.ach.get():.0f}ACH | {self.compliance.get():.0f}% {mask_clean} | {hvac_clean}"
        self.scenario_label.config(text=info)
        messagebox.showinfo('Locked', 'Scenario A saved. Change settings and run again to compare.')


    def export_csv(self):
        #sauvegarde vos résultats de simulation, il ouvre une fenêtre pour enregistrer les données finales dans un nouveau fichier CSV sur l'ordinateur
        
        if self.results_df is None:
            messagebox.showwarning('Hold on', 'Nothing to export yet.')
            return
            
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV", "*.csv")])
        
        if not path: 
            return
        
        
        try:
            
            with open(path, 'w') as f:
                header = f"# {self.tod_var.get()} | {self.speed.get():.0f}km/h | ACH: {self.ach.get():.0f} | {self.hvac_var.get()} | {self.mask_var.get()} @ {self.compliance.get():.0f}%\n\n"
                f.write(header)
                
            self.results_df.to_csv(path, mode='a', index=False)
            messagebox.showinfo('Done', f'Saved to {path}')
            
        
        except Exception as e:
            
            messagebox.showerror('Export Failed', f'Error saving file:\n{e}')