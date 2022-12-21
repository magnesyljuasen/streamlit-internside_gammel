

class Geoenergy:
    def __init__(self, demand_arr, temperature, cop, thermal_conductivity, groundwater_table, coverage):
        self.energy_arr = demand_arr.flatten()
        self.energy_sum = np.sum(self.energy_arr)
        self.coverage = coverage
        self.cop = cop
        self.energy_gshp_arr = np.array(0)
        self.energy_gshp_sum = int
        self.heat_pump_size = float

        self.temperature = temperature
        self.thermal_conductivity = thermal_conductivity
        self.groundwater_table = groundwater_table
        self.demand_calculation()
        self.pygfunction_calculation([60, 70, 80, 90, 100, 110], 3, 2)
        self.wellnumber_calculation()
        self.show_results()
        
    def demand_calculation(self):
        self.energy_gshp_arr, self.energy_gshp_sum, self.heat_pump_size = self.coverage_calculation()
        self.heat_pump_size_adjustment()
        self.energy_gshp_delivered_arr, self.energy_gshp_compressor_arr, self.energy_gshp_peak_arr, \
        self.energy_gshp_delivered_sum, self.energy_gshp_compressor_sum, self.energy_gshp_peak_sum = self.cop_calculation()



    def cop_calculation(self):
        cop = self.cop
        energy_arr = self.energy_arr
        energy_gshp_arr = self.energy_gshp_arr
        energy_gshp_delivered_arr = energy_gshp_arr - energy_gshp_arr / cop
        energy_gshp_compressor_arr = energy_gshp_arr - energy_gshp_delivered_arr
        energy_gshp_peak_arr = energy_arr - energy_gshp_arr

        energy_gshp_delivered_sum = int(np.sum(energy_gshp_delivered_arr))
        energy_gshp_compressor_sum = int(np.sum(energy_gshp_compressor_arr))
        energy_gshp_peak_sum = int(np.sum(energy_gshp_peak_arr))

        return energy_gshp_delivered_arr, energy_gshp_compressor_arr, energy_gshp_peak_arr, energy_gshp_delivered_sum, energy_gshp_compressor_sum, energy_gshp_peak_sum

    def diagram(self):
        wide_form = pd.DataFrame({
            'Varighet (timer)' : np.array(range(0, len(self.energy_arr))),
            'Spisslast (ikke bergvarme)' : np.sort(self.energy_arr)[::-1], 
            'Levert energi fra brønn(er)' : np.sort(self.energy_gshp_arr)[::-1],
            'Strømforbruk varmepumpe' : np.sort(self.energy_gshp_compressor_arr)[::-1]
            })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast (ikke bergvarme)', 'Levert energi fra brønn(er)', 'Strømforbruk varmepumpe'],
            as_=['key', 'Effekt (kW)']).mark_area().encode(
                x=alt.X('Varighet (timer):Q', scale=alt.Scale(domain=[0, 8760])),
                y='Effekt (kW):Q',
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast (ikke bergvarme)', 'Levert energi fra brønn(er)', 'Strømforbruk varmepumpe'], 
                range=['#ffdb9a', '#48a23f', '#1d3c34']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)

    def show_results(self):
        #st.subheader("Forenklet dimensjonering")
        number_of_wells = self.number_of_wells
        meters = self.meter
        heat_pump_size = self.heat_pump_size
        text = " brønn"
        text1 = " energibrønn"
        text2 = "dybde"
        
        column_1, column_2 = st.columns(2)
        with column_1:
            svg = """ <svg width="27" height="35" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip0"><rect x="505" y="120" width="27" height="26"/></clipPath></defs><g clip-path="url(#clip0)" transform="translate(-505 -120)"><path d="M18.6875 10.8333C20.9312 10.8333 22.75 12.6522 22.75 14.8958 22.75 17.1395 20.9312 18.9583 18.6875 18.9583L2.97917 18.9583C2.82959 18.9583 2.70833 19.0796 2.70833 19.2292 2.70833 19.3787 2.82959 19.5 2.97917 19.5L18.6875 19.5C21.2303 19.5 23.2917 17.4386 23.2917 14.8958 23.2917 12.353 21.2303 10.2917 18.6875 10.2917L3.63946 10.2917C3.63797 10.2916 3.63678 10.2904 3.63678 10.2889 3.6368 10.2882 3.63708 10.2875 3.63756 10.2871L7.23315 6.69148C7.33706 6.58388 7.33409 6.41244 7.22648 6.30852 7.12154 6.20715 6.95514 6.20715 6.85019 6.30852L2.78769 10.371C2.68196 10.4768 2.68196 10.6482 2.78769 10.754L6.85019 14.8165C6.95779 14.9204 7.12923 14.9174 7.23315 14.8098 7.33452 14.7049 7.33452 14.5385 7.23315 14.4335L3.63756 10.8379C3.63651 10.8369 3.63653 10.8351 3.63759 10.8341 3.6381 10.8336 3.63875 10.8333 3.63946 10.8333Z" stroke="#1D3C34" stroke-width="0.270833" fill="#1D3C34" transform="matrix(6.12323e-17 1 -1.03846 6.35874e-17 532 120)"/></g></svg>"""
            render_svg(svg)
            st.metric(label="Brønndybde ", value=f"{int(meters)} m")
        with column_2:
            svg = """ <svg width="31" height="35" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip0"><rect x="395" y="267" width="31" height="26"/></clipPath></defs><g clip-path="url(#clip0)" transform="translate(-395 -267)"><path d="M24.3005 0.230906 28.8817 0.230906 28.8817 25.7691 24.3005 25.7691Z" stroke="#1E3D35" stroke-width="0.461812" stroke-linecap="round" stroke-miterlimit="10" fill="#F0F3E3" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M1.40391 2.48455 1.40391 25.5936 6.41918 25.5936 6.41918 2.48455C4.70124 1.49627 3.02948 1.44085 1.40391 2.48455Z" stroke="#1E3D35" stroke-width="0.461812" stroke-linecap="round" stroke-miterlimit="10" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M24.3005 25.7691 1.23766 25.7691" stroke="#1F3E36" stroke-width="0.461812" stroke-linecap="round" stroke-miterlimit="10" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M24.3005 0.230906 6.59467 0.230906 6.59467 25.7691" stroke="#1F3E36" stroke-width="0.461812" stroke-linecap="round" stroke-miterlimit="10" fill="#FBFDF6" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M24.3005 17.6874 6.59467 17.6874" stroke="#1F3E36" stroke-width="0.461812" stroke-linecap="round" stroke-miterlimit="10" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M24.3005 8.33108 6.59467 8.33108" stroke="#1F3E36" stroke-width="0.461812" stroke-linecap="round" stroke-miterlimit="10" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M9.71652 12.4874 10.1691 12.4874 10.1691 14.0114 11.222 14.7133 11.222 16.108 10.2153 16.8007 9.71652 16.8007" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M9.72575 12.4874 9.26394 12.4874 9.26394 14.0114 8.22025 14.7133 8.22025 16.108 9.21776 16.8007 9.72575 16.8007" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M14.27 12.4874 14.7226 12.4874 14.7226 14.0114 15.7663 14.7133 15.7663 16.108 14.7687 16.8007 14.27 16.8007" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M14.27 12.4874 13.8174 12.4874 13.8174 14.0114 12.7645 14.7133 12.7645 16.108 13.7712 16.8007 14.27 16.8007" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M1.40391 5.90195 0.230906 5.90195 0.230906 10.9542 1.40391 10.9542" stroke="#1E3D35" stroke-width="0.461812" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M1.40391 13.0046 0.230906 13.0046 0.230906 25.0025 1.40391 25.0025" stroke="#1E3D35" stroke-width="0.461812" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M28.0412 4.58117 25.2611 4.58117 25.2611 2.73393 25.2611 2.10586 28.0412 2.10586 28.0412 4.58117Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M25.4366 2.73393 28.0412 2.73393" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M25.4366 3.34352 28.0412 3.34352" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M25.4366 3.95311 28.0412 3.95311" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M9.71652 20.6799 10.1691 20.6799 10.1691 22.2131 11.222 22.9059 11.222 24.3005 10.2153 25.0025 9.71652 25.0025" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M9.72575 20.6799 9.26394 20.6799 9.26394 22.2131 8.22025 22.9059 8.22025 24.3005 9.21776 25.0025 9.72575 25.0025" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M14.27 20.6799 14.7226 20.6799 14.7226 22.2131 15.7663 22.9059 15.7663 24.3005 14.7687 25.0025 14.27 25.0025" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M14.27 20.6799 13.8174 20.6799 13.8174 22.2131 12.7645 22.9059 12.7645 24.3005 13.7712 25.0025 14.27 25.0025" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M20.0149 1.05293 23.4139 1.05293 23.4139 7.56448 20.0149 7.56448Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M17.9552 13.0046 23.4046 13.0046 23.4046 15.5538 17.9552 15.5538Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M19.0913 11.6931C19.0913 11.9073 18.9176 12.081 18.7034 12.081 18.4891 12.081 18.3155 11.9073 18.3155 11.6931 18.3155 11.4788 18.4891 11.3052 18.7034 11.3052 18.9176 11.3052 19.0913 11.4788 19.0913 11.6931Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M18.7034 13.0046 18.7034 12.081" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M20.4028 11.6931C20.4028 11.9073 20.2292 12.081 20.0149 12.081 19.8007 12.081 19.627 11.9073 19.627 11.6931 19.627 11.4788 19.8007 11.3052 20.0149 11.3052 20.2292 11.3052 20.4028 11.4788 20.4028 11.6931Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M20.0149 13.0046 20.0149 12.081" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M21.7421 11.6931C21.7421 11.9073 21.5684 12.081 21.3542 12.081 21.1399 12.081 20.9663 11.9073 20.9663 11.6931 20.9663 11.4788 21.1399 11.3052 21.3542 11.3052 21.5684 11.3052 21.7421 11.4788 21.7421 11.6931Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M21.3542 13.0046 21.3542 12.081" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M23.0536 11.6931C23.0536 11.9073 22.88 12.081 22.6657 12.081 22.4515 12.081 22.2778 11.9073 22.2778 11.6931 22.2778 11.4788 22.4515 11.3052 22.6657 11.3052 22.88 11.3052 23.0536 11.4788 23.0536 11.6931Z" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="#F3F8E8" transform="matrix(1.04327 0 0 1 395.314 267)"/><path d="M22.6657 13.0046 22.6657 12.081" stroke="#1E3D35" stroke-width="0.230906" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="matrix(1.04327 0 0 1 395.314 267)"/></g></svg>"""
            render_svg(svg)
            st.metric(label="Varmepumpestørrelse", value=str(int(heat_pump_size)) + " kW")

        if number_of_wells > 1:
            text = " brønner" 
            text1 = " energibrønner"
            text2 = "total dybde"
            st.info(f"Brønndybden bør fordeles på {number_of_wells} brønner á {int(meters/number_of_wells)} m med 15 meter avstand")

        with st.expander("Mer om brønndybde og varmepumpestørrelse"):
            
            st.write(""" Vi har gjort en forenklet beregning for å dimensjonere et bergvarmeanlegg med 
            energibrønn og varmepumpe for din bolig. Dybde på energibrønn og størrelse på varmepumpe 
            beregnes ut ifra et anslått oppvarmingsbehov for boligen din og antakelser om 
            egenskapene til berggrunnen der du bor. Varmepumpestørrelsen gjelder on/off 
            og ikke varmepumper med inverterstyrt kompressor.""")

            st.write('**Energi- og effekt**')
            self.diagram()
            st.write('**Simulert temperatur (borehullsveggen)**')
            self.borehole_temperature()
            st.caption(f""" kWh/meter {self.kWh_per_meter} og min temp {int(self.min_temperature)} grader""")
        
            st.write(""" Før du kan installere bergvarme, må entreprenøren gjøre en grundigere beregning. 
            Den må baseres på reelt oppvarmings- og kjølebehov, en mer nøyaktig vurdering av grunnforholdene, 
            inkludert berggrunnens termiske egenskaper, og simuleringer av temperaturen i energibrønnen. """)

            
            
