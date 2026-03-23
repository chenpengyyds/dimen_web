# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:47:02 2026

@author: chenpengyyds
"""

# 文件名：step2_web_app.py
import streamlit as st
import pandas as pd
import sqlite3

# --- 1. 极速缓存连接 ---
@st.cache_resource
def init_connection():
    return sqlite3.connect("materials_web.db", check_same_thread=False)

conn = init_connection()

# --- 2. 网页 UI 设置 ---
st.title("🔬 极速版：高通量材料属性检索系统")

# --- 3. 侧边栏筛选 ---
with st.sidebar:
    st.header("🔍 筛选条件")
    formula = st.text_input("化学式:", "")
    energy_cutoff = st.slider("最高形成能:", -5.0, 0.5, 0.0)
    # 增加一个控制显示数量的滑块
    row_limit = st.select_slider("显示条数:", options=[100, 500, 1000], value=500)

# --- 4. 智能 SQL 查询 (核心：让数据库干活，不让浏览器干活) ---
query = "SELECT * FROM Materials WHERE `形成能 (eV/atom)` <= ?"
params = [energy_cutoff]

if formula:
    query += " AND `化学式` LIKE ?"
    params.append(f"%{formula}%")

# 关键点：一定要加 LIMIT！
query += f" LIMIT {row_limit}"

# 执行查询
df = pd.read_sql_query(query, conn, params=params)

# --- 5. 结果展示 ---
if not df.empty:
    st.success(f"⚡ 检索完成！已展示最匹配的前 {len(df)} 条数据。")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("🏮 未找到符合条件的材料。")