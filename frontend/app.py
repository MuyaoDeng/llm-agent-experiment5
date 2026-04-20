"""
前端界面 - Streamlit应用
"""
import streamlit as st
import requests
import json
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title=" 基于云端API的Agent",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e3f2fd 100%);
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #1565C0 ;
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1E88E5 0%, #1565C0 100%);
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: white !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(21, 101, 192, 0.3);
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: white;
        border: 2px solid #1E88E5;
        border-radius: 8px;
        color: #333333;
    }
    
    /* 容器样式 */
    .css-1d391kg .stSelectbox, .css-1d391kg .stSlider {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px;
    }
    
    /* 成功提示 */
    .stSuccess {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* 错误提示 */
    .stError {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        color: white;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* 警告提示 */
    .stWarning {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* 信息提示 */
    .stInfo {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* Metric样式 */
    [data-testid="stMetricValue"] {
        color: #1565C0 !important;
        font-size: 2rem;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-size: 1rem;
    }
    
    /* Expander样式 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 8px;
        color: #1565C0;
    }
    
    /* 分割线 */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1E88E5, transparent);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = "http://localhost:8000"
if 'llm_api_key' not in st.session_state:
    st.session_state.llm_api_key = ""
if 'llm_base_url' not in st.session_state:
    st.session_state.llm_base_url = "https://api.deepseek.com/v1"
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = "deepseek-chat"

# 标题区域
st.markdown("""
<div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
            padding: 30px; border-radius: 15px; margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3);">
    <h1 style="color:rgba(255, 255, 255, 0.9); margin: 0; text-align: center; font-size: 2.5rem;">
        基于云端API的Agent智能体系统
    </h1>
    <p style="color: rgba(255, 255, 255, 0.9); margin: 10px 0 0 0; text-align: center; font-size: 1.1rem;">
        具备自主思考与工具调用能力
    </p>
</div>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 后端API地址配置
    backend_url = st.text_input(
        "后端服务地址",
        value=st.session_state.backend_url,
        placeholder="http://localhost:8000",
        help="后端FastAPI服务的URL地址"
    )
    
    if backend_url != st.session_state.backend_url:
        st.session_state.backend_url = backend_url
    
    st.divider()
    
    # LLM配置
    st.subheader("🤖 LLM配置")
    
    llm_api_key = st.text_input(
        "API Key",
        value=st.session_state.llm_api_key,
        type="password",
        placeholder="sk-your-api-key-here",
        help="LLM服务的API密钥"
    )
    
    llm_base_url = st.text_input(
        "API Base URL",
        value=st.session_state.llm_base_url,
        placeholder="https://api.deepseek.com/v1",
        help="LLM API的基础URL"
    )
    
    llm_model = st.text_input(
        "模型名称",
        value=st.session_state.llm_model,
        placeholder="deepseek-chat",
        help="使用的模型名称"
    )
    
    # 更新session state
    if llm_api_key != st.session_state.llm_api_key:
        st.session_state.llm_api_key = llm_api_key
    if llm_base_url != st.session_state.llm_base_url:
        st.session_state.llm_base_url = llm_base_url
    if llm_model != st.session_state.llm_model:
        st.session_state.llm_model = llm_model
    
    st.divider()
    
    # 高级选项
    st.header("⚙️ 高级选项")
    
    # 初始化max_iterations会话状态
    if 'max_iterations' not in st.session_state:
        st.session_state.max_iterations = 10
    
    max_iterations = st.slider(
        "最大迭代次数", 
        1, 20, 
        value=st.session_state.max_iterations,
        help="智能体执行的最大迭代次数"
    )
    
    # 更新会话状态
    st.session_state.max_iterations = max_iterations

# 主界面
st.markdown("""
<div style="background: white; padding: 6px 25px; border-radius: 15px; margin-bottom: 10px;
            box-shadow: 0 2px 10px rgba(21, 101, 192, 0.1);">
    <h2 style="color: #1565C0; margin: 0; font-size: 1.4rem;">💬 查询输入</h2>
""", unsafe_allow_html=True)

# 查询输入区域
query = st.text_area(
    "",
    placeholder="请输入您的研究需求，例如：帮我调研2026年关于DPO算法的最新进展",
    height=180,
    key="query_input",
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

# 提交按钮
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 开始调研", type="primary", use_container_width=True):
        # 后面你原来的按钮逻辑全部不动，完全保留
        if not query.strip():
            st.warning("请输入查询内容")
        elif not st.session_state.llm_api_key:
            st.warning("请在侧边栏填入API Key")
        else:
            # 后续原有逻辑全部不变
            status_placeholder = st.empty()
            result_placeholder = st.empty()
            log_placeholder = st.empty()
            
            status_placeholder.info("🔄 正在处理您的请求...")
            
            try:
                response = requests.post(
                    f"{st.session_state.backend_url}/query",
                    json={
                        "query": query,
                        "max_iterations": st.session_state.max_iterations,
                        "llm_config": {
                            "api_key": st.session_state.llm_api_key,
                            "base_url": st.session_state.llm_base_url,
                            "model": st.session_state.llm_model
                        }
                    },
                    timeout=300
                )
                # 后面你原本的接口请求、结果渲染、日志展示代码全部原样保留
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["success"]:
                        status_placeholder.success("✅ 调研完成！")
                        
                        # 显示最终结果
                        with result_placeholder.container():
                            st.markdown("""
                            <div style="background: white; padding: 25px; border-radius: 15px; margin-bottom: 20px;
                                        box-shadow: 0 2px 10px rgba(21, 101, 192, 0.1);">
                                <h2 style="color: #1565C0; margin-top: 0;">📊 调研结果</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("""
                            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
                                        border: 2px solid #E3F2FD; box-shadow: 0 2px 8px rgba(21, 101, 192, 0.08);">
                            """, unsafe_allow_html=True)
                            st.markdown(data["final_response"])
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                                        padding: 15px; border-radius: 8px; color: white; text-align: center;">
                                <strong>总迭代次数: {data['iterations']}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 显示执行日志
                        with log_placeholder.container():
                            st.markdown("""
                            <div style="background: white; padding: 25px; border-radius: 15px; margin-bottom: 20px;
                                        box-shadow: 0 2px 10px rgba(21, 101, 192, 0.1);">
                                <h2 style="color: #1565C0; margin-top: 0;">📝 执行日志（思考链路追踪）</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            execution_log = data["execution_log"]
                            
                            # 摘要信息
                            st.markdown("""
                            <div style="background: #E3F2FD; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                            """, unsafe_allow_html=True)
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("总步骤数", execution_log["total_steps"])
                            with col2:
                                st.metric("总耗时", f"{execution_log['total_time']:.2f}秒")
                            with col3:
                                st.metric("开始时间", execution_log["start_time"].split("T")[1][:8])
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            st.markdown("""
                            <div style="height: 2px; background: linear-gradient(90deg, transparent, #1E88E5, transparent);
                                        margin: 20px 0;"></div>
                            """, unsafe_allow_html=True)
                            
                            # 详细步骤
                            for step in execution_log["steps"]:
                                step_type = step["type"]
                                
                                # 根据步骤类型选择图标和颜色
                                if step_type == "user_query":
                                    icon = "💬"
                                    color = "blue"
                                elif step_type == "llm_thinking":
                                    icon = "🤔"
                                    color = "orange"
                                elif step_type == "llm_response":
                                    icon = "💡"
                                    color = "green"
                                elif step_type == "tool_call":
                                    icon = "🔧"
                                    color = "violet"
                                elif step_type == "tool_result":
                                    icon = "✅"
                                    color = "green"
                                elif step_type == "completion":
                                    icon = "🎉"
                                    color = "rainbow"
                                elif step_type == "error":
                                    icon = "❌"
                                    color = "red"
                                else:
                                    icon = "📌"
                                    color = "gray"
                                
                                with st.expander(
                                    f"{icon} 步骤 {step['step_number']}: {step['description']} "
                                    f"({step['execution_time']:.2f}秒)",
                                    expanded=(step_type in ["user_query", "completion", "error"])
                                ):
                                    st.write(f"**时间:** {step['timestamp']}")
                                    st.write(f"**类型:** {step_type}")
                                    
                                    # 显示详细信息
                                    if step["details"]:
                                        st.json(step["details"])
                    else:
                        status_placeholder.error("❌ 调研失败")
                        st.error(data.get("error", "未知错误"))
                        
                        if "execution_log" in data:
                            with log_placeholder.container():
                                st.header("📝 执行日志")
                                st.json(data["execution_log"])
                else:
                    status_placeholder.error(f"❌ 请求失败: HTTP {response.status_code}")
                    st.error(response.text)
                    
            except requests.exceptions.Timeout:
                status_placeholder.error("❌ 请求超时")
                st.error("请求处理时间过长，请稍后重试")
            except Exception as e:
                status_placeholder.error("❌ 发生错误")
                st.error(f"错误信息: {str(e)}")

# 页脚
st.markdown("""
<div style="height: 2px; background: linear-gradient(90deg, transparent, #1E88E5, transparent);
            margin: 30px 0;"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: white; padding: 25px; border-radius: 15px; margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(21, 101, 192, 0.1);">
    <h2 style="color: #1565C0; margin-top: 0;">📖 使用说明</h2>
    <div style="color: #333333; line-height: 1.8;">
        <p><strong>1. 输入查询:</strong> 在文本框中输入您的研究需求</p>
        <p><strong>2. 开始调研:</strong> 点击"开始调研"按钮</p>
        <p><strong>3. 查看结果:</strong> 系统将自动规划步骤、调用工具并生成报告</p>
        <p><strong>4. 追踪过程:</strong> 在执行日志中查看完整的思考链路</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
            padding: 20px; border-radius: 10px; text-align: center; color: white; margin-top: 30px;
            box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3);">
    <p style="margin: 0; font-size: 1.1rem;">本系统由AI智能体驱动，支持自主思考与工具调用</p>
</div>
""", unsafe_allow_html=True)