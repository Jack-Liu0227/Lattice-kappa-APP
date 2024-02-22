
#!/user/bin/env python3
# -*- coding: utf-8 -*-
#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os,glob

import streamlit_scripts.file_op as fo
import streamlit_scripts.chang_model as cm
import streamlit_scripts.calculate_K as calk

import streamlit as st
import pandas as pd
import predict

def display_results(df):
    formula=r"$$\Kappa_L=\frac{G V_s V^{\frac{1}{3}}}{N T} \cdot e^{-\gamma}$$"
    template=f"""
            The volume of the crystal structure is {df["Volume (Å3)"].iloc[0]} Å$^3$.<br>
            The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"].iloc[0]} GPa.<br>
            The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"].iloc[0]} GPa.<br>
            The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"].iloc[0]} m/s.<br>
            The Grunisen parameter of the crystal structure is {df["Grüneisen parameter"].iloc[0]}.<br>
            The formula of the lattice thermal conductivity is: {formula}.<br>
            The calculated lattice thermal conductivity is {df["Kappa_cal"].iloc[0]} W/(m·K).<br>
            """
    return template
def app():
    st.title("AI4Kappa")
    sour_path = os.path.abspath('.')
    root_dir="root_dir"
    root_dir_path=os.path.join(sour_path,root_dir)
    model_path=os.path.join(sour_path,"model")
    uploaded_files = st.sidebar.file_uploader("Please upload the primitive cell CIF not the conventional cell CIF!!!",['cif'],accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            save_path = os.path.join(root_dir_path, file_name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.write(f"File saved: {file_name}")

        cif_path_list = glob.glob(os.path.join(root_dir_path, '*.cif'))
        for i in range(len(cif_path_list)):
            cif_file_path = cif_path_list[i]
            if fo.is_valid_cif(cif_file_path):
                pass
            else:
                cif_name = os.path.basename(cif_file_path)
                st.write(f"{cif_name} Invalid CIF file with no structures!")
                os.remove(cif_file_path)
                st.write(f"In order to prevent program errors, invalid CIF file {cif_name} has been deleted.")
        if len(glob.glob(os.path.join(root_dir_path, '*.cif'))):
            cif_path_list,cif_name_list=fo.create_id_prop(root_dir_path)
            first_cif_path=cif_path_list[0]
            cry_content = fo.get_crystalline_content(first_cif_path)
            results_csv_path = os.path.join(sour_path, "test_results.csv")
            model_path_list, model_name_list = cm.get_model_path(model_path)
            cm.copy_model(model_path_list[0], sour_path)
            predict.main(root_dir_path)
            pre_df = cm.get_pre_dataframe(results_csv_path, model_name_list[0])
            for model_path, model_name in zip(model_path_list[1:], model_name_list[1:]):
                cm.copy_model(model_path, sour_path)
                predict.main(root_dir_path)
                pre_df1 = cm.get_pre_dataframe(results_csv_path, model_name)
                pre_df = pd.merge(pre_df, pre_df1, left_index=True, right_index=True)
            try:
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                whole_info_df = pd.merge(all_cry_df, pre_df, left_index=True, right_index=True)
                speed_df = calk.cal_speed(whole_info_df)
                gamma_df = calk.cal_gamma(speed_df)
                final_df = calk.by_formula(gamma_df )
                st.write("---")
                ls = ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)",
                      "Bulk modulus (GPa)", "Shear modulus (GPa)", "Sound velocity of the transverse wave (m s-1)",
                      "Sound velocity of the longitude wave (m s-1)", "Speed of sound (m s-1)",
                      "Poisson ratio", "Grüneisen parameter", "Acoustic Debye Temperature (K)", "Kappa_cal"]
                specify_col_index = [ls[0], ls[1], ls[2], ls[3], ls[4], ls[5], ls[6], ls[7], ls[8],  ls[10],ls[12]]
                final_df = final_df.loc[:, specify_col_index]
                st.dataframe(final_df)
                st.write("---")
                st.write(f"The file name of displaying crystalline is: {final_df.index[0]}")
                st.write("The information of uploaded crystal structure is:")
                st.write(cry_content, unsafe_allow_html=True)
                st.write("---")
                template = display_results(final_df)
                st.markdown(template, unsafe_allow_html=True)

            except Exception as e:
                st.write(e)
            fo.del_cif_file(root_dir_path)

    else:
        st.title('Please upload primitive cell CIF file')
    declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using Al4Kappa on their own. 
        We will happily fix issues in the documentation and examples should you find any, 
        however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
    st.write("---")
    st.markdown(declaration, unsafe_allow_html=True)
