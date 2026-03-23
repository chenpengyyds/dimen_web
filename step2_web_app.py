# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:47:02 2026

@author: chenpengyyds
"""

# 文件名：step2_web_app.py
import streamlit as st
import pandas as pd
import sqlite3

# 【必须放在第一行】开启宽屏模式
st.set_page_config(page_title="低维材料数据库", layout="wide")

@st.cache_resource
def init_conn():
    return sqlite3.connect("materials_web.db", check_same_thread=False)

conn = init_conn()

# --- 侧边栏：筛选控制 ---
with st.sidebar:
    st.title("🔍 筛选中心")
    formula = st.text_input("元素/化学式 (如 MgO):", "")
    energy_cutoff = st.slider("最高形成能 (eV/atom):", -5.0, 0.5, 0.0)
    st.divider()
    st.info("提示：点击表格标题可排序")

# --- 主界面：头部 ---
st.markdown("# 🔬 第一性原理低维材料属性平台")
st.caption("基于 Materials Project 高通量计算数据")

# --- 核心查询逻辑 ---
base_query = "FROM Materials WHERE `形成能 (eV/atom)` <= ?"
params = [energy_cutoff]
if formula:
    base_query += " AND `化学式` LIKE ?"
    params.append(f"%{formula}%")

# 计算总数
total_rows = pd.read_sql_query(f"SELECT COUNT(*) {base_query}", conn, params=params).iloc[0,0]

# 分页处理
items_per_page = 30
total_pages = (total_rows // items_per_page) + 1
if 'page' not in st.session_state: st.session_state.page = 1

# 查询当前页数据
offset = (st.session_state.page - 1) * items_per_page
final_query = f"SELECT * {base_query} LIMIT {items_per_page} OFFSET {offset}"
df = pd.read_sql_query(final_query, conn, params=params)

# --- 数据展示区 ---
if not df.empty:
    # 顶部数据概览
    c1, c2, c3 = st.columns(3)
    c1.metric("匹配材料总数", total_rows)
    c2.metric("当前页平均带隙", f"{df['能带 (eV)'].mean():.2f} eV")
    c3.metric("当前页平均形成能", f"{df['形成能 (eV/atom)'].mean():.2f}")

    # 大表格展示 (use_container_width 让它变宽)
    st.dataframe(df, use_container_width=True, height=550)

    # 翻页控制栏
    p1, p2, p3 = st.columns([1,2,1])
    with p1:
        if st.button("⬅️ 上一页") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()
    with p2:
        st.write(f"第 **{st.session_state.page}** 页 / 共 {total_pages} 页")
    with p3:
        if st.button("下一页 ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()
else:
    st.error("❌ 未找到符合条件的材料，请调整筛选范围。")