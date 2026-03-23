# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:47:02 2026

@author: chenpengyyds
"""

# 文件名：step2_web_app.py
import streamlit as st
import pandas as pd
import sqlite3

# 1. 宽屏模式
st.set_page_config(page_title="材料极速检索", layout="wide")

# 2. 数据库超频连接（保持不变）
@st.cache_resource
def get_connection():
    conn = sqlite3.connect("materials_web.db", check_same_thread=False)
    conn.execute("PRAGMA cache_size = 10000")
    conn.execute("PRAGMA temp_store = MEMORY") # 💡 临时数据存在内存，极速
    return conn

# 3. 带缓存的查询（保持不变）
@st.cache_data(show_spinner=False)
def fetch_data(query_sql, params):
    conn = get_connection()
    return pd.read_sql_query(query_sql, conn, params=params)

# --- 主界面 ---
st.markdown("# 🔬 低维材料属性检索系统")

# 4. 核心：首屏空载逻辑
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        search_keyword = st.text_input("请输入化学式或元素进行检索 (例如: MoS2 或 MgO)", "").strip()
    with c2:
        energy_slider = st.slider("最高形成能:", -5.0, 0.5, 0.0)

# --- 💡 关键改动：只有输入了关键词才开始跑数据库 ---
if not search_keyword:
    st.info("💡 请在上方输入化学式，点击回车即可瞬间调取 13.5 万行数据。")
    # 这里放一张你觉得好看的背景图，或者简单的系统介绍，避免空白
    st.stop() # 停止运行后面的数据库查询代码

# --- 以下代码只有在输入 search_keyword 后才会执行 ---

# 拼接查询条件
base_where = "WHERE `化学式` LIKE ? AND `形成能 (eV/atom)` <= ?"
params = [f"%{search_keyword}%", energy_cutoff]

# 5. 秒级获取总数
total_rows = fetch_data(f"SELECT COUNT(*) FROM Materials {base_where}", params).iloc[0, 0]

# 6. 分页（每页30条）
items_per_page = 30
if 'page' not in st.session_state: st.session_state.page = 1

offset = (st.session_state.page - 1) * items_per_page
query_data = f"SELECT * FROM Materials {base_where} LIMIT {items_per_page} OFFSET {offset}"
df = fetch_data(query_data, params)

if not df.empty:
    st.success(f"✅ 找到 {total_rows} 个匹配材料")
    st.dataframe(df, use_container_width=True, height=600)
    
    # 翻页按钮（简易版）
    col1, col2 = st.columns([1, 1])
    if st.session_state.page > 1:
        if col1.button("⬅️ 上一页"):
            st.session_state.page -= 1
            st.rerun()
    if len(df) == items_per_page:
        if col2.button("下一页 ➡️"):
            st.session_state.page += 1
            st.rerun()