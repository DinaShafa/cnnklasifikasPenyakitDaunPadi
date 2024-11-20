import streamlit as st
import sqlite3
from streamlit_authenticator import Authenticate
import hashlib
from PIL import Image
import numpy as np
import tensorflow as tf
print(tf.__version__)

# Streamlit UI Elements
st.set_page_config(page_title="SmartFARM", page_icon="🌾")

# Logo and title in the sidebar
st.sidebar.image("images\logo1.jpg", width=100)
st.sidebar.image("images\logo2.jpg", width=100)
#st.sidebar.title("🌾" "SmartFARM")

# Check if session_state is a dictionary-like object
if not isinstance(st.session_state, dict):
    st.session_state = {}  # Reset session_state to an empty dictionary

# Initialize default values if not already set
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Load the model with custom objects if needed
# Definisikan kelas CustomLayer jika model Anda menggunakannya
class CustomLayer(tf.keras.layers.Layer):
    def __init__(self):
        super().__init__()

    def build(self, input_shape):
        pass

    def call(self, inputs):
        return inputs  # Example functionality

# Try loading the model with custom objects
try:
    model = tf.keras.models.load_model(
        'CNN-Leaf Diseases Exception-83.33.h5',
        custom_objects={'CustomLayer': CustomLayer}
    )
    print("Model loaded successfully")
except Exception as e:
    print("Error loading model:", e)

# Class info for disease descriptions and solutions
class_info = {
    'Bacterial leaf blight': {
        'description': "Penyakit bakteri yang menyebabkan bercak coklat besar pada daun dan sering kali disertai daun menguning.",
        'solution': "Buang daun yang terinfeksi, gunakan antibiotik nabati, dan hindari penyiraman berlebihan untuk mencegah penyebaran bakteri."
    },
    'Brown spot': {
        'description': "Penyakit yang menimbulkan bercak coklat pada daun dan dapat menyebar secara cepat.",
        'solution': "Tingkatkan ventilasi sekitar tanaman, pangkas bagian yang terinfeksi, dan gunakan fungisida bila diperlukan."
    },
    'Leaf smut': {
        'description': "Penyakit yang ditandai dengan bercak kecil pada daun, biasanya akibat infeksi jamur.",
        'solution': "Semprotkan fungisida secara berkala dan jaga kelembapan daun untuk mencegah penyebaran jamur."
    }
}

# Preprocess image function
def preprocess_image(image):
    image = image.resize((224, 224))
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = image_array / 255.0
    return image_array

# Function to display prediction results
def display_prediction(predicted_label):
    info = class_info[predicted_label]
    st.write(f"**Klasifikasi**: ***{predicted_label}***")
    st.write(f"**Pengertian**: {info['description']}")
    st.write(f"**Solusi**: {info['solution']}")

# Password hash function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database connection and functions
def create_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, is_admin INTEGER)''')
    conn.commit()
    conn.close()

def add_user(username, password, is_admin=0):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)', (username, hash_password(password), is_admin))
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def is_admin(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT is_admin FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] == 1 if result else False

# Profile Page
def profile_page():
    st.title("Profile Anda")
    st.write(f"Username Saat Ini: {st.session_state['username']}")
    new_username = st.text_input("Ubah Username", value=st.session_state["username"])
    new_password = st.text_input("Ubah Password", type="password")
    confirm_password = st.text_input("Konfirmasi Password", type="password")
    
    if st.button("Perbarui Profil"):
        if new_password == confirm_password:
            update_user_profile(st.session_state["username"], new_username, new_password)
            st.session_state["username"] = new_username
            st.success("Profil berhasil diperbarui. Silakan login kembali dengan username baru.")
            logout()  # Logout after updating profile
        else:
            st.error("Password tidak cocok. Silakan coba lagi.")

def update_user_profile(current_username, new_username, new_password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE users SET username=?, password=? WHERE username=?', 
              (new_username, hash_password(new_password), current_username))
    conn.commit()
    conn.close()

# Initialize database
create_db()

# Login and Register
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = verify_user(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Login gagal, username atau password salah.")

def register():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password == confirm_password:
            add_user(username, password)
            st.success("Akun berhasil dibuat! Silakan login.")
        else:
            st.error("Password tidak cocok.")

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.rerun()

# Main Page
def home_page():
    st.title("Tanaman Padi")
    image_path = "images/padi.jpg"  # Make sure the image file is in this path
    st.image(image_path, caption="Rice Plant (Padi)", use_container_width=True)
    st.write("Padi (Oryza sativa) adalah tanaman serealia yang menjadi sumber makanan pokok utama bagi sebagian besar populasi dunia, terutama di Asia. Beras, hasil olahan dari bulir padi, merupakan sumber karbohidrat yang sangat penting. Tanaman ini memiliki akar serabut, batang yang terdiri dari ruas-ruas, dan daun yang panjang dan sempit. Bunga padi tersusun dalam malai, dan buahnya berupa bulir yang mengandung beras.")
    st.write("Padi sangat penting sebagai sumber bahan pangan di Indonesia maupun di Asia. Sebagai sumber makanan pokok dari padi, beras adalah sumber energi utama bagi jutaan orang.  Sebagian besar wilayah Indonesia menanam padi yang menjadikannya komoditas pertanian yang sangat penting, baik untuk konsumsi dalam negeri maupun ekspor. Tanaman padi juga memiliki nilai budaya yang sangat tinggi di banyak masyarakat.")
    st.write("Proses budidaya padi melibatkan berbagai tahapan, mulai dari pemilihan varietas, pengolahan tanah, penanaman, pemupukan, hingga panen. Namun, budidaya padi seringkali dihadapkan pada berbagai tantangan seperti serangan hama dan penyakit, kekurangan nutrisi, serta kondisi iklim yang ekstrem.")
    st.write("Beberapa cara merawat padi dengan benar:")
    st.write("1. Penyiraman yang tepat\n2. Pemberian pupuk yang sesuai\n3. Perlindungan terhadap hama dan penyakit.")
    
    st.subheader("Penyakit Pada Daun Padi")
    st.write("Beberapa jenis penyakit daun padi antara lain:")
    image_path = "images/BLB.jpg"  # Make sure the image file is in this path
    st.image(image_path, caption="Bacterial Leaf Blight (BLB)", use_container_width=True)
    st.write("**Bacterial Leaf Blight (BLB)**, yang disebabkan oleh bakteri Xanthomonas oryzae pv. oryzae, adalah salah satu penyakit daun padi yang dapat menyebabkan kerugian besar pada tanaman. Gejala pertama biasanya muncul sebagai bercak air yang membesar, berwarna kekuningan atau putih di sepanjang tepi daun, yang akhirnya mengering dan mengakibatkan daun layu. Penyakit ini menyebar melalui air irigasi atau oleh angin dan dapat dengan cepat merusak tanaman, terutama pada fase vegetatif.")
    image_path = "images/BS.jpg"  # Make sure the image file is in this path
    st.image(image_path, caption="Brown Spot", use_container_width=True)
    st.write("**Brown Spot** adalah penyakit yang disebabkan oleh jamur Cochliobolus miyabeanus. Penyakit ini sering muncul pada daun padi yang terinfeksi dengan bercak-bercak kecil berwarna cokelat gelap yang memiliki batasan yang jelas. Seiring berjalannya waktu, bercak ini berkembang dan bisa menyebabkan hilangnya klorofil, sehingga mengurangi fotosintesis dan menurunkan hasil panen. Penyakit ini sering muncul pada kondisi kelembapan yang tinggi dan dapat diperburuk dengan penggunaan benih yang terinfeksi.")
    image_path = "images/LS.jpg"  # Make sure the image file is in this path
    st.image(image_path, caption="Leaf Smut", use_container_width=True)
    st.write("**Leaf Smut** disebabkan oleh jamur Entyloma oryzae, yang menyebabkan munculnya bercak-bercak kecil berwarna putih atau keperakan pada daun padi. Seiring waktu, bercak tersebut bisa berkembang menjadi bintik-bintik yang lebih besar, menyebabkan daun menjadi keriput dan mati. Penyakit ini biasanya menyerang tanaman padi pada kondisi kelembapan tinggi dan dapat menyebar melalui benih yang terinfeksi. Pengendalian penyakit ini melibatkan penggunaan benih sehat, rotasi tanaman, serta aplikasi fungisida yang sesuai.")
    st.write("Ketiga penyakit tersebut, meskipun memiliki penyebab yang berbeda, semua dapat mengurangi kualitas dan kuantitas hasil panen padi jika tidak ditangani dengan baik. Pengelolaan yang efektif melibatkan penggunaan varietas tahan penyakit, sanitasi yang baik, dan aplikasi pestisida atau fungisida sesuai kebutuhan.")  
    st.write("Untuk menentukan atau mengidentifikasi penyakit daun padi tidaklah mudah. Maka dibuatlah website ini dengan tujuan memudahkan petani dalam mengidentifikasi penyakit daun padi tersebut agar tanaman padi mendapatkan penanganan yang tepat sehingga dapat meminimalisir kegagalan panen akibat kesalahan identifikasi dan penangan penyakit pada daun padi.")

    # Use st.radio for navigation
    #page = st.radio("Pilih Halaman", options=["Klasifikasi Penyakit"])

    #if page == "Klasifikasi Penyakit":
     #   cnn_calculation()

# CNN Classification Page
# Halaman Pehitungan CNN
def cnn_calculation():
    st.title("Klasifikasi Penyakit")
    # Upload gambar dan lakukan prediksi
    uploaded_image = st.file_uploader("Upload gambar daun", type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        st.image(img, caption='Gambar yang diunggah', use_container_width=True)

        # Preprocess dan prediksi
        image_array = preprocess_image(img)
        predictions = model.predict(image_array)

        # Display probabilitas
        st.write("Probabilitas per kelas:")
        for label in class_info:
            index = list(class_info.keys()).index(label)
            st.write(f"{label}: {predictions[0][index]:.4f}")

        # Tentukan hasil prediksi
        predicted_class = np.argmax(predictions, axis=1)
        predicted_label = list(class_info.keys())[predicted_class[0]]

        # Tampilkan hasil prediksi, pengertian, solusi, dan gambar referensi
        display_prediction(predicted_label)


# About Page
def about_page():
    st.title("About")
    
    # Display creator info
    st.write("### Pembuat Website")
    st.write("Nama: [Dina Shafa'ul Lathifah]")  # Replace with the actual name
    st.write("Deskripsi: Website ini dibuat untuk membantu para petani dalam mendeteksi penyakit pada tanaman padi menggunakan teknologi CNN (Convolutional Neural Network).")
    
    # Social media and contact links
    st.write("### Hubungi Kami melalui Media Sosial:")
    st.markdown("[LinkedIn](https//LinkedIn.com)")
    st.markdown("[Facebook](https://facebook.com) | [Instagram](https://instagram.com) | [Twitter](https://twitter.com)")  # Replace with actual links
    
    st.write("### Email")
    st.write("Email: [email@example.com](mailto:email@example.com)")  # Replace with actual email
    
    st.write("### Terima Kasih telah mengunjungi SmartFARM!")

# Structure of the application
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# Sidebar menu for logged-in users
if st.session_state["logged_in"]:
    with st.sidebar:
        selected = st.radio("Menu", ["Home", "Klasifikasi", "About", "Profile", "Logout"])

    if selected == "Home":
        home_page()
    elif selected == "Klasifikasi":
        cnn_calculation()
    elif selected == "About":
        about_page()
    elif selected == "Profile":
        profile_page()
    elif selected == "Logout":
        logout()

# Sidebar menu for non-logged-in users
else:
    with st.sidebar:
        action = st.radio("Menu", options=["Login", "Create Account"])  # Add the 'options' argument

    if action == "Login":
        login()
    elif action == "Create Account":
        register()
# Sidebar menu for non-logged-in users
    else:
        with st.sidebar:
            action = st.radio("Menu", options=["Login", "Create Account"])  # Add the 'options' argument

        if action == "Login":
            login()
        elif action == "Create Account":
            register()
