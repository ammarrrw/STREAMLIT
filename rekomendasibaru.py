import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sistem Rekomendasi Asupan Nutrisi Seimbang", layout="wide")

# Streamlit states initialization
if 'person' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations=None
    st.session_state.person=None
    st.session_state.weight_loss_option=None

class Person:
    def __init__(self,age,height,weight,gender):
        self.age=age
        self.height=height
        self.weight=weight
        self.gender=gender
        #self.activity=activity
    def calculate_bmi(self,):
        bmi=round(self.weight/((self.height/100)**2),2)
        return bmi

    def display_result(self,):
        bmi=self.calculate_bmi()
        bmi_string=f'{bmi} kg/m²'
        if bmi<=16.99:
            category='Kekurangan berat badan tingkat berat'
            color='Red'
        elif 17.0<=bmi<18.49:
            category='Kekurangan berat badan tingkat ringan'
            color='Yellow'
        elif 18.5<=bmi<24.99:
            category='Normal'
            color='Green'
        elif 25.0<=bmi<29.99:
            category='Kelebihan berat badan tingkat ringan'
            color='Yellow'
        else:
            category='Kelebihan berat badan tingkat berat'
            color='Red'
        return bmi_string,category,color

    def calculate_bmr(self):
        if self.gender=='Laki-Laki':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        return bmr

    def calories_calculator(self):
        bmi=self.calculate_bmi()
        if bmi<17:
            weight = 1.9
        elif 17.1<=bmi<18.4:
            weight = 1.725
        elif 18.5<=bmi<25:
            weight = 1.55
        elif 25.1<=bmi<27.0:
            weight = 1.375
        else:
            weight = 1.2

        maintain_calories = self.calculate_bmr()*weight
        return maintain_calories

class Display:
    def __init__(self):
        pass

    def display_bmi(self,person):
        st.header('Indeks Masa Tubuh (IMT)')
        bmi_string,category,color = person.display_result()
        st.metric(label="", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 25px;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.markdown(
            """
            Rentang BMI Sehat: 18.5 kg/m² - 25 kg/m².
            """)

    def display_calories(self,person):
        st.header('Kebutuhan Kalori')   
        total_kalori=person.calories_calculator()
        st.metric(label="", value=(round(total_kalori)))



def generate_menu(dataset, total_kalori):
    menu = []
    satukalimakan = total_kalori / 3

    for waktu, items in dataset.items():
        if dataset is makanan_pokok:
            kalori = satukalimakan * 38.57 / 100
        elif dataset is sayuran:
            kalori = satukalimakan * 25.14 / 100
        elif dataset is lauk_hewani or dataset is lauk_nabati:
            kalori = (satukalimakan * 25 / 100) / 2
        else:
            kalori = satukalimakan * 11.28 / 100

        for idx, item in items.iterrows():
            gram = kalori / item['Kalori'] * 100
            protein = (kalori * item['Protein']) / 100
            lemak = (kalori * item['Lemak']) / 100
            karbohidrat = (kalori * item['Karbohidrat']) / 100

            menu.append({
                'waktu': waktu,
                'nama': item['Nama Bahan'],
                'jumlah_gram': round(gram),
                'jumlah_kalori': round(kalori),
                'jumlah_protein': round(protein, 2),
                'jumlah_lemak': round(lemak, 2),
                'jumlah_karbohidrat': round(karbohidrat, 2)
            })
    return menu

def main():
    global makanan_pokok, lauk_hewani, lauk_nabati, sayuran, buah

    # Load datasets
    makanan_pokok = pd.read_csv("Makanan Pokok.csv")
    lauk_hewani = pd.read_csv("Lauk Pauk (Hewani).csv")
    lauk_nabati = pd.read_csv("Lauk Pauk (Nabati).csv")
    sayuran = pd.read_csv("Sayuran.csv")
    buah = pd.read_csv("Buah.csv")
    
    def random_dataset(data):
        waktu = ['Pagi', 'Siang', 'Malam']
        split_values = np.linspace(0, len(data), 4).astype(int)
        split_values[-1] = split_values[-1] - 1
        frac_data = data.sample(frac=1).reset_index(drop=True)
        data_waktu = []
        for s in range(len(split_values)-1):
            data_waktu.append(frac_data.loc[split_values[s]:split_values[s+1]].head(3))
        return dict(zip(waktu, data_waktu))

    # Generate random datasets
    makanan_pokok = random_dataset(makanan_pokok)
    lauk_hewani = random_dataset(lauk_hewani)
    lauk_nabati = random_dataset(lauk_nabati)
    sayuran = random_dataset(sayuran)
    buah = random_dataset(buah)

    # Generate menus
    total_kalori=person.calories_calculator()
    Menu = generate_menu(makanan_pokok, total_kalori)
    Menu.extend(generate_menu(sayuran, total_kalori))
    Menu.extend(generate_menu(lauk_hewani, total_kalori))
    Menu.extend(generate_menu(lauk_nabati, total_kalori))
    Menu.extend(generate_menu(buah, total_kalori))

    # Membuat dictionary kosong untuk menyimpan data sesuai dengan waktu
    data_waktu = {'Pagi': [], 'Siang': [], 'Malam': []}

    # Memisahkan data sesuai dengan waktu dan menyimpannya dalam dictionary
    for item in Menu:
        waktujadi = item['waktu']
        data_waktu[waktujadi].append(item)

    data_pagi = data_waktu['Pagi']
    data_siang = data_waktu['Siang']
    data_malam = data_waktu['Malam']

    indeks1 = [0, 3, 6, 9, 12]
    indeks2 = [1, 4, 7, 10, 13]
    indeks3 = [2, 5, 8, 11, 14]

    # Menyimpan makanan pagi, siang, dan malam ke dalam tiga kategori
    menu_pagi = [[], [], []]
    menu_siang = [[], [], []]
    menu_malam = [[], [], []]

    # Menyusun makanan ke dalam tiga kategori
    for idx, makanan_idx in enumerate([indeks1, indeks2, indeks3]):
        for idx_makanan in makanan_idx:
            makanan = data_pagi[idx_makanan]
            menu_pagi[idx].append(makanan)

    for idx, makanan_idx in enumerate([indeks1, indeks2, indeks3]):
        for idx_makanan in makanan_idx:
            makanan = data_siang[idx_makanan]
            menu_siang[idx].append(makanan)

    for idx, makanan_idx in enumerate([indeks1, indeks2, indeks3]):
        for idx_makanan in makanan_idx:
            makanan = data_malam[idx_makanan]
            menu_malam[idx].append(makanan)


    # Menampilkan menu
    col1, col2, col3 = st.columns(3)

    # Menampilkan menu pagi di kolom pertama
    with col1:
        st.write("Menu Pagi:")
        for i, item in enumerate(menu_pagi, start=1):
            total_protein = sum(m['jumlah_protein'] for m in item)
            total_lemak = sum(m['jumlah_lemak'] for m in item)
            total_karbohidrat = sum(m['jumlah_karbohidrat'] for m in item)

            meal_name = f"Pagi {i}"
            expander = st.expander(f"Menu {meal_name}")
            for makanan in item:
                nama_makanan = makanan['nama']
                jumlah_gram = makanan['jumlah_gram']
                jumlah_kalori = makanan['jumlah_kalori']
                expander.write(f"{nama_makanan} - {jumlah_gram} gram - {jumlah_kalori} kkal")
            expander.write("")
            expander.write(f"Total protein: {total_protein:.2f} gram")
            expander.write(f"Total lemak: {total_lemak:.2f} gram")
            expander.write(f"Total karbohidrat: {total_karbohidrat:.2f} gram")

    # Menampilkan menu siang di kolom kedua
    with col2:
        st.write("Menu Siang:")
        for i, item in enumerate(menu_siang, start=1):
            total_protein = sum(m['jumlah_protein'] for m in item)
            total_lemak = sum(m['jumlah_lemak'] for m in item)
            total_karbohidrat = sum(m['jumlah_karbohidrat'] for m in item)

            meal_name = f"Siang {i}"
            expander = st.expander(f"Menu {meal_name}")
            for makanan in item:
                nama_makanan = makanan['nama']
                jumlah_gram = makanan['jumlah_gram']
                jumlah_kalori = makanan['jumlah_kalori']
                expander.write(f"{nama_makanan} - {jumlah_gram} gram - {jumlah_kalori} kkal")
            expander.write("")
            expander.write(f"Total protein: {total_protein:.2f} gram")
            expander.write(f"Total lemak: {total_lemak:.2f} gram")
            expander.write(f"Total karbohidrat: {total_karbohidrat:.2f} gram")
    # Menampilkan menu malam di kolom ketiga
    with col3:
        st.write("Menu Malam:")
        for i, item in enumerate(menu_malam, start=1):
            total_protein = sum(m['jumlah_protein'] for m in item)
            total_lemak = sum(m['jumlah_lemak'] for m in item)
            total_karbohidrat = sum(m['jumlah_karbohidrat'] for m in item)
            
            meal_name = f"Malam {i}"
            expander = st.expander(f"Menu {meal_name}")
            for makanan in item:
                nama_makanan = makanan['nama']
                jumlah_gram = makanan['jumlah_gram']
                jumlah_kalori = makanan['jumlah_kalori']
                expander.write(f"{nama_makanan} - {jumlah_gram} gram - {jumlah_kalori} kkal")
            expander.write("")
            expander.write(f"Total protein: {total_protein:.2f} gram")
            expander.write(f"Total lemak: {total_lemak:.2f} gram")
            expander.write(f"Total karbohidrat: {total_karbohidrat:.2f} gram")



# Streamlit app
title="<h1 style='text-align: center;'>Rekomendasi Menu Makanan</h1>"
st.markdown(title, unsafe_allow_html=True)
with st.form("recommendation_form"):
    st.write("Sesuaikan data dan klik tombol \"Buat Rekomendasi\" untuk mendapatkan rekomendasi menu")
    age = st.number_input('Umur',min_value=10, max_value=120, step=1)
    height = st.number_input('Tinggi(cm)',min_value=100, max_value=300, step=1)
    weight = st.number_input('Berat(kg)',min_value=10, max_value=300, step=1)
    gender = st.radio('Gender',('Laki-Laki','Perempuan'))
    # activity = st.select_slider('Aktifitas',options=['Sangat jarang olahraga ', 'Jarang olahraga', 'Olahraga Menengah (3-5 hari/minggu)', 
    # 'Sering Berolahraga (6-7 hari/minggu)', 'Sangat sering olahraga'])
    
    generated = st.form_submit_button("Buat Rekomendasi")

if generated:
    st.session_state.generated=True
    person = Person(age,height,weight,gender)
    display=Display()
    with st.container():
        display.display_bmi(person)
    with st.container():
        display.display_calories(person) 
    main()
