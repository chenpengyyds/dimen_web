# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:47:02 2026

@author: chenpengyyds
"""

# 文件名：step2_web_app.py
import streamlit as st
import pandas as pd
import sqlite3

# 1. 网页全局设置 (必须写在第一行)
st.set_page_config(page_title="材料属性检索中心", page_icon="🏭", layout="wide")

# 2. 网页大标题
st.title("🏭 厂长专属：一维/二维王牌材料检索大本营")
st.markdown("欢迎来到数字孪生材料工厂！在这里，您可以毫秒级查询 SQLite 数据库中的极品材料。")

# 3. 左侧边栏：检索控制台
st.sidebar.header("🔍 精准筛选引擎")
search_formula = st.sidebar.text_input("🎯 搜索化学式 (如 MoS2，留空则看全部):", "")
selected_dim = st.sidebar.selectbox("📐 选择晶体维度:", ["全部", "1D", "2D", "3D", "Molecular_or_Other"])
max_energy = st.sidebar.slider("⚡ 允许的最高形成能 (eV/atom):", -5.0, 0.5, 0.1, step=0.05)

# 4. 核心大脑：拼接 SQL 查询语句
# 注意：因为表头带有空格和括号，SQL 里必须用反引号 ` 包起来
query = "SELECT * FROM Materials WHERE `形成能 (eV/atom)` <= ?"
params = [max_energy]

# 如果厂长输入了化学式，就加上模糊匹配的条件
if search_formula:
    query += " AND `化学式` LIKE ?"
    params.append(f"%{search_formula}%")

# 如果厂长指定了维度，就加上维度条件
if selected_dim != "全部":
    query += " AND `维度` = ?"
    params.append(selected_dim)

# 5. 瞬间连接数据库并执行查询
conn = sqlite3.connect("materials_web.db")
df_results = pd.read_sql_query(query, conn, params=params)
conn.close()

# 6. 将结果展示在网页中央
st.success(f"✅ 检索完成！数据库引擎在 0.01 秒内为您锁定了 **{len(df_results)}** 个符合条件的王牌材料。")

# 用极其美观的交互式表格展示出来
st.dataframe(df_results, use_container_width=True, height=600)