# streamlit_app.py
import streamlit as st
import math

st.set_page_config(page_title="REC 정책 파라미터 엔진", layout="wide")
st.title("REC 정책 파라미터 엔진 (초안)")

with st.sidebar:
    st.header("① 수요(의무량) 파라미터")
    base_gen_gwh = st.number_input("기준발전량(GWh)", min_value=0.0, value=630000.0, step=1000.0)
    oblig_rate = st.number_input("의무비율(%)", min_value=0.0, max_value=30.0, value=13.5, step=0.1)
    avg_weight = st.number_input("평균 가중치(의무량→REC 환산)", min_value=0.5, max_value=2.5, value=1.0, step=0.05)
    re100_extra_rec = st.number_input("RE100 추가수요(REC)", min_value=0.0, value=0.0, step=10000.0)

    st.header("② 공급(발급량) 파라미터")
    st.caption("단위: REC = MWh (가중치 반영 후)")
    rec_solar = st.number_input("태양광 발급량(REC)", min_value=0.0, value=37612000.0, step=10000.0)
    rec_wind = st.number_input("풍력 발급량(REC)", min_value=0.0, value=3250000.0, step=10000.0)
    rec_bio = st.number_input("바이오 발급량(REC)", min_value=0.0, value=15188000.0, step=10000.0)
    rec_fuelcell = st.number_input("연료전지 발급량(REC)", min_value=0.0, value=11207000.0, step=10000.0)
    rec_others = st.number_input("기타 발급(수력/폐기물 등)", min_value=0.0, value=12400000.0, step=10000.0)

    st.header("③ 가격·계약 파라미터")
    rec_price_ref = st.number_input("현물 기준가격(원/kWh)", min_value=0.0, value=69.8, step=1.0)
    smp = st.number_input("SMP(원/kWh)", min_value=0.0, value=114.7, step=1.0)
    fixed_price = st.number_input("고정가격계약 단가(원/kWh)", min_value=0.0, value=151.0, step=1.0)
    cfd_strike = st.number_input("CfD 행사가격(원/kWh)", min_value=0.0, value=151.0, step=1.0)
    price_elasticity = st.slider("현물가격 수급탄성(단순)", 0.1, 2.0, 0.6, 0.1)

# 1) 수요(의무량) -> REC 환산
# 의무량(GWh) = 기준발전량 * 의무비율
# 의무 REC ≈ 의무량(GWh) * 1,000 / 평균가중치
obligation_gwh = base_gen_gwh * (oblig_rate / 100)
demand_rec = (obligation_gwh * 1000.0) / max(avg_weight, 1e-6)
demand_total_rec = demand_rec + re100_extra_rec

# 2) 공급(발급량)
supply_rec = rec_solar + rec_wind + rec_bio + rec_fuelcell + rec_others

# 3) 수급지수 및 현물가격 추정(아주 단순한 형태)
supply_demand_ratio = (demand_total_rec / max(supply_rec, 1e-6))
# 가격 = 기준가격 * (수급지수 ** 탄성)
rec_spot_est = rec_price_ref * (supply_demand_ratio ** price_elasticity)

# 4) 발전사업자 수익 비교 (kWh당)
rev_spot = smp + rec_spot_est
rev_fixed = fixed_price
rev_cfd = cfd_strike + (smp - cfd_strike)  # 양방향 CfD 정산 후 기대수익은 SMP에 수렴(단, 음가격/캡 등 실제 규칙 반영 필요)

# 출력
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("수요·공급(REC)")
    st.metric("의무+RE100 수요", f"{demand_total_rec:,.0f} REC")
    st.metric("공급(발급)", f"{supply_rec:,.0f} REC")
    st.metric("수급지수(수요/공급)", f"{supply_demand_ratio:,.2f}")

with col2:
    st.subheader("현물가격 추정")
    st.metric("현물 기준가격", f"{rec_price_ref:,.1f} 원/kWh")
    st.metric("현물 추정가격", f"{rec_spot_est:,.1f} 원/kWh")

with col3:
    st.subheader("kWh당 발전사업자 수익")
    st.metric("현물(SMP+REC)", f"{rev_spot:,.1f} 원/kWh")
    st.metric("고정가격", f"{rev_fixed:,.1f} 원/kWh")
    st.metric("CfD(개념적)", f"{rev_cfd:,.1f} 원/kWh")

st.info("주의: 실제 정산(별표4), 탄소검증 우대, 변동형 가중치, 시간대별 캡처가격, 의무연기·과징금 등은 단순화되어 있으며, 실무 도입 시 별도 모듈로 확장해야 합니다.")
