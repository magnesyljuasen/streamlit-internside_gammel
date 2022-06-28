import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['asidjghiasdgjij', '456']).generate()
print(hashed_passwords)

    