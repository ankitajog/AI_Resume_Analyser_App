
import streamlit as st # type: ignore
import nltk # type: ignore
import spacy # type: ignore
nltk.download('stopwords')
custom_nlp = spacy.load('en_core_web_sm')

import pandas as pd # type: ignore
import base64, random
import time, datetime
from pyresparser import ResumeParser # type: ignore
from pdfminer.high_level import extract_text # type: ignore
import io, random
from streamlit_tags import st_tags # type: ignore
from PIL import Image # type: ignore
import pymysql # type: ignore
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
from Courses import network_course, database_course, cloud_course, devops_course

import re
# import pafy
import pafy # type: ignore
import plotly.express as px # type: ignore
# import youtube_dl


import yt_dlp  # type: ignore

def fetch_yt_video(link):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title')
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None

def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    text = extract_text(file)
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

#-----Email validation-----#
def is_valid_email(email):
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

connection = pymysql.connect(host='localhost', user='root', password='A8041@abj#')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,
                courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
    name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
    courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

#----Users---#
# Insert new user into database
def register_user(name, email, password):
    try:
        insert_sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (name, email, password))
        connection.commit()
        return True
    except pymysql.err.IntegrityError:
        return False  # email already exists

# Validate login
def validate_user(email, password):
    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    return cursor.fetchone()  # returns row if exists

#-----------#
# ---------- CONTACT TABLE ----------#
def create_contact_table():
    contact_sql = """
    CREATE TABLE IF NOT EXISTS contact (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        message TEXT NOT NULL,
        timestamp VARCHAR(50) NOT NULL,
        PRIMARY KEY (id)
    );
    """
    cursor.execute(contact_sql)
    connection.commit()

def insert_contact(name, email, message):
    ts = time.time()
    cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    timestamp = str(cur_date + '_' + cur_time)

    insert_sql = "INSERT INTO contact (name, email, message, timestamp) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_sql, (name, email, message, timestamp))
    connection.commit()

#--------------------------------#
# ---------- ADMIN TABLE ----------
def create_admin_table():
    admin_sql = """
    CREATE TABLE IF NOT EXISTS admins (
        id INT NOT NULL AUTO_INCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        PRIMARY KEY (id)
    );
    """
    cursor.execute(admin_sql)
    connection.commit()

def validate_admin(username, password):
    # hardcoded admin OR fetch from DB if needed
    if username == "machine_learning_hub" and password == "mlhub123":
        return {"id": 1, "username": username}
    return None

    
#-------------------------------#
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon='./Logo/ai_image.jpeg',
)


def run():
    st.title("AI Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin","Contact"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    # link = '[©Developed by Spidy20](http://github.com/spidy20)'
    # st.sidebar.markdown(link, unsafe_allow_html=True)
    img = Image.open('./Logo/ai_image.jpeg')
    img = img.resize((300,300))
    st.image(img)

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)
    connection.select_db("sra")

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(300) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)

    # Create users table for sign-in/sign-up
    users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        PRIMARY KEY (id)
    );  
"""
    cursor.execute(users_table_sql)
    connection.commit()
#-----------------------------#
    create_admin_table()
#-------------------------------#
    
    if choice == 'Normal User':
        st.subheader("🔐 Normal User Portal")

        # Initialize session state
        if "user_logged_in" not in st.session_state:
            st.session_state.user_logged_in = False
            st.session_state.current_user = None

        menu = ["Sign In", "Sign Up"]
        user_choice = st.radio("Select Option:", menu)

        
        # ---------- SIGN UP ----------
        if user_choice == "Sign Up":
            st.subheader("📝 Create a New Account")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")

            if st.button("Register"):
                if not is_valid_email(new_email):
                    st.error("⚠ Invalid Email! Please enter a valid email address (e.g., user@example.com).")
                elif not new_name or not new_password:
                    st.error("⚠ Please fill all fields.")
                else:
                    if register_user(new_name, new_email, new_password):
                        st.success("✅ Registration Successful! Please Sign In.")
                    else:
                        st.error("⚠ Email already exists. Try another.")


    # ---------- SIGN IN ----------
        elif user_choice == "Sign In":
            if not st.session_state.user_logged_in:
                st.subheader("🔑 Sign In to your Account")
                email_input = st.text_input("Email")
                password_input = st.text_input("Password", type="password")

                if st.button("Sign In"):
                    user = validate_user(email_input, password_input)
                    if user:
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = user
                        st.success(f"✅ Welcome {user[1]}!")  # user[1] = name
                    else:
                        st.error("❌ Invalid Email or Password")
            else:
                user = st.session_state.current_user
                st.success(f"Signed in as: {user[1]} ({user[2]})")

                # Logout
                if st.button("Logout"):
                    st.session_state.user_logged_in = False
                    st.session_state.current_user = None
                    st.success("You have been logged out.")   

    
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume....'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)
                #-------------------------------------------------------#
                # --- ATS Compatibility Check ---#
                st.subheader("ATS Compatibility Check 🔍")
                issues = []

                # Check for tables or images (basic detection in PDF text)
                if "Table" in resume_text or "table" in resume_text:
                    issues.append("Tables detected – ATS may not parse table content properly.")

                # Check for uncommon fonts or symbols (using special characters)
                if any(char in resume_text for char in ["•", "★", "→", "✓", "✔", "✦"]):
                    issues.append("Special symbols detected – replace with plain text or bullet points.")

                # Check for columns/pages formatting
                if resume_data['no_of_pages'] > 2:
                    issues.append("Resume is longer than 2 pages – shorter resumes are more ATS friendly.")

                # Check for images or graphics keywords
                if any(word in resume_text.lower() for word in ["image", "graphic", "photo", "diagram"]):
                    issues.append("Graphics detected – ATS cannot read images or diagrams.")

                # Final Output
                if issues:
                    for issue in issues:
                        st.warning(issue)
                    st.info("⚠ Consider simplifying your resume for better ATS parsing.")
                else:
                    st.success("✅ Your resume looks ATS-friendly!")

                #---------------------------------------#

                st.header("Resume Analysis")
                st.success("Hello! , " + resume_data['name'])
                st.subheader("Your Basic info")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)

                st.subheader("Skills Recommendation💡")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')
                skills = resume_data.get('skills', [])
                if not skills:
                    skills = ["No skills found. Please check resume format."]
                    keywords = st_tags(label='### Skills that you have',
                    text='See our skills recommendation',
                    value=skills, key='1')


                ##  recommendation
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit','ETL','Data Mining', 'Data Analysis','Machine Learning','Python',
                                'R', 'MATLAB'
                            ]
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'cocoa', 'cocoa touch', 'xcode',
                                'Swift',]
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']
                network_keywords = ['network', 'cisco', 'router', 'switching', 'firewall', 'tcp/ip', 'lan', 'wan',
                                    'vpn', 'juniper', 'dns']
                database_keywords = ['sql', 'mysql', 'oracle', 'postgresql', 'mongodb', 'database', 'schema', 'query',
                                    'normalization', 'stored procedures', 'pl/sql']
                cloud_keywords = ['aws', 'azure', 'gcp', 'cloud', 'ec2', 's3', 'lambda', 'cloudformation', 'terraform',
                                  'kubernetes']
                devops_keywords = ['jenkins', 'docker', 'kubernetes', 'ci/cd', 'ansible', 'chef', 'puppet', 'gitlab',
                                   'github actions', 'monitoring', 'grafana']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success(" Our analysis says you are looking for Data Science Jobs.")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='2')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success(" Our analysis says you are looking for Web Development Jobs ")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='3')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success(" Our analysis says you are looking for Android App Development Jobs ")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='4')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success(" Our analysis says you are looking for IOS App Development Jobs ")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='5')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success(" Our analysis says you are looking for UI-UX Development Jobs ")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='6')# <--- Different key for a different widget
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break
                    # Add below existing UI/UX section
                    elif i.lower() in network_keywords:
                        reco_field = 'Network Engineer'
                        st.success("Our analysis says you are looking for Network Engineering Jobs")
                        recommended_skills = ['Cisco', 'Routing', 'Switching', 'TCP/IP', 'LAN/WAN', 'VPN', 'Firewall', 'Network Security']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                   text='Recommended skills generated from System',
                                   value=recommended_skills, key='7')
                        st.markdown(
        '''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
        unsafe_allow_html=True)
                        rec_course = course_recommender(network_course)
                        break

                    elif i.lower() in database_keywords:
                        reco_field = 'Database Engineer'
                        st.success("**Our analysis says you are looking for Database Engineering Jobs**")
                        recommended_skills = ['SQL', 'Oracle', 'Database Design', 'Stored Procedures', 'PL/SQL', 'Normalization']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                   text='Recommended skills generated from System',
                                   value=recommended_skills, key='8')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                        rec_course = course_recommender(database_course)
                        break

                    elif i.lower() in cloud_keywords:
                        reco_field = 'Cloud Engineer'
                        st.success("**Our analysis says you are looking for Cloud Engineering Jobs**")
                        recommended_skills = ['AWS', 'Azure', 'GCP', 'Terraform', 'CloudFormation', 'Lambda', 'EC2', 'S3']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                   text='Recommended skills generated from System',
                                   value=recommended_skills, key='9')
                        st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                        rec_course = course_recommender(cloud_course)
                        break

                    elif i.lower() in devops_keywords:
                        reco_field = 'DevOps Engineer'
                        st.success("**Our analysis says you are looking for DevOps Jobs**")
                        recommended_skills = ['Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'GitLab', 'Ansible', 'Monitoring']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                   text='Recommended skills generated from System',
                                   value=recommended_skills, key='10')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                        rec_course = course_recommender(devops_course)
                        break

                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                ### Resume writing recommendation
                st.subheader("Resume Tips & Ideas💡")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍/h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html=True)

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success(' Your Resume Writing Score: ' + str(score) + '')
                st.warning(
                    "Note: This score is calculated based on the content that you have added in your Resume.")
                st.balloons()

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                            str(recommended_skills), str(rec_course))

                ## Resume writing video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                res_vid_title = fetch_yt_video(resume_vid)
                #st.subheader("✅ **" + res_vid_title + "**")
                #"✅ **" + None + "**"
                if res_vid_title is not None:
                    st.subheader("✅ " + res_vid_title + "")
                else:
                    st.subheader("✅ No Title Available")

                st.video(resume_vid)

                ## Interview Preparation Video
                st.header("**Bonus Video for Interview👨‍💼 Tips💡**")
                interview_vid = random.choice(interview_videos)
                int_vid_title = fetch_yt_video(interview_vid)
                #st.subheader("✅ " + int_vid_title + "")
                st.subheader("✅ " + (int_vid_title or "No title available") + "")

                st.video(interview_vid)

                connection.commit()
            else:
                st.error('Something went wrong..')

#-----------------------------------------------------------------#               
    elif choice == "Admin":
        st.subheader("🔐 Admin Login")

        # Initialize admin session
        if "admin_logged_in" not in st.session_state:
            st.session_state.admin_logged_in = False

        # Login form
        if not st.session_state.admin_logged_in:
            ad_user = st.text_input("Username")
            ad_password = st.text_input("Password", type="password")

            if st.button("Login"):
                if ad_user == "machine_learning_hub" and ad_password == "mlhub123":
                    st.session_state.admin_logged_in = True
                    st.success("✅ Welcome Admin!")
                else:
                    st.error("❌ Wrong Username or Password")

        # Dashboard (only if logged in)
        if st.session_state.admin_logged_in:
            try:
                # Load all user data
                df = pd.read_sql("SELECT * FROM user_data", connection)

                if not df.empty:
                    st.header("**User's👨‍💻 Data**")
                    st.dataframe(df)

                    # Download link
                    st.markdown(
                        get_table_download_link(df, 'User_Data.csv', '📥 Download Report'),
                        unsafe_allow_html=True
                    )

                    # 📊 Predicted Field Chart
                    if "Predicted_Field" in df.columns:
                        field_counts = df["Predicted_Field"].value_counts()
                        st.subheader("📊 Predicted Field Distribution")
                        fig1 = px.pie(
                            values=field_counts.values,
                            names=field_counts.index,
                            title="Predicted Field according to the Skills"
                        )
                        st.plotly_chart(fig1)

                    # 📊 User Level Chart
                    if "User_level" in df.columns:
                        level_counts = df["User_level"].value_counts()
                        st.subheader("📊 User Experience Levels")
                        fig2 = px.pie(
                            values=level_counts.values,
                            names=level_counts.index,
                            title="User's Experience Level"
                        )
                        st.plotly_chart(fig2)
                else:
                    st.info("ℹ No user data available yet.")

            except Exception as e:
                st.error(f"⚠ Could not load data: {e}")

            # Logout
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.success("You have been logged out.")   
            
            
    elif choice == "Contact":
        st.subheader("📩 Contact Us")
        create_contact_table()

        with st.form(key='contact_form'):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Your Message")

            submit_button = st.form_submit_button("Send Message")

            if submit_button:
                if name and email and message:
                    insert_contact(name, email, message)
                    st.success("✅ Your message has been sent successfully!")
                else:
                    st.error("⚠ Please fill all fields before submitting.")

run()




