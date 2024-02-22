#!/user/bin/env python3
# -*- coding: utf-8 -*-
#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob

import streamlit_scripts.file_op as fo
import streamlit_scripts.chang_model as cm
import streamlit_scripts.calculate_K as calk

import streamlit as st
import pandas as pd
import predict

def display_results(df):
    formula=r"$$\kappa_L=A\frac{M V^{\frac{1}{3}} \theta_a^3}{\gamma^2 T n} $$"
    try:
        template=f"""
                The number of atoms of the crystal structure is {df["Number of Atoms"][0]}.<br>
                The volume of the crystal structure is {df["Volume (Å3)"][0]} Å$^3$.<br>
                The total atomic mass of the crystal structure is {df["the total atomic mass (amu)"][0]} amu.<br>
                The Bulk modulus of the crystal structure is {df["Bulk modulus (GPa)"][0]} GPa.<br>
                The Shear modulus of the crystal structure is {df["Shear modulus (GPa)"][0]} GPa.<br>
                The sound velocity of the crystal structure is {df["Speed of sound (m s-1)"][0]} m/s.<br>
                The Acoustic Debye Temperature  of the crystal structure is {df["Acoustic Debye Temperature (K)"][0]} K.<br>
                The Grunisen parameter of the crystal structure is {df["Grüneisen parameter"][0]}.<br>
                The formula of the lattice thermal conductivity is: {formula}.<br>
                The calculated lattice thermal conductivity is {df["Kappa_Slack"][0]} W/(m·K).<br>
                """
    except Exception as e:
        st.write(e)
    return template

def app():
    sour_path = os.path.abspath('.')
    root_dir="root_dir"
    root_dir_path=os.path.join(sour_path,root_dir)
    model_path=os.path.join(sour_path,"model")
    st.title("Slack Model")
    uploaded_files = st.sidebar.file_uploader("Please upload the primitive cell CIF not the conventional cell CIF!!!",['cif'],accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            if "CIF" in file_name:
                file_name=file_name.replace("CIF","cif")
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

        cif_path_list,cif_name_list=fo.create_id_prop(root_dir_path)
        if len( glob.glob(os.path.join(root_dir_path, '*.cif'))):
            first_cif_path=cif_path_list[0]
            cry_content = fo.get_crystalline_content(first_cif_path)
            results_csv_path = os.path.join(sour_path, "test_results.csv")
            model_path_list, model_name_list = cm.get_model_path(model_path)
            cm.copy_model(model_path_list[0], sour_path)
            predict.main(root_dir_path)
            pre_df = cm.get_pre_dataframe(results_csv_path, model_name_list[0])
            for model_path, model_name in zip(model_path_list[1:], model_name_list[1:]):
                cm.copy_model(model_path, sour_path)
                try:
                    predict.main(root_dir_path)
                    pre_df1 = cm.get_pre_dataframe(results_csv_path, model_name)
                    pre_df = pd.merge(pre_df, pre_df1, left_index=True, right_index=True)
                except Exception as e:
                    st.write(e)
            try:
                st.write("---")
                all_cry_df = fo.get_dir_crystalline_data(root_dir_path)
                whole_info_df = pd.merge(all_cry_df, pre_df, left_index=True, right_index=True)
                speed_df=calk.cal_speed(whole_info_df)
                Debye_df = calk.cal_Debye_T(speed_df)
                gamma_df=calk.cal_gamma(Debye_df)
                A_df = calk.cal_A(gamma_df, 1)
                K_slack_df = calk.cal_K_Slack(A_df)
                ls = ["Number of Atoms", "Density (g cm-3)", "Volume (Å3)", "the total atomic mass (amu)",
                      "Bulk modulus (GPa)", "Shear modulus (GPa)", "Sound velocity of the transverse wave (m s-1)",
                      "Sound velocity of the longitude wave (m s-1)", "Speed of sound (m s-1)",
                      "Poisson ratio", "Grüneisen parameter", "Acoustic Debye Temperature (K)", "Kappa_Slack"]
                specify_col_index = [ls[0], ls[1], ls[2], ls[3], ls[4], ls[5], ls[6], ls[7], ls[8], ls[9], ls[10],
                                     ls[11], ls[12]]
                final_df = K_slack_df.loc[:, specify_col_index]
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

    with st.container():
        st.write("---")
        declaration = """<p style='font-size: 22px;'>We strive to have clear documentation and examples to help everyone with using Al4Kappa on their own. 
            We will happily fix issues in the documentation and examples should you find any, 
            however, we will not be able to offer extensive user support and training, except for our collaborators.</p>"""
        st.markdown(declaration, unsafe_allow_html=True)