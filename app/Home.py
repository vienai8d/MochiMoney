import streamlit as st


def main():
    st.set_page_config(page_title="Home", page_icon="./assets/icon/mochi_icon_512.png", layout="centered")
    st.title("MochiMoney")
    st.image("./assets/icon/mochi_icon_512.png")


if __name__ == "__main__":
    main()
