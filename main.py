import streamlit as st, requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="MC Servers", page_icon="🧭")
URL, HEADERS = "https://minecraft-mp.com/servers/list/{}/", {"User-Agent":"Mozilla/5.0"}

def fetch(p):
    try:
        html = requests.get(URL.format(p), headers=HEADERS, timeout=10).content
        soup = BeautifulSoup(html, "html.parser")
        body = soup.select_one("table.table.table-bordered tbody")
        rows = body.find_all("tr") if body else []
        data = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells)<3: continue
            parts = cells[1].text.strip().split("\n")
            player_text = cells[2].text.strip()
            players = 0
            try:
                players = int(player_text.split("/")[0])
            except ValueError:
                players = 0
            data.append({
                "Name": parts[0].strip(),
                "IP": parts[-1].strip(),
                "Ver": next((x for x in parts if "1." in x), "-"),
                "Players": players,
                "Tags": cells[4].text.strip() if len(cells) > 4 else "-"
            })
        return data
    except Exception as e:
        st.error(e)
        return []

def app():
    st.title("MC Servers")
    st.session_state.setdefault("page", 1)
    mn = st.slider("Min Players", 0, 1000, 0)
    mx = st.slider("Max Players", 0, 1000, 1000)
    c1, c2, _ = st.columns([0.1, 0.1, 1.5])
    if c1.button("←", disabled=st.session_state.page < 2):
        st.session_state.page -= 1
        st.rerun()
    if c2.button("→"):
        st.session_state.page += 1
        st.rerun()
    servers = [s for s in fetch(st.session_state.page) if mn <= s["Players"] <= mx]
    st.text(f"Page: {st.session_state.page} | Players: {mn}-{mx}")
    if servers:
        df = pd.DataFrame(servers)
        st.dataframe(df)
        st.download_button("Save", df.to_csv(index=False), f"page-{st.session_state.page}.csv")
    else:
        st.info("No servers found.")

if __name__ == "__main__":
    app()